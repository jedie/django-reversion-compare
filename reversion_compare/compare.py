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
from django.utils.encoding import force_str
from django.utils.translation import ugettext as _
from reversion import is_registered
from reversion.models import Version
from reversion.revisions import _get_options


logger = logging.getLogger(__name__)


class FieldVersionDoesNotExist:
    """
    Sentinel object to handle missing fields
    """

    def __str__(self):
        return force_str(_("Field didn't exist!"))


DOES_NOT_EXIST = FieldVersionDoesNotExist()


class CompareObject:
    def __init__(self, field, field_name, obj, version_record, follow):
        self.field = field
        self.field_name = field_name
        self.obj = obj
        self.version_record = version_record  # instance of reversion.models.Version()
        self.follow = follow
        # try and get a value, if none punt
        self.compare_foreign_objects_as_id = getattr(settings, "REVERSION_COMPARE_FOREIGN_OBJECTS_AS_ID", False)
        # ignore not registered models
        self.ignore_not_registered = getattr(settings, "REVERSION_COMPARE_IGNORE_NOT_REGISTERED", False)
        if self.compare_foreign_objects_as_id:
            self.value = version_record.field_dict.get(getattr(field, "attname", field_name), DOES_NOT_EXIST)
        else:
            self.value = version_record.field_dict.get(field_name, DOES_NOT_EXIST)

    def _obj_repr(self, obj):
        # FIXME: How to create a better representation of the current value?
        try:
            return force_str(obj)
        except Exception:
            return repr(obj)

    def _choices_repr(self, obj):
        return force_str(dict(self.field.flatchoices).get(obj, obj), strings_only=True)

    def _to_string_ManyToManyField(self):
        return ", ".join(self._obj_repr(item) for item in self.get_many_to_many())

    def _to_string_ForeignKey(self):
        return self._obj_repr(self.get_related())

    def to_string(self):
        internal_type = self.field.get_internal_type()
        func_name = f"_to_string_{internal_type}"
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
        raise NotImplementedError

    def __eq__(self, other):
        if hasattr(self.field, "get_internal_type"):
            assert self.field.get_internal_type() != "ManyToManyField"

        if self.value != other.value:
            return False

        # see - https://hynek.me/articles/hasattr/
        if not self.compare_foreign_objects_as_id:
            internal_type = getattr(self.field, "get_internal_type", None)
            if internal_type is None or internal_type() == "ForeignKey":  # FIXME!
                if self.version_record.field_dict != other.version_record.field_dict:
                    return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_object_version(self):
        return self.version_record._object_version

    def get_related(self):
        if getattr(self.field, "related_model", None):
            obj = self.get_object_version().object
            try:
                return getattr(obj, self.field.name, None)
            except ObjectDoesNotExist:
                return None

    def get_reverse_foreign_key(self):
        obj = self.get_object_version().object
        if self.field.related_name and hasattr(obj, self.field.related_name):
            if isinstance(self.field, models.fields.related.OneToOneRel):
                try:
                    ids = {force_str(getattr(obj, force_str(self.field.related_name)).pk)}
                except ObjectDoesNotExist:
                    ids = set()
            else:
                # If there is a _ptr this is a multi-inheritance table and inherits from a non-abstract class
                ids = {force_str(v.pk) for v in getattr(obj, force_str(self.field.related_name)).all()}
                if not ids and any([f.name.endswith("_ptr") for f in obj._meta.get_fields()]):
                    # If there is a _ptr this is a multi-inheritance table and inherits from a non-abstract class
                    # lets try and get the parent items associated entries for this field
                    others = self.version_record.revision.version_set.filter(
                        object_id=self.version_record.object_id
                    ).all()
                    for p in others:
                        p_obj = p._object_version.object
                        if not isinstance(p_obj, type(obj)) and hasattr(p_obj, force_str(self.field.related_name)):
                            ids = {force_str(v.pk) for v in getattr(p_obj, force_str(self.field.related_name)).all()}
        else:
            return {}, {}, []  # TODO: refactor that

        # Get the related model of the current field:
        related_model = self.field.field.model
        return self.get_many_to_something(ids, related_model, is_reverse=True)

    def get_many_to_many(self):
        """
        returns a queryset with all many2many objects
        """
        if self.field.get_internal_type() != "ManyToManyField":  # FIXME!
            return {}, {}, []  # TODO: refactor that
        elif self.value is DOES_NOT_EXIST:
            return {}, {}, []  # TODO: refactor that

        try:
            ids = frozenset(map(force_str, self.value))
        except TypeError:
            # catch errors e.g. produced by taggit's TaggableManager
            logger.exception("Can't collect m2m ids")
            return {}, {}, []  # TODO: refactor that

        # Get the related model of the current field:
        return self.get_many_to_something(ids, self.field.related_model)

    def get_many_to_something(self, target_ids, related_model, is_reverse=False):
        # get instance of reversion.models.Revision():
        # A group of related object versions.
        old_revision = self.version_record.revision

        # Get a queryset with all related objects.
        versions = {
            ver.object_id: ver
            for ver in old_revision.version_set.filter(
                content_type=ContentType.objects.get_for_model(related_model), object_id__in=target_ids
            ).all()
        }

        missing_objects_dict = {}
        deleted = []

        if not self.follow:
            # This models was not registered with follow relations
            # Try to fill missing related objects
            potentially_missing_ids = target_ids.difference(frozenset(versions))
            # logger.debug(
            #     self.field_name,
            #     f"target: {target_ids} - actual: {versions} - missing: {potentially_missing_ids}"
            # )
            if potentially_missing_ids:
                missing_objects_dict = {
                    force_str(rel.pk): rel
                    for rel in related_model.objects.filter(pk__in=potentially_missing_ids).iterator()
                    if is_registered(rel.__class__) or not self.ignore_not_registered
                }

        if is_reverse:
            missing_objects_dict = {
                ver.object_id: ver
                for o in missing_objects_dict.values()
                for ver in Version.objects.get_for_object(o)
                if ver.revision.date_created < old_revision.date_created
            }

            if is_registered(related_model) or not self.ignore_not_registered:
                # shift query to database
                deleted = list(Version.objects.filter(revision=old_revision).get_deleted(related_model))
            else:
                deleted = []

        return versions, missing_objects_dict, deleted

    def get_debug(self):  # pragma: no cover
        if not settings.DEBUG:
            return

        result = [
            f"field..............: {self.field!r}",
            f"field_name.........: {self.field_name!r}",
            f"field internal type: {self.field.get_internal_type()!r}",
            f"field_dict.........: {self.version_record.field_dict!r}",
            f"obj................: {self.obj!r} (pk: {self.obj.pk}, id: {id(self.obj)})",
            (
                f"version............: {self.version_record!r}"
                f" (pk: {self.version_record.pk}, id: {id(self.version_record)})"
            ),
            f"value..............: {self.value!r}",
            f"to string..........: {self.to_string()!r}",
            f"related............: {self.get_related()!r}",
        ]
        m2m_versions, missing_objects, missing_ids, deleted = self.get_many_to_many()
        if m2m_versions or missing_objects or missing_ids:
            m2m = ', '.join(f'{item} ({item.type})' for item in m2m_versions)
            result.append(f"many-to-many.......: {m2m}")

            if missing_objects:
                result.append(f"missing m2m objects: {missing_objects!r}")
            else:
                result.append("missing m2m objects: (has no)")

            if missing_ids:
                result.append(f"missing m2m IDs....: {missing_ids!r}")
            else:
                result.append("missing m2m IDs....: (has no)")
        else:
            result.append("many-to-many.......: (has no)")

        return result

    def debug(self):  # pragma: no cover
        if not settings.DEBUG:
            return
        for item in self.get_debug():
            logger.debug(item)


