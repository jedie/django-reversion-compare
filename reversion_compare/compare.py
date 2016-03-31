"""
    compare
    ~~~~~~~

    Compare objects for django-reversion-compare

    :copyleft: 2012-2016 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.translation import ugettext as _


from reversion_compare import reversion_api


logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class FieldVersionDoesNotExist(object):
    """
    Sentinel object to handle missing fields
    """
    def __str__(self):
        return force_text(_("Field didn't exist!"))

DOES_NOT_EXIST = FieldVersionDoesNotExist()


class CompareObject(object):
    def __init__(self, field, field_name, obj, version, has_int_pk, adapter):
        self.field = field
        self.field_name = field_name
        self.obj = obj
        self.version = version  # instance of reversion.models.Version()
        self.has_int_pk = has_int_pk
        self.adapter = adapter
        # try and get a value, if none punt
        self.value = version.field_dict.get(field_name, DOES_NOT_EXIST)

    def _obj_repr(self, obj):
        # FIXME: How to create a better representation of the current value?
        try:
            return str(obj)
        except Exception as e:
            return repr(obj)

    def _choices_repr(self, obj):
        return force_text(dict(self.field.flatchoices).get(obj, obj),
                          strings_only=True)

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

        if self.field.choices:
            return self._choices_repr(self.value)

        if isinstance(self.value, str):
            return self.value
        else:
            return self._obj_repr(self.value)

    def __cmp__(self, other):
        raise NotImplemented()

    def __eq__(self, other):
        if hasattr(self.field, 'get_internal_type'):
            assert self.field.get_internal_type() != "ManyToManyField"

        if self.value != other.value:
            return False
        
        # see - https://hynek.me/articles/hasattr/
        internal_type = getattr(self.field,'get_internal_type',None)
        if internal_type is None or internal_type() == "ForeignKey":  # FIXME!
            if self.version.field_dict != other.version.field_dict:
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_related(self):
        if getattr(self.field, 'rel', None):
            obj = self.version.object_version.object
            try:
                return getattr(obj, self.field.name, None)
            except ObjectDoesNotExist:
                return None

    def get_reverse_foreign_key(self):
        obj = self.version.object_version.object
        if self.has_int_pk and self.field.related_name and hasattr(obj, self.field.related_name):
            if isinstance(self.field, models.fields.related.OneToOneRel):
                try:
                    ids = [getattr(obj, str(self.field.related_name)).pk]
                except ObjectDoesNotExist:
                    ids = []
            else:
                ids = [v.id for v in getattr(obj, str(self.field.related_name)).all()]  # is: version.field_dict[field.name]
                if ids == [] and any([f.name.endswith('_ptr') for f in obj._meta.fields]):
                    # If there is a _ptr this is a multiinheritance table and inherits from a non-abstract class
                    # lets try and get the parent items associated entries for this field
                    others = self.version.revision.version_set.filter(object_id=self.version.object_id)
                    for p in others:
                        p_obj = p.object_version.object
                        if type(p_obj) != type(obj) and hasattr(p_obj,str(self.field.related_name)):
                            ids = [v.id for v in getattr(p_obj, str(self.field.related_name)).all()]

        else:
            return ([], [], [], [])  # TODO: refactory that

        # Get the related model of the current field:
        related_model = self.field.field.model
        return self.get_many_to_something(ids, related_model, is_reverse=True)

    def get_many_to_many(self):
        """
        returns a queryset with all many2many objects
        """
        if self.field.get_internal_type() != "ManyToManyField":  # FIXME!
            return ([], [], [], [])  # TODO: refactory that
        elif self.value is DOES_NOT_EXIST:
            return ([], [], [], [])  # TODO: refactory that

        related_model = self.field.rel.to

        ids = None
        if reversion_api.has_int_pk(related_model):
            ids = [int(v) for v in self.value]  # is: version.field_dict[field.name]

        # Get the related model of the current field:
        return self.get_many_to_something(ids, related_model)

    def get_many_to_something(self, ids, related_model, is_reverse=False):

        # get instance of reversion.models.Revision():
        # A group of related object versions.
        old_revision = self.version.revision

        # Get a queryset with all related objects.
        versions = old_revision.version_set.filter(
            content_type=ContentType.objects.get_for_model(related_model),
            object_id__in=ids
        )

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

        deleted = []
        if is_reverse:
            true_missing_objects = []
            for o in missing_objects:
                for ver in reversion_api.get_for_object(o):
                    # An object can only be missing if it actually existed prior to this version
                    # Otherwise its a new item
                    if ver.revision.date_created < old_revision.date_created:
                        true_missing_objects.append(o)
            missing_objects = true_missing_objects
            deleted = [d for d in reversion_api.get_deleted(related_model) if d.revision == old_revision]
        return versions, missing_objects, missing_ids, deleted

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
        m2m_versions, missing_objects, missing_ids, deleted = self.get_many_to_many()
        if m2m_versions or missing_objects or missing_ids:
            result.append(
                "many-to-many.......: %s" % ", ".join(
                    ["%s (%s)" % (
                        item,
                        item.type
                    ) for item in m2m_versions]
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
    def __init__(self, field, field_name, obj, version1, version2, manager, is_reversed):
        self.field = field
        self.field_name = field_name
        self.obj = obj

        model = self.obj.__class__
        self.has_int_pk = reversion_api.has_int_pk(model)
        self.adapter = manager.get_adapter(model)  # VersionAdapter instance

        # is a related field (ForeignKey, ManyToManyField etc.)
        self.is_related = getattr(self.field, 'rel', None) is not None
        self.is_reversed = is_reversed
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

        info = None
        if hasattr(self.field, 'get_internal_type') and self.field.get_internal_type() == "ManyToManyField":
            info = self.get_m2m_change_info()
        elif self.is_reversed:
            info = self.get_m2o_change_info()
        if info:
            keys = (
                "changed_items", "removed_items", "added_items",
                "removed_missing_objects", "added_missing_objects", 'deleted_items'
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
        # return self._get_both_results("get_many_to_many")
        m2m_data1, m2m_data2 = self._get_both_results("get_many_to_many")
        return m2m_data1, m2m_data2

    def get_reverse_foreign_key(self):
        return self._get_both_results("get_reverse_foreign_key")

    M2O_CHANGE_INFO = None

    def get_m2o_change_info(self):
        if self.M2O_CHANGE_INFO is not None:
            return self.M2O_CHANGE_INFO

        m2o_data1, m2o_data2 = self.get_reverse_foreign_key()

        self.M2O_CHANGE_INFO = self.get_m2s_change_info(m2o_data1, m2o_data2)
        return self.M2O_CHANGE_INFO

    M2M_CHANGE_INFO = None

    def get_m2m_change_info(self):
        if self.M2M_CHANGE_INFO is not None:
            return self.M2M_CHANGE_INFO

        m2m_data1, m2m_data2 = self.get_many_to_many()

        self.M2M_CHANGE_INFO = self.get_m2s_change_info(m2m_data1, m2m_data2)
        return self.M2M_CHANGE_INFO

    # Abstract Many-to-Something (either -many or -one) as both
    # many2many and many2one relationships looks the same from the refered object.
    def get_m2s_change_info(self, obj1_data, obj2_data):

        result1, missing_objects1, missing_ids1, deleted1 = obj1_data
        result2, missing_objects2, missing_ids2, deleted2 = obj2_data

        # missing_objects_pk1 = [obj.pk for obj in missing_objects1]
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

        return {
            "changed_items": changed_items,
            "removed_items": removed_items,
            "added_items": added_items,
            "same_items": same_items,
            "same_missing_objects": same_missing_objects,
            "removed_missing_objects": removed_missing_objects,
            "added_missing_objects": added_missing_objects,
            "deleted_items": deleted1,
        }


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

        logger.debug("-" * 79)

