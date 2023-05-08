"""
    admin
    ~~~~~

    All example admin classes would be used in django-reversion-compare unittests, too.

    :copyleft: 2012-2015 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin
from reversion_compare_project.models import (
    Car,
    CountryFieldTestModel,
    CustomModel,
    Factory,
    Identity,
    MigrationModel,
    NotRegisteredModel,
    Person,
    Pet,
    RegisteredWithNotRegisteredRelationModel,
    SimpleModel,
    TemplateField,
    VariantModel,
)


class SimpleModelAdmin(CompareVersionAdmin):
    pass


admin.site.register(SimpleModel, SimpleModelAdmin)


class MigrationModelAdmin(CompareVersionAdmin):
    pass


admin.site.register(MigrationModel, MigrationModelAdmin)


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


@admin.register(CountryFieldTestModel)
class CountryFieldTestModelAdmin(CompareVersionAdmin):
    pass


####################################################################################################


@admin.register(RegisteredWithNotRegisteredRelationModel)
class RegisteredWithNotRegisteredRelationModelAdmin(CompareVersionAdmin):
    pass


@admin.register(NotRegisteredModel)
class NotRegisteredModelModelAdmin(admin.ModelAdmin):
    pass