class CompareObjects:
    def __init__(self, field, field_name, obj, version1, version2, is_reversed):
        self.field = field
        self.field_name = field_name
        self.obj = obj

        # is a related field (ForeignKey, ManyToManyField etc.)
        self.is_related = getattr(self.field, "related_model", None) is not None
        self.is_reversed = is_reversed
        if not self.is_related:
            self.follow = None
        elif self.field_name in _get_options(self.obj.__class__).follow:
            self.follow = True
        else:
            self.follow = False

        self.compare_obj1 = CompareObject(field, field_name, obj, version1, self.follow)
        self.compare_obj2 = CompareObject(field, field_name, obj, version2, self.follow)

        self.value1 = self.compare_obj1.value
        self.value2 = self.compare_obj2.value

        self.M2O_CHANGE_INFO = None
        self.M2M_CHANGE_INFO = None

    def changed(self):
        """ return True if at least one field has changed values. """

        info = None
        if hasattr(self.field, "get_internal_type") and self.field.get_internal_type() == "ManyToManyField":
            info = self.get_m2m_change_info()
        elif self.is_reversed:
            info = self.get_m2o_change_info()
        if info:
            keys = (
                "changed_items",
                "removed_items",
                "added_items",
                "removed_missing_objects",
                "added_missing_objects",
                "deleted_items",
            )
            for key in keys:
                if info[key]:
                    return True
            return False

        return self.compare_obj1 != self.compare_obj2

    def to_string(self):
        return self.compare_obj1.to_string(), self.compare_obj2.to_string()

    def get_related(self):
        return self.compare_obj1.get_related(), self.compare_obj2.get_related()

    def get_many_to_many(self):
        return self.compare_obj1.get_many_to_many(), self.compare_obj2.get_many_to_many()

    def get_reverse_foreign_key(self):
        return self.compare_obj1.get_reverse_foreign_key(), self.compare_obj2.get_reverse_foreign_key()

    def get_m2o_change_info(self):
        if self.M2O_CHANGE_INFO is not None:
            return self.M2O_CHANGE_INFO

        m2o_data1, m2o_data2 = self.get_reverse_foreign_key()

        self.M2O_CHANGE_INFO = self.get_m2s_change_info(m2o_data1, m2o_data2)
        return self.M2O_CHANGE_INFO

    def get_m2m_change_info(self):
        if self.M2M_CHANGE_INFO is not None:
            return self.M2M_CHANGE_INFO

        m2m_data1, m2m_data2 = self.get_many_to_many()

        self.M2M_CHANGE_INFO = self.get_m2s_change_info(m2m_data1, m2m_data2)
        return self.M2M_CHANGE_INFO

    # Abstract Many-to-Something (either -many or -one) as both
    # many2many and many2one relationships looks the same from the referred object.
    def get_m2s_change_info(self, obj1_data, obj2_data):

        result_dict1, missing_objects_dict1, deleted1 = obj1_data
        result_dict2, missing_objects_dict2, deleted2 = obj2_data

        # Create same_items, removed_items, added_items with related m2m items
        changed_items = []
        removed_items = []
        added_items = []
        same_items = []

        same_missing_objects_dict = {k: v for k, v in missing_objects_dict1.items() if k in missing_objects_dict2}
        removed_missing_objects_dict = {
            k: v for k, v in missing_objects_dict1.items() if k not in missing_objects_dict2
        }
        added_missing_objects_dict = {k: v for k, v in missing_objects_dict2.items() if k not in missing_objects_dict1}

        # logger.debug("same_missing_objects: %s", same_missing_objects_dict)
        # logger.debug("removed_missing_objects: %s", removed_missing_objects_dict)
        # logger.debug("added_missing_objects: %s", added_missing_objects_dict)

        for primary_key in set().union(result_dict1.keys(), result_dict2.keys()):
            if primary_key in result_dict1:
                version1 = result_dict1[primary_key]
            else:
                version1 = None

            if primary_key in result_dict2:
                version2 = result_dict2[primary_key]
            else:
                version2 = None

            # logger.debug("%r - %r - %r", primary_key, version1, version2)

            if version1 is not None and version2 is not None:
                # In both -> version changed or the same
                if version1.serialized_data == version2.serialized_data:
                    # logger.debug("same item: %s", version1)
                    same_items.append(version1)
                else:
                    changed_items.append((version1, version2))
            elif version1 is not None and version2 is None:
                # In 1 but not in 2 -> removed
                # logger.debug("%s %s", primary_key, missing_objects_dict2)
                # logger.debug("%s %s", repr(primary_key), repr(missing_objects_dict2))
                if primary_key in added_missing_objects_dict:
                    added_missing_objects_dict.pop(primary_key)
                    same_missing_objects_dict[primary_key] = missing_objects_dict2[primary_key]
                    continue
                removed_items.append(version1)
            elif version1 is None and version2 is not None:
                # In 2 but not in 1 -> added
                # logger.debug("added: %s", version2)
                added_items.append(version2)
            else:
                raise RuntimeError()

        # In Place Sorting of Lists (exclude changed since its a tuple)
        removed_items.sort(key=lambda item: force_str(item))
        added_items.sort(key=lambda item: force_str(item))
        same_items.sort(key=lambda item: force_str(item))
        deleted1.sort(key=lambda item: force_str(item))
        same_missing_objects = sorted(same_missing_objects_dict.values(), key=lambda item: force_str(item))
        removed_missing_objects = sorted(removed_missing_objects_dict.values(), key=lambda item: force_str(item))
        added_missing_objects = sorted(added_missing_objects_dict.values(), key=lambda item: force_str(item))

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

    def debug(self):  # pragma: no cover
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
