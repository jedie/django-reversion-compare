# coding: utf-8

"""
    admin
    ~~~~~
    
    Admin extensions for django-reversion-compare

    :copyleft: 2012 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from functools import partial

from django import template
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.admin import helpers, options
from django.contrib.admin.util import unquote, quote
from django.contrib.contenttypes.generic import GenericInlineModelAdmin, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models, transaction, connection
from django.forms.formsets import all_valid
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.dateformat import format
from django.utils.encoding import force_unicode
from django.utils.html import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext as _

from reversion.forms import SelectDiffForm
from reversion.helpers import html_diff
from reversion.models import Revision, Version, has_int_pk, VERSION_ADD, VERSION_CHANGE, VERSION_DELETE
from reversion.revisions import default_revision_manager, RegistrationError



class CompareVersionAdmin(VersionAdmin):
    """
    Enhanced version of VersionAdmin with a flexible compare version API.
    
    You can define own method to compare fields in two ways (in this order):
    
        Create a method for a field via the field name, e.g.:
            "compare_%s" % field_name
            
        Create a method for every field by his internal type
            "compare_%s" % field.get_internal_type()
        
        see: https://docs.djangoproject.com/en/1.4/howto/custom-model-fields/#django.db.models.Field.get_internal_type
        
    If no method defined it would build a simple ndiff from repr().
       
    example:
    
    ----------------------------------------------------------------------------
    class MyModel(models.Model):
        date_created = models.DateTimeField(auto_now_add=True)
        last_update = models.DateTimeField(auto_now=True)
        user = models.ForeignKey(User)
        content = models.TextField()
        sub_text = models.ForeignKey(FooBar)
    
    class MyModelAdmin(CompareVersionAdmin):
        def compare_DateTimeField(self, obj, version1, version2, value1, value2):
            ''' compare all model datetime model field in ISO format '''
            date1 = value1.isoformat(" ")
            date2 = value2.isoformat(" ")
            html = html_diff(date1, date2)
            return html
        
        def compare_sub_text(self, obj, version1, version2, value1, value2):
            ''' field_name example '''
            return "%s -> %s" % (value1, value2)
            
    ----------------------------------------------------------------------------
    """
    compare_template = "reversion/compare.html"

    # list/tuple of field names for the compare view. Set to None for all existing fields
    compare_fields = None

    # list/tuple of field names to exclude from compare view.
    compare_exclude = None

    def get_urls(self):
        """Returns the additional urls used by the Reversion admin."""
        urls = super(CompareVersionAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.module_name,
        reversion_urls = patterns("",
                                  url("^([^/]+)/history/compare/$", admin_site.admin_view(self.compare_view), name='%s_%s_compare' % info),
                                  )
        return reversion_urls + urls

    def _get_action_list(self, request, object_id, extra_context=None):
        """Renders the history view."""
        object_id = unquote(object_id) # Underscores in primary key get quoted to "_5F"
        opts = self.model._meta
        action_list = [
            {
                "version": version,
                "revision": version.revision,
                "url": reverse("%s:%s_%s_revision" % (self.admin_site.name, opts.app_label, opts.module_name), args=(quote(version.object_id), version.id)),
            }
            for version
            in self._order_version_queryset(self.revision_manager.get_for_object_reference(
                self.model,
                object_id,
            ).select_related("revision__user"))
        ]
        return action_list

    def history_view(self, request, object_id, extra_context=None):
        """Renders the history view."""
        action_list = self._get_action_list(request, object_id, extra_context=extra_context)

        if len(action_list) < 2:
            # Less than two history items aren't enough to compare ;)
            comparable = False
        else:
            comparable = True
            # for pre selecting the compare radio buttons depend on the ordering:
            if self.history_latest_first:
                action_list[0]["first"] = True
                action_list[1]["second"] = True
            else:
                action_list[-1]["first"] = True
                action_list[-2]["second"] = True

        # Compile the context.
        context = {
            "action_list": action_list,
            "comparable": comparable,
            "compare_view": True,
        }
        context.update(extra_context or {})
        return super(VersionAdmin, self).history_view(request, object_id, context)

    def fallback_compare(self, obj, version1, version2, value1, value2):
        """
        Simply create a html diff from the repr() result.
        Used for every field which has no own compare method.
        """
        if not isinstance(value1, basestring):
            # FIXME: How to create a better representation of the current value?
            value1 = repr(value1)
            value2 = repr(value2)

        html = html_diff(value1, value2)
        return html

    def _get_compare(self, field, field_name, obj, version1, version2, value1, value2):
        """
        Call the methods to create the compare html part.
        Try:
            1. name scheme: "compare_%s" % field_name
            2. name scheme: "compare_%s" % field.get_internal_type()
            3. Fallback to: self.fallback_compare()
        """
        def _get_compare_func(suffix):
            func_name = "compare_%s" % suffix
            if hasattr(self, func_name):
                func = getattr(self, func_name)
                return func

        # Try method in the name scheme: "compare_%s" % field_name
        func = _get_compare_func(field_name)
        if func is not None:
            html = func(obj, version1, version2, value1, value2)
            return html

        # Try method in the name scheme: "compare_%s" % field.get_internal_type()
        internal_type = field.get_internal_type()
        func = _get_compare_func(internal_type)
        if func is not None:
            html = func(obj, version1, version2, value1, value2)
            return html

        # Fallback to self.fallback_compare()
        html = self.fallback_compare(obj, version1, version2, value1, value2)
        return html

    def compare(self, obj, version1, version2):
        """
        Create a generic html diff from the obj between version1 and version2:
        
            A diff of every changes field values.
        
        This method should be overwritten, to create a nice diff view
        coordinated with the model.
        """
        diff = []

        for field in obj._meta.fields:
            #print field, field.db_type, field.get_internal_type()

            field_name = field.name

            if self.compare_fields and field_name not in self.compare_fields:
                continue
            if self.compare_exclude and field_name in self.compare_exclude:
                continue

            value1 = version1.field_dict[field_name]
            value2 = version2.field_dict[field_name]

            if value1 == value2:
                # Skip all fields that aren't changed
                continue

            html = self._get_compare(field, field_name, obj, version1, version2, value1, value2)

            diff.append({
                "field_name": field_name,
                "diff": html
            })
        return diff

    def compare_view(self, request, object_id, extra_context=None):
        """
        compare two versions.
        Used self.make_compare() to create the html diff.
        """
        if self.compare is None:
            raise Http404("Compare view not enabled.")

        form = SelectDiffForm(request.GET)
        if not form.is_valid():
            raise Http404("Wrong version IDs.")

        version_id1 = form.cleaned_data["version_id1"]
        version_id2 = form.cleaned_data["version_id2"]

        object_id = unquote(object_id) # Underscores in primary key get quoted to "_5F"
        obj = get_object_or_404(self.model, pk=object_id)
        version1 = get_object_or_404(Version, pk=version_id1, object_id=unicode(obj.pk))
        version2 = get_object_or_404(Version, pk=version_id2, object_id=unicode(obj.pk))

        if version_id1 > version_id2:
            # Compare always the newest one with the older one 
            version1, version2 = version2, version1

        compare_data = self.compare(obj, version1, version2)

        opts = self.model._meta

        context = {
            "opts": opts,
            "app_label": opts.app_label,
            "module_name": capfirst(opts.verbose_name),
            "title": _("Compare %(name)s") % {"name": version1.object_repr},
            "obj": obj,
            "compare_data": compare_data,
            "version1": version1,
            "version2": version2,
            "changelist_url": reverse("%s:%s_%s_changelist" % (self.admin_site.name, opts.app_label, opts.module_name)),
            "history_url": reverse("%s:%s_%s_history" % (self.admin_site.name, opts.app_label, opts.module_name), args=(quote(obj.pk),)),
        }
        extra_context = extra_context or {}
        context.update(extra_context)
        return render_to_response(self.compare_template or self._get_template_list("compare.html"),
            context, template.RequestContext(request))
