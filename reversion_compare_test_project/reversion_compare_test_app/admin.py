# coding: utf-8

"""
    admin
    ~~~~~
    
    All example admin classes would be used in django-reversion-compare unittests, too.

    :copyleft: 2012 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.contrib import admin
from django.contrib.contenttypes.generic import GenericStackedInline
from django.template.loader import render_to_string

from reversion_compare.admin import CompareVersionAdmin
from reversion_compare.helpers import html_diff

from reversion_compare_test_project.reversion_compare_test_app.models import SimpleModel, Manufacturer, Car, Person, Pet

from reversion.models import Revision, Version


#------------------------------------------------------------------------------
# add django-revision models to admin, needful for debugging:

class RevisionAdmin(admin.ModelAdmin):
    list_display = ("id", "manager_slug", "date_created", "user", "comment")
    list_display_links = ("date_created",)
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)
    list_filter = ("manager_slug", "user", "comment")
    search_fields = ("manager_slug", "user", "comment")

admin.site.register(Revision, RevisionAdmin)


class VersionAdmin(admin.ModelAdmin):
    list_display = ("object_repr", "revision", "type", "object_id", "content_type", "format",)
    list_display_links = ("object_repr", "object_id")
    list_filter = ("content_type", "format")
    search_fields = ("object_repr", "serialized_data")

admin.site.register(Version, VersionAdmin)

#------------------------------------------------------------------------------


class SimpleModelAdmin(CompareVersionAdmin):
    pass
admin.site.register(SimpleModel, SimpleModelAdmin)


class ManufacturerAdmin(CompareVersionAdmin):
    pass
admin.site.register(Manufacturer, ManufacturerAdmin)

class CarAdmin(CompareVersionAdmin):
    pass
admin.site.register(Car, CarAdmin)


class PersonAdmin(CompareVersionAdmin):
    pass
admin.site.register(Person, PersonAdmin)

class PetAdmin(CompareVersionAdmin):
    pass
admin.site.register(Pet, PetAdmin)







"""
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


class HobbyModelAdmin(CompareVersionAdmin):
    pass
admin.site.register(HobbyModel, HobbyModelAdmin)

class PersonModelAdmin(CompareVersionAdmin):
    pass
admin.site.register(PersonModel, PersonModelAdmin)

class GroupModelAdmin(CompareVersionAdmin):
    pass
admin.site.register(GroupModel, GroupModelAdmin)

class MembershipModelAdmin(CompareVersionAdmin):
    pass
admin.site.register(MembershipModel, MembershipModelAdmin)
"""
