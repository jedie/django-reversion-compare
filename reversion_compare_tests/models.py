"""
    models
    ~~~~~~

    All example models would be used for django-reversion-compare unittests, too.

    :copyleft: 2012-2022 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import dataclasses

from django.conf import settings
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django_countries.fields import CountryField
from django_tools.file_storage.file_system_storage import OverwriteFileSystemStorage
from reversion import revisions


class SimpleModel(models.Model):
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"SimpleModel pk: {self.pk!r} text: {self.text!r}"


class MigrationModel(models.Model):
    """
    Test model for "incompatible version data" fallback.
    See:
    https://github.com/jedie/django-reversion-compare/issues/148

    The model will be filled in migrations!
    """
    info = models.CharField(
        max_length=255,
        help_text='This field never changed and contains info about migration/version'
    )
    # number_then_text = models.CharField(
    #     max_length=32,
    #     help_text='migrate between CharField -> IntegerField -> CharField'
    # )
    number_then_text = models.IntegerField(
        help_text='migrate between CharField -> IntegerField -> CharField'
    )

    # text = models.TextField(
    #     help_text='TextField -> CharField(max_length=128) -> CharField(max_length=64)'
    # )
    text = models.CharField(
        max_length=128,
        help_text='TextField -> CharField(max_length=128) -> CharField(max_length=64)'
    )
    # text = models.CharField(
    #     max_length=64,
    #     help_text='TextField -> CharField(max_length=128) -> CharField(max_length=64)'
    # )

    def __str__(self):
        return f"MigrationModel pk: {self.pk!r} text: {self.text!r}"

# ------------------------------------------------------------------------------


"""
models with relationships

Factory & Car would be only registered in admin.py
so no relation data would be stored

Person & Pet would be registered here with the follow information, so that
related data would be also stored in django-reversion

see "Advanced model registration" here:
    https://github.com/etianen/django-reversion/wiki/Low-level-API
"""


class Building(models.Model):
    address = models.CharField(max_length=128)

    def __str__(self):
        return self.address


class Factory(Building):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Car(models.Model):
    name = models.CharField(max_length=128)
    manufacturer = models.ForeignKey(Factory, related_name="cars", on_delete=models.CASCADE)
    supplier = models.ManyToManyField(Factory, related_name="suppliers", blank=True)

    def __str__(self):
        return (
            f"{self.name} from {self.manufacturer}"
            f" supplier(s): {', '.join(s.name for s in self.supplier.all())}"
        )


class Pet(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(max_length=100)
    pets = models.ManyToManyField(Pet, blank=True)
    # If you work someone, its at a build, but maybe not a factory!
    workplace = models.ForeignKey(Building, related_name="workers", null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Identity(models.Model):
    id_numer = models.CharField(max_length=100)
    person = models.OneToOneField(Person, related_name="_identity", on_delete=models.CASCADE)

    def __str__(self):
        return self.id_numer


revisions.register(Person, follow=["pets"])
revisions.register(Pet)


class VariantModel(models.Model):
    """
    This model should contain all variants of all existing types,
    without the related fields.

    TODO: Add reversion_compare_tests for all variants!
    """

    TEST_CHOICES = (("a", "alpha"), ("b", "bravo"))
    boolean = models.BooleanField(default=True)
    null_boolean = models.BooleanField(null=True)

    char = models.CharField(max_length=1, blank=True, null=True)
    choices_char = models.CharField(max_length=1, blank=True, null=True, choices=TEST_CHOICES)
    text = models.TextField(blank=True, null=True)
    # skip: models.SlugField()

    integer = models.IntegerField(blank=True, null=True)
    integers = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=64, blank=True, null=True
    )
    positive_integer = models.PositiveIntegerField(blank=True, null=True)
    big_integer = models.BigIntegerField(blank=True, null=True)
    # skip:
    # models.PositiveSmallIntegerField()
    # models.SmallIntegerField()

    time = models.TimeField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)

    decimal = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    float = models.FloatField(blank=True, null=True)

    email = models.EmailField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    file_field = models.FileField(storage=OverwriteFileSystemStorage(create_backups=False), blank=True, null=True)

    filepath = models.FilePathField(path=settings.MEDIA_ROOT, blank=True, null=True)

    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"VariantModel instance pk: {self.pk:d}"


class CustomModel(models.Model):
    """Model which uses a custom version manager."""

    text = models.TextField()


class TemplateField(models.Model):
    """VersionAdmin in django-reversion has field compare_template that is str
    Model used for check correct handling this case
    Should be used ForeignKey for calling mixins.CompareMixin._get_compare_func
    """

    # some field for easy creating revisions
    text = models.CharField(max_length=20)
    template = models.ForeignKey(Person, blank=True, null=True, on_delete=models.CASCADE)


class CountryFieldTestModel(models.Model):
    # Test with model fields from https://github.com/SmileyChris/django-countries
    one_country = CountryField()
    multiple_countries = CountryField(multiple=True)
