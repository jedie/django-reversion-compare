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


@admin.register(SimpleModel)
class SimpleModelAdmin(CompareVersionAdmin):
    pass


@admin.register(MigrationModel)
class MigrationModelAdmin(CompareVersionAdmin):
    pass


@admin.register(Factory)
class FactoryAdmin(CompareVersionAdmin):
    pass


@admin.register(Car)
class CarAdmin(CompareVersionAdmin):
    pass


@admin.register(Person)
class PersonAdmin(CompareVersionAdmin):
    pass


@admin.register(Pet)
class PetAdmin(CompareVersionAdmin):
    pass


@admin.register(VariantModel)
class VariantModelAdmin(CompareVersionAdmin):
    pass


@admin.register(CustomModel, Identity)
class CustomModelAdmin(CompareVersionAdmin):
    pass


@admin.register(TemplateField)
class TemplateFieldModelAdmin(CompareVersionAdmin):
    pass


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
