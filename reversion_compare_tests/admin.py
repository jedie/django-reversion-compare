# coding: utf-8

"""
    admin
    ~~~~~

    All example admin classes would be used in django-reversion-compare unittests, too.

    :copyleft: 2012-2015 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""



from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from .models import Car, CustomModel, Factory, Identity, Person, Pet, SimpleModel, TemplateField, VariantModel


class SimpleModelAdmin(CompareVersionAdmin):
    pass


admin.site.register(SimpleModel, SimpleModelAdmin)


class FactoryAdmin(CompareVersionAdmin):
    pass


admin.site.register(Factory, FactoryAdmin)


class CarAdmin(CompareVersionAdmin):
    pass


admin.site.register(Car, CarAdmin)


class PersonAdmin(CompareVersionAdmin):
    pass


admin.site.register(Person, PersonAdmin)


class PetAdmin(CompareVersionAdmin):
    pass


admin.site.register(Pet, PetAdmin)


class VariantModelAdmin(CompareVersionAdmin):
    pass


admin.site.register(VariantModel, VariantModelAdmin)


class CustomModelAdmin(CompareVersionAdmin):
    pass


admin.site.register(CustomModel, CustomModelAdmin)

admin.site.register(Identity, CustomModelAdmin)


class TemplateFieldModelAdmin(CompareVersionAdmin):
    pass


admin.site.register(TemplateField, TemplateFieldModelAdmin)


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
