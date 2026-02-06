import djadmin

from reversion_compare.mixins import CompareMethodsMixin, CompareMixin
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


class DjAdminCompareVersionAdmin(CompareMethodsMixin, CompareMixin, djadmin.ModelAdmin):
    pass


@djadmin.register(SimpleModel)
class SimpleModelAdmin(DjAdminCompareVersionAdmin):
    pass


@djadmin.register(MigrationModel)
class MigrationModelAdmin(DjAdminCompareVersionAdmin):
    pass


@djadmin.register(Factory)
class FactoryAdmin(DjAdminCompareVersionAdmin):
    pass


@djadmin.register(Car)
class CarAdmin(DjAdminCompareVersionAdmin):
    pass


@djadmin.register(Person)
class PersonAdmin(DjAdminCompareVersionAdmin):
    pass


@djadmin.register(Pet)
class PetAdmin(DjAdminCompareVersionAdmin):
    pass


@djadmin.register(VariantModel)
class VariantModelAdmin(DjAdminCompareVersionAdmin):
    pass


@djadmin.register(CustomModel, Identity)
class CustomModelAdmin(DjAdminCompareVersionAdmin):
    pass


@djadmin.register(TemplateField)
class TemplateFieldModelAdmin(DjAdminCompareVersionAdmin):
    pass


@djadmin.register(CountryFieldTestModel)
class CountryFieldTestModelAdmin(DjAdminCompareVersionAdmin):
    pass


####################################################################################################


@djadmin.register(RegisteredWithNotRegisteredRelationModel)
class RegisteredWithNotRegisteredRelationModelAdmin(DjAdminCompareVersionAdmin):
    pass


@djadmin.register(NotRegisteredModel)
class NotRegisteredModelModelAdmin(djadmin.ModelAdmin):
    pass


print('djadmin registered')
