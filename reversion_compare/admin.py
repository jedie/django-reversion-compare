# coding: utf-8

"""
    admin
    ~~~~~
    
    Admin extensions for django-reversion-compare

    :copyleft: 2012 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import logging

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
from reversion.models import Version, VERSION_TYPE_CHOICES, VERSION_CHANGE, \
    has_int_pk

from reversion_compare.forms import SelectDiffForm
from reversion_compare.helpers import html_diff, compare_queryset
from django.conf import settings
from django.contrib.contenttypes.models import ContentType


logger = logging.getLogger(__name__)

VERSION_TYPE_DICT = dict(VERSION_TYPE_CHOICES)


class CompareObject(object):
    def __init__(self, field, field_name, obj, version, has_int_pk, adapter):
        self.field = field
        self.field_name = field_name
        self.obj = obj
        self.version = version # instance of reversion.models.Version()
        self.has_int_pk = has_int_pk
        self.adapter = adapter

        self.value = version.field_dict[field_name]

    def _obj_repr(self, obj):
        # FIXME: How to create a better representation of the current value?
        try:
            return unicode(obj)
        except Exception, e:
            return repr(obj)

    def _to_string_ManyToManyField(self):
        queryset = self.get_many_to_many()
        return ", ".join([self._obj_repr(item) for item in queryset])

    def _to_string_ForeignKey(self):
        obj = self.get_related()
        return self._obj_repr(obj)

    def to_string(self):
        internal_type = self.field.get_internal_type()
        func_name = "_to_string_%s" % internal_type
        if hasattr(self, func_name):
            func = getattr(self, func_name)
            return func()

        if isinstance(self.value, basestring):
            return self.value
        else:
            return self._obj_repr(self.value)

    def __cmp__(self, other):
        raise NotImplemented()

    def __eq__(self, other):
        assert self.field.get_internal_type() != "ManyToManyField"
        
        if self.value != other.value:
            return False

        if self.field.get_internal_type() == "ForeignKey": # FIXME!
            if self.version.field_dict != other.version.field_dict:
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_related(self):
        if self.field.rel is not None:
            obj = self.version.object_version.object
            related = getattr(obj, self.field.name)
            return related

    def get_many_to_many(self):
        """
        returns a queryset with all many2many objects
        """
        if self.field.get_internal_type() != "ManyToManyField": # FIXME!
            return (None, None, None)

        if self.has_int_pk:
            ids = [int(v) for v in self.value] # is: version.field_dict[field.name]

        # get instance of reversion.models.Revision(): A group of related object versions. 
        old_revision = self.version.revision

        # Get the related model of the current field:
        related_model = self.field.rel.to

        # Get a queryset with all related objects.
        queryset = old_revision.version_set.filter(
            content_type=ContentType.objects.get_for_model(related_model),
            object_id__in=ids
        )
#        logger.debug("m2m queryset: %s", queryset)

        versions = sorted(list(queryset))
#        logger.debug("versions: %s", versions)

        if self.has_int_pk:
            # The primary_keys would be stored in a text field -> convert it to integers
            # This is interesting in different places!
            for version in versions:
                version.object_id = int(version.object_id)

        missing_objects = []
        missing_ids = []

        if self.field_name not in self.adapter.follow:
            # This models was not registered with follow relations
            # Try to fill missing related objects
            target_ids = set(ids)
            actual_ids = set([version.object_id for version in versions])
            missing_ids1 = target_ids.difference(actual_ids)
            # logger.debug(self.field_name, "target: %s - actual: %s - missing: %s" % (target_ids, actual_ids, missing_ids1))
            if missing_ids1:
                missing_objects = related_model.objects.all().filter(pk__in=missing_ids1)
                missing_ids = list(target_ids.difference(set(missing_objects.values_list('pk', flat=True))))

        return versions, missing_objects, missing_ids

    def get_debug(self):
        if not settings.DEBUG:
            return

        result = [
            "field..............: %r" % self.field,
            "field_name.........: %r" % self.field_name,
            "field internal type: %r" % self.field.get_internal_type(),
            "field_dict.........: %s" % repr(self.version.field_dict),
            "adapter............: %r (follow: %r)" % (self.adapter, ", ".join(self.adapter.follow)),
            "has_int_pk ........: %r" % self.has_int_pk,
            "obj................: %r (pk: %s, id: %s)" % (self.obj, self.obj.pk, id(self.obj)),
            "version............: %r (pk: %s, id: %s)" % (self.version, self.version.pk, id(self.version)),
            "value..............: %r" % self.value,
            "to string..........: %s" % repr(self.to_string()),
            "related............: %s" % repr(self.get_related()),
        ]
        m2m_versions, missing_objects, missing_ids = self.get_many_to_many()
        if m2m_versions or missing_objects or missing_ids:
            result.append(
                "many-to-many.......: %s" % ", ".join(
                    ["%s (%s)" % (item, VERSION_TYPE_DICT[item.type]) for item in m2m_versions]
                )
            )

            if missing_objects:
                result.append("missing m2m objects: %s" % repr(missing_objects))
            else:
                result.append("missing m2m objects: (has no)")

            if missing_ids:
                result.append("missing m2m IDs....: %s" % repr(missing_ids))
            else:
                result.append("missing m2m IDs....: (has no)")
        else:
            result.append("many-to-many.......: (has no)")

        return result


    def debug(self):
        if not settings.DEBUG:
            return
        for item in self.get_debug():
            logger.debug(item)


class CompareObjects(object):
    def __init__(self, field, field_name, obj, version1, version2, manager):
        self.field = field
        self.field_name = field_name
        self.obj = obj

        model = self.obj.__class__
        self.has_int_pk = has_int_pk(model)
        self.adapter = manager.get_adapter(model) # VersionAdapter instance

        # is a related field (ForeignKey, ManyToManyField etc.)
        self.is_related = self.field.rel is not None
        
        if not self.is_related:
            self.follow = None
        elif self.field_name in self.adapter.follow:
            self.follow = True
        else:
            self.follow = False          

        self.compare_obj1 = CompareObject(field, field_name, obj, version1, self.has_int_pk, self.adapter)
        self.compare_obj2 = CompareObject(field, field_name, obj, version2, self.has_int_pk, self.adapter)

        self.value1 = self.compare_obj1.value
        self.value2 = self.compare_obj2.value

    def changed(self):
        """ return True if at least one field has changed values. """
        
        if self.field.get_internal_type() == "ManyToManyField": # FIXME!
            info = self.get_m2m_change_info()
            keys = (
                "changed_items", "removed_items", "added_items",
                "removed_missing_objects", "added_missing_objects"
            )
            for key in keys:
                if info[key]:
                    return True 
            return False 
        
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

    def get_many_to_many(self):
        #return self._get_both_results("get_many_to_many")
        m2m_data1, m2m_data2 = self._get_both_results("get_many_to_many")
        return m2m_data1, m2m_data2

    M2M_CHANGE_INFO = None
    def get_m2m_change_info(self):
        if self.M2M_CHANGE_INFO is not None:
            return self.M2M_CHANGE_INFO
        
        m2m_data1, m2m_data2 = self.get_many_to_many()

        result1, missing_objects1, missing_ids1 = m2m_data1
        result2, missing_objects2, missing_ids2 = m2m_data2

#        missing_objects_pk1 = [obj.pk for obj in missing_objects1]
#        missing_objects_pk2 = [obj.pk for obj in missing_objects2]
        missing_objects_dict2 = dict([(obj.pk, obj) for obj in missing_objects2])

        # logger.debug("missing_objects1: %s", missing_objects1)
        # logger.debug("missing_objects2: %s", missing_objects2)
        # logger.debug("missing_ids1: %s", missing_ids1)
        # logger.debug("missing_ids2: %s", missing_ids2)

        missing_object_set1 = set(missing_objects1)
        missing_object_set2 = set(missing_objects2)
        # logger.debug("%s %s", missing_object_set1, missing_object_set2)

        same_missing_objects = missing_object_set1.intersection(missing_object_set2)
        removed_missing_objects = missing_object_set1.difference(missing_object_set2)
        added_missing_objects = missing_object_set2.difference(missing_object_set1)

        # logger.debug("same_missing_objects: %s", same_missing_objects)
        # logger.debug("removed_missing_objects: %s", removed_missing_objects)
        # logger.debug("added_missing_objects: %s", added_missing_objects)


        # Create same_items, removed_items, added_items with related m2m items

        changed_items = []
        removed_items = []
        added_items = []
        same_items = []

        primary_keys1 = [version.object_id for version in result1]
        primary_keys2 = [version.object_id for version in result2]

        result_dict1 = dict([(version.object_id, version) for version in result1])
        result_dict2 = dict([(version.object_id, version) for version in result2])

        # logger.debug(result_dict1)
        # logger.debug(result_dict2)

        for primary_key in set(primary_keys1).union(set(primary_keys2)):
            if primary_key in result_dict1:
                version1 = result_dict1[primary_key]
            else:
                version1 = None

            if primary_key in result_dict2:
                version2 = result_dict2[primary_key]
            else:
                version2 = None

            #logger.debug("%r - %r - %r", primary_key, version1, version2)

            if version1 is not None and version2 is not None:
                # In both -> version changed or the same
                if version1.serialized_data == version2.serialized_data:
                    #logger.debug("same item: %s", version1)
                    same_items.append(version1)
                else:
                    changed_items.append((version1, version2))
            elif version1 is not None and version2 is None:
                # In 1 but not in 2 -> removed
                #logger.debug("%s %s", primary_key, missing_objects_pk2)
                #logger.debug("%s %s", repr(primary_key), repr(missing_objects_pk2))
                if primary_key in missing_objects_dict2:
                    missing_object = missing_objects_dict2[primary_key]
                    added_missing_objects.remove(missing_object)
                    same_missing_objects.add(missing_object)
                    continue

                removed_items.append(version1)
            elif version1 is None and version2 is not None:
                # In 2 but not in 1 -> added
                #logger.debug("added: %s", version2)
                added_items.append(version2)
            else:
                raise RuntimeError()

        self.M2M_CHANGE_INFO = {
            "changed_items": changed_items,
            "removed_items": removed_items,
            "added_items": added_items,
            "same_items": same_items,
            "same_missing_objects": same_missing_objects,
            "removed_missing_objects": removed_missing_objects,
            "added_missing_objects": added_missing_objects,
        }
        return self.M2M_CHANGE_INFO


    def debug(self):
        if not settings.DEBUG:
            return
        logger.debug("_______________________________")
        logger.debug(" *** CompareObjects debug: ***")
        logger.debug("changed: %s", self.changed())
        logger.debug("follow: %s", self.follow)

        debug1 = self.compare_obj1.get_debug()
        debug2 = self.compare_obj2.get_debug()
        debug_set1 = set(debug1)
        debug_set2 = set(debug2)

        logger.debug(" *** same attributes/values in obj1 and obj2: ***")
        intersection = debug_set1.intersection(debug_set2)
        for item in debug1:
            if item in intersection:
                logger.debug(item)

        logger.debug(" -" * 40)
        logger.debug(" *** unique attributes/values from obj1: ***")
        difference = debug_set1.difference(debug_set2)
        for item in debug1:
            if item in difference:
                logger.debug(item)

        logger.debug(" -" * 40)
        logger.debug(" *** unique attributes/values from obj2: ***")
        difference = debug_set2.difference(debug_set1)
        for item in debug2:
            if item in difference:
                logger.debug(item)

        logger.debug("-"*79)


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
            # logger.debug("func_name: %s", func_name)
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

        # Create a list of all normal fields and append many-to-many fields
        fields = [field for field in obj._meta.fields]
        concrete_model = obj._meta.concrete_model
        fields += concrete_model._meta.many_to_many

        has_unfollowed_fields = False

        for field in fields:
            #logger.debug("%s %s %s", field, field.db_type, field.get_internal_type())

            field_name = field.name

            if self.compare_fields and field_name not in self.compare_fields:
                continue
            if self.compare_exclude and field_name in self.compare_exclude:
                continue

            obj_compare = CompareObjects(field, field_name, obj, version1, version2, self.revision_manager)
            #obj_compare.debug()

            is_related = obj_compare.is_related
            follow = obj_compare.follow
            if is_related and not follow:
                has_unfollowed_fields = True

            if not obj_compare.changed():
                # Skip all fields that aren't changed
                continue

            html = self._get_compare(obj_compare)

            diff.append({
                "field": field,
                "is_related": is_related,
                "follow": follow,
                "diff": html,
            })

        return diff, has_unfollowed_fields

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

        object_id = unquote(object_id) # Underscores in primary key get quoted to "_5F"
        obj = get_object_or_404(self.model, pk=object_id)
        queryset = self.revision_manager.get_for_object(obj)
        version1 = get_object_or_404(queryset, pk=version_id1)
        version2 = get_object_or_404(queryset, pk=version_id2)

        if version_id1 > version_id2:
            # Compare always the newest one with the older one 
            version1, version2 = version2, version1

        compare_data, has_unfollowed_fields = self.compare(obj, version1, version2)

        opts = self.model._meta

        context = {
            "opts": opts,
            "app_label": opts.app_label,
            "module_name": capfirst(opts.verbose_name),
            "title": _("Compare %(name)s") % {"name": version1.object_repr},
            "obj": obj,
            "compare_data": compare_data,
            "has_unfollowed_fields": has_unfollowed_fields,
            "version1": version1,
            "version2": version2,
            "changelist_url": reverse("%s:%s_%s_changelist" % (self.admin_site.name, opts.app_label, opts.module_name)),
            "change_url": reverse("%s:%s_%s_change" % (self.admin_site.name, opts.app_label, opts.module_name), args=(quote(obj.pk),)),
            "original": obj,
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

    def compare_ForeignKey(self, obj_compare):
        related1, related2 = obj_compare.get_related()
        obj_compare.debug()
        value1, value2 = unicode(related1), unicode(related2)
#        value1, value2 = repr(related1), repr(related2)
        return self.generic_add_remove(related1, related2, value1, value2)

    def simple_compare_ManyToManyField(self, obj_compare):
        """ comma separated list of all m2m objects """
        m2m1, m2m2 = obj_compare.get_many_to_many()
        old = ", ".join([unicode(item) for item in m2m1])
        new = ", ".join([unicode(item) for item in m2m2])
        html = html_diff(old, new)
        return html

    def compare_ManyToManyField(self, obj_compare):
        """ create a table for m2m compare """
        change_info = obj_compare.get_m2m_change_info()
        context = {"change_info": change_info}
        return render_to_string("reversion-compare/compare_generic_many_to_many.html", context)

#    compare_ManyToManyField = simple_compare_ManyToManyField

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

    def compare_DateTimeField(self, obj_compare):
        ''' compare all model datetime model field in ISO format '''
        context = {
            "date1": obj_compare.value1,
            "date2": obj_compare.value2,
        }
        return render_to_string("reversion-compare/compare_DateTimeField.html", context)
