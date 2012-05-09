# coding: utf-8

"""
    admin
    ~~~~~
    
    Admin extensions for django-reversion-compare

    :copyleft: 2012 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django import template
from django.conf.urls.defaults import patterns, url
from django.contrib.admin.util import unquote, quote
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.utils.text import capfirst
from django.utils.translation import ugettext as _

from reversion.admin import VersionAdmin
from reversion.models import Version

from reversion_compare.forms import SelectDiffForm
from reversion_compare.helpers import html_diff
from django.conf import settings


class CompareObject(object):
    def __init__(self, field, field_name, obj, version):
        self.field = field
        self.field_name = field_name
        self.obj = obj
        self.version = version
        self.value = version.field_dict[field_name]

    def to_string(self):
        if isinstance(self.value, basestring):
            return self.value
        else:
            # FIXME: How to create a better representation of the current value?
            return repr(self.value)

    def __cmp__(self, other):
        raise NotImplemented()

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def get_related(self):
        if self.field.rel is not None:
            obj = self.version.object_version.object
            related = getattr(obj, self.field.name)
            return related

    def debug(self):
        if not settings.DEBUG:
            return
        print "field..............: %r" % self.field
        print "field_name.........: %r" % self.field_name
        print "field internal type: %r" % self.field.get_internal_type()
        print "field_dict.........: %s" % repr(self.version.field_dict)
        print "obj................: %r (pk: %s, id: %s)" % (self.obj, self.obj.pk, id(self.obj))
        print "version............: %r (pk: %s, id: %s)" % (self.version, self.version.pk, id(self.version))
        print "value..............: %r" % self.value
        print "to string..........: %s" % repr(self.to_string())
        print "related............: %s" % repr(self.get_related())


class CompareObjects(object):
    def __init__(self, field, field_name, obj, version1, version2):
        self.field = field
        self.field_name = field_name
        self.obj = obj

        self.compare_obj1 = CompareObject(field, field_name, obj, version1)
        self.compare_obj2 = CompareObject(field, field_name, obj, version2)

        self.value1 = self.compare_obj1.value
        self.value2 = self.compare_obj2.value

    def changed(self):
        return self.compare_obj1 != self.compare_obj2

    def _get_result(self, compare_obj, func_name):
        func = getattr(compare_obj, func_name)
        result = func()
        return result

    def _get_both_results(self, func_name):
        result1 = self._get_result(self.compare_obj1, func_name)
        result2 = self._get_result(self.compare_obj2, func_name)
        return (result1, result2)

    def to_string(self):
        return self._get_both_results("to_string")

    def get_related(self):
        return self._get_both_results("get_related")

    def debug(self):
        if not settings.DEBUG:
            return
        print "_______________________________"
        print " *** CompareObjects debug: ***"
        print "changed:", self.changed()
        print "_________________________"
        print " *** debug for obj1: ***"
        self.compare_obj1.debug()
        print "_________________________"
        print " *** debug for obj2: ***"
        self.compare_obj2.debug()
        print "-"*79


class BaseCompareVersionAdmin(VersionAdmin):
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

    # Template file used for the compare view:    
    compare_template = "reversion-compare/compare.html"

    # list/tuple of field names for the compare view. Set to None for all existing fields
    compare_fields = None

    # list/tuple of field names to exclude from compare view.
    compare_exclude = None

    # change template from django-reversion to add compare selection form: 
    object_history_template = "reversion-compare/object_history.html"

    # sort from new to old as default, see: https://github.com/etianen/django-reversion/issues/77 
    history_latest_first = True

    def get_urls(self):
        """Returns the additional urls used by the Reversion admin."""
        urls = super(BaseCompareVersionAdmin, self).get_urls()
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
        return super(BaseCompareVersionAdmin, self).history_view(request, object_id, context)

    def fallback_compare(self, obj_compare):
        """
        Simply create a html diff from the repr() result.
        Used for every field which has no own compare method.
        """
        value1, value2 = obj_compare.to_string()
        html = html_diff(value1, value2)
        return html

    def _get_compare(self, obj_compare):
        """
        Call the methods to create the compare html part.
        Try:
            1. name scheme: "compare_%s" % field_name
            2. name scheme: "compare_%s" % field.get_internal_type()
            3. Fallback to: self.fallback_compare()
        """
        def _get_compare_func(suffix):
            func_name = "compare_%s" % suffix
#            print "func_name:", func_name
            if hasattr(self, func_name):
                func = getattr(self, func_name)
                return func

        # Try method in the name scheme: "compare_%s" % field_name
        func = _get_compare_func(obj_compare.field_name)
        if func is not None:
            html = func(obj_compare)
            return html

        # Try method in the name scheme: "compare_%s" % field.get_internal_type()
        internal_type = obj_compare.field.get_internal_type()
        func = _get_compare_func(internal_type)
        if func is not None:
            html = func(obj_compare)
            return html

        # Fallback to self.fallback_compare()
        html = self.fallback_compare(obj_compare)
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

            obj_compare = CompareObjects(field, field_name, obj, version1, version2)
            #obj_compare.debug()

            if not obj_compare.changed():
                # Skip all fields that aren't changed
                continue

            html = self._get_compare(obj_compare)

            diff.append({
                "field": field,
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


class CompareVersionAdmin(BaseCompareVersionAdmin):
    """
    expand the base class with prepered compare methods.
    """
    def generic_add_remove(self, raw_value1, raw_value2, value1, value2):
        if raw_value1 is None:
            # a new values was added:
            context = {"value": value2}
            return render_to_string("reversion-compare/compare_generic_add.html", context)
        elif raw_value2 is None:
            # the existing value was removed:
            context = {"value": value1}
            return render_to_string("reversion-compare/compare_generic_remove.html", context)
        else:
            html = html_diff(value1, value2)
            return html

    def compare_DateTimeField(self, obj_compare):
        ''' compare all model datetime model field in ISO format '''
        context = {
            "date1": obj_compare.value1,
            "date2": obj_compare.value2,
        }
        return render_to_string("reversion-compare/compare_DateTimeField.html", context)

    def compare_ForeignKey(self, obj_compare):
        related1, related2 = obj_compare.get_related()
        value1, value2 = unicode(related1), unicode(related2)
#        value1, value2 = repr(related1), repr(related2)
        return self.generic_add_remove(related1, related2, value1, value2)

    def compare_FileField(self, obj_compare):
        value1 = obj_compare.value1
        value2 = obj_compare.value2

        # FIXME: Needed to not get 'The 'file' attribute has no file associated with it.' 
        if value1:
            value1 = value1.url
        else:
            value1 = None

        if value2:
            value2 = value2.url
        else:
            value2 = None

        return self.generic_add_remove(value1, value2, value1, value2)

