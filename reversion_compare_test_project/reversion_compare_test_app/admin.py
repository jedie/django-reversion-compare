# coding: utf-8


from django.contrib import admin
from django.contrib.contenttypes.generic import GenericStackedInline
from django.template.loader import render_to_string

from reversion_compare.admin import CompareVersionAdmin
from reversion_compare.helpers import html_diff

from reversion_compare_test_project.reversion_compare_test_app.models import ChildModel, RelatedModel, GenericRelatedModel, \
    FlatExampleModel



class RelatedModelInline(admin.StackedInline):
    model = RelatedModel


class GenericRelatedInline(GenericStackedInline):
    model = GenericRelatedModel


class ChildModelAdmin(CompareVersionAdmin):
    inlines = RelatedModelInline, GenericRelatedInline,
    list_display = ("parent_name", "child_name",)
    list_editable = ("child_name",)

admin.site.register(ChildModel, ChildModelAdmin)


class FlatExampleModelAdmin(CompareVersionAdmin):
    def compare_sub_text(self, obj, version1, version2, value1, value2):
        ''' field_name example '''
        return "%s -> %s" % (value1, value2)

admin.site.register(FlatExampleModel, FlatExampleModelAdmin)
