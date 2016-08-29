# coding: utf-8

"""
    admin
    ~~~~~

    Admin extensions for django-reversion-compare

    :copyleft: 2012-2016 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import logging

from django import template
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
try:
    from django.contrib.admin.utils import unquote, quote
except ImportError:  # Django < 1.7  # pragma: no cover
    from django.contrib.admin.util import unquote, quote
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.text import capfirst
from django.utils.translation import ugettext as _

from reversion.admin import VersionAdmin
from reversion.models import Revision, Version

from reversion_compare.forms import SelectDiffForm
from reversion_compare.mixins import CompareMixin, CompareMethodsMixin

logger = logging.getLogger(__name__)


class BaseCompareVersionAdmin(CompareMixin, VersionAdmin):
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

    # change template from django-reversion to add compare selection form:
    object_history_template = "reversion-compare/object_history.html"

    def get_urls(self):
        """Returns the additional urls used by the Reversion admin."""
        urls = super(BaseCompareVersionAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.model_name,
        reversion_urls = [
            url("^([^/]+)/history/compare/$", admin_site.admin_view(self.compare_view), name='%s_%s_compare' % info),
        ]
        return reversion_urls + urls

    def _get_action_list(self, request, object_id, extra_context=None):
        """Renders the history view."""
        object_id = unquote(object_id)  # Underscores in primary key get quoted to "_5F"
        opts = self.model._meta
        action_list = [
            {
                "version": version,
                "revision": version.revision,
                "url": reverse("%s:%s_%s_revision" % (self.admin_site.name, opts.app_label, opts.model_name),
                               args=(quote(version.object_id), version.id)),
            }
            for version
            in self._order_version_queryset(Version.objects.get_for_object_reference(
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

    def compare_view(self, request, object_id, extra_context=None):
        """
        compare two versions.
        Used self.make_compare() to create the html diff.
        """
        if self.compare is None:
            raise Http404("Compare view not enabled.")

        form = SelectDiffForm(request.GET)
        if not form.is_valid():
            msg = "Wrong version IDs."
            if settings.DEBUG:
                msg += " (form errors: %s)" % ", ".join(form.errors)
            raise Http404(msg)

        version_id1 = form.cleaned_data["version_id1"]
        version_id2 = form.cleaned_data["version_id2"]

        if version_id1 > version_id2:
            # Compare always the newest one (#2) with the older one (#1)
            version_id1, version_id2 = version_id2, version_id1

        object_id = unquote(object_id)  # Underscores in primary key get quoted to "_5F"
        obj = get_object_or_404(self.model, pk=object_id)
        queryset = Version.objects.get_for_object(obj)
        version1 = get_object_or_404(queryset, pk=version_id1)
        version2 = get_object_or_404(queryset, pk=version_id2)

        next_version = queryset.filter(pk__gt=version_id2).last()
        prev_version = queryset.filter(pk__lt=version_id1).first()

        compare_data, has_unfollowed_fields = self.compare(obj, version1, version2)

        opts = self.model._meta

        context = {
            "opts": opts,
            "app_label": opts.app_label,
            "model_name": capfirst(opts.verbose_name),
            "title": _("Compare %(name)s") % {"name": version1.object_repr},
            "obj": obj,
            "compare_data": compare_data,
            "has_unfollowed_fields": has_unfollowed_fields,
            "version1": version1,
            "version2": version2,
            "changelist_url": reverse("%s:%s_%s_changelist" % (self.admin_site.name, opts.app_label, opts.model_name)),
            "change_url": reverse("%s:%s_%s_change" % (self.admin_site.name, opts.app_label, opts.model_name),
                                  args=(quote(obj.pk),)),
            "original": obj,
            "history_url": reverse("%s:%s_%s_history" % (self.admin_site.name, opts.app_label, opts.model_name),
                                   args=(quote(obj.pk),)),
        }

        # don't use urlencode with dict for generate prev/next-urls
        # Otherwise we can't unitests it!
        if next_version:
            next_url = "?version_id1=%i&version_id2=%i" % (
                version2.id, next_version.id
            )
            context.update({'next_url': next_url})
        if prev_version:
            prev_url = "?version_id1=%i&version_id2=%i" % (
                prev_version.id, version1.id
            )
            context.update({'prev_url': prev_url})

        extra_context = extra_context or {}
        context.update(extra_context)
        return render_to_response(self.compare_template or self._get_template_list("compare.html"),
                                  context, template.RequestContext(request))


class CompareVersionAdmin(CompareMethodsMixin, BaseCompareVersionAdmin):
    """
    expand the base class with prepared compare methods. This is the
    class to inherit
    """
    pass


if hasattr(settings, "ADD_REVERSION_ADMIN") and settings.ADD_REVERSION_ADMIN:
    class RevisionAdmin(admin.ModelAdmin):
        list_display = ("id", "date_created", "user", "comment")
        list_display_links = ("date_created",)
        date_hierarchy = 'date_created'
        ordering = ('-date_created',)
        list_filter = ("user", "comment")
        search_fields = ("user", "comment")

    admin.site.register(Revision, RevisionAdmin)

    
    class VersionAdmin(admin.ModelAdmin):
        list_display = ("object_repr", "revision", "object_id", "content_type", "format",)
        list_display_links = ("object_repr", "object_id")
        list_filter = ("content_type", "format")
        search_fields = ("object_repr", "serialized_data")

    admin.site.register(Version, VersionAdmin)
