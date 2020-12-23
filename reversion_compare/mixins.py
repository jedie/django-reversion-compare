"""
    mixin
    ~~~~~

    Mixins for views (admin and cbv) for django-reversion-compare

    :copyleft: 2012-2020 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models
from django.template.loader import render_to_string
from django.utils.encoding import force_str

from reversion_compare.compare import CompareObjects
from reversion_compare.helpers import html_diff


class CompareMixin:
    """A mixin to add comparison capabilities to your views"""

    # list/tuple of field names for the compare view. Set to None for all existing fields
    compare_fields = None

    # list/tuple of field names to exclude from compare view.
    compare_exclude = None

    # sort from new to old as default, see: https://github.com/etianen/django-reversion/issues/77
    history_latest_first = True

    def _order_version_queryset(self, queryset):
        """Applies the correct ordering to the given version queryset."""
        if self.history_latest_first:
            return queryset.order_by("-pk")
        return queryset.order_by("pk")

    def _get_compare(self, obj_compare):
        """
        Call the methods to create the compare html part.
        Try:
            1. name scheme: "compare_%s" % field_name
            2. name scheme: "compare_%s" % field.get_internal_type()
            3. Fallback to: self.fallback_compare()
        """

        def _get_compare_func(suffix):
            # logger.debug("func_name: %s", func_name)
            func_name = f"compare_{suffix}"
            if hasattr(self, func_name):
                func = getattr(self, func_name)
                if callable(func):
                    return func

        # Try method in the name scheme: "compare_%s" % field_name
        func = _get_compare_func(obj_compare.field_name)
        if func is not None:
            html = func(obj_compare)
            return html

        # Determine if its a reverse field
        if obj_compare.field in self.reverse_fields:
            func = _get_compare_func("ManyToOneRel")
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

        # This gathers the related reverse ForeignKey fields, so we can do ManyToOne compares
        self.reverse_fields = []
        for field in obj._meta.get_fields(include_hidden=True):
            f = getattr(field, "field", None)
            if isinstance(f, models.ForeignKey) and f not in fields:
                self.reverse_fields.append(f.remote_field)

        fields += self.reverse_fields

        has_unfollowed_fields = False

        for field in fields:
            # logger.debug("%s %s %s", field, field.db_type, field.get_internal_type())
            try:
                field_name = field.name
            except BaseException:
                # is a reverse FK field
                field_name = field.field_name

            if self.compare_fields and field_name not in self.compare_fields:
                continue
            if self.compare_exclude and field_name in self.compare_exclude:
                continue

            is_reversed = field in self.reverse_fields
            obj_compare = CompareObjects(field, field_name, obj, version1, version2, is_reversed)
            # obj_compare.debug()

            is_related = obj_compare.is_related
            follow = obj_compare.follow
            if is_related and not follow:
                has_unfollowed_fields = True

            if not obj_compare.changed():
                # Skip all fields that aren't changed
                continue

            html = self._get_compare(obj_compare)
            diff.append({"field": field, "is_related": is_related, "follow": follow, "diff": html})

        return diff, has_unfollowed_fields

    def fallback_compare(self, obj_compare):
        """
        Simply create a html diff from the repr() result.
        Used for every field which has no own compare method.
        """
        value1, value2 = obj_compare.to_string()
        html = html_diff(value1, value2)
        return html


class CompareMethodsMixin:
    """A mixin to add prepared compare methods."""

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
        # obj_compare.debug()
        value1, value2 = force_str(related1), force_str(related2)
        return self.generic_add_remove(related1, related2, value1, value2)

    def simple_compare_ManyToManyField(self, obj_compare):
        """ comma separated list of all m2m objects """
        m2m1, m2m2 = obj_compare.get_many_to_many()
        old = ", ".join(force_str(item) for item in m2m1)
        new = ", ".join(force_str(item) for item in m2m2)
        html = html_diff(old, new)
        return html

    def compare_ManyToOneRel(self, obj_compare):
        change_info = obj_compare.get_m2o_change_info()
        context = {"change_info": change_info}
        return render_to_string("reversion-compare/compare_generic_many_to_many.html", context)

    def compare_ManyToManyField(self, obj_compare):
        """ create a table for m2m compare """
        change_info = obj_compare.get_m2m_change_info()
        context = {"change_info": change_info}
        return render_to_string("reversion-compare/compare_generic_many_to_many.html", context)

    # compare_ManyToManyField = simple_compare_ManyToManyField

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
        """ compare all model datetime field in ISO format """
        context = {"date1": obj_compare.value1, "date2": obj_compare.value2}
        return render_to_string("reversion-compare/compare_DateTimeField.html", context)

    def compare_BooleanField(self, obj_compare):
        """ compare booleans as a complete field, rather than as a string """
        context = {"bool1": obj_compare.value1, "bool2": obj_compare.value2}
        return render_to_string("reversion-compare/compare_BooleanField.html", context)

    compare_NullBooleanField = compare_BooleanField
