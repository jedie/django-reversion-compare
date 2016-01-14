# coding: utf-8

"""
    models
    ~~~~~~

    All example models would be used for django-reversion-compare unittests, too.

    :copyleft: 2012-2015 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals, print_function


import os
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

try:
    from reversion import revisions as reversion
except ImportError:
    import reversion



from django.db import models
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class SimpleModel(models.Model):
    text = models.CharField(max_length=255)
    def __str__(self):
        return "SimpleModel pk: %r text: %r" % (self.pk, self.text)

#------------------------------------------------------------------------------

"""
models with relationships

Factory & Car would be only registered in admin.py
so no relation data would be stored

Person & Pet would be registered here with the follow information, so that
related data would be also stored in django-reversion

see "Advanced model registration" here:
    https://github.com/etianen/django-reversion/wiki/Low-level-API
"""

@python_2_unicode_compatible
class Factory(models.Model):
    name = models.CharField(max_length=128)
    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Car(models.Model):
    name = models.CharField(max_length=128)
    manufacturer = models.ForeignKey(Factory, related_name="cars")
    supplier = models.ManyToManyField(Factory, related_name="suppliers", blank=True)
    def __str__(self):
        return "%s from %s supplier(s): %s" % (self.name, self.manufacturer, ", ".join([s.name for s in self.supplier.all()]))


@python_2_unicode_compatible
class Pet(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Person(models.Model):
    name = models.CharField(max_length=100)
    pets = models.ManyToManyField(Pet, blank=True)
    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Identity(models.Model):
    id_numer = models.CharField(max_length=100)
    person = models.OneToOneField(Person, related_name='_identity')
    def __str__(self):
        return self.id_numer

reversion.register(Person, follow=["pets"])
#reversion.register(Pet, follow=["person_set"])
reversion.register(Pet)


@python_2_unicode_compatible
class VariantModel(models.Model):
    """
    This model should contain all variants of all existing types,
    without the related fields.

    TODO: Add tests for all variants!
    """
    boolean = models.BooleanField(default=True)
    null_boolean = models.NullBooleanField()

    char = models.CharField(max_length=1, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    # skip: models.SlugField()

    integer = models.IntegerField(blank=True, null=True)
    integers = models.CommaSeparatedIntegerField(max_length=64, blank=True, null=True)
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

    filepath = models.FilePathField(
        path=settings.UNITTEST_TEMP_PATH,
        blank=True, null=True
    )

    ip_address = models.IPAddressField(blank=True, null=True)
    # skip: models.GenericIPAddressField()

    def __str__(self):
        return "VariantModel instance pk: %i" % self.pk

#------------------------------------------------------------------------------

class CustomModel(models.Model):
    "Model which uses a custom version manager."
    text = models.TextField()

"""

class ParentModel(models.Model):
    parent_name = models.CharField(max_length=255)
    def __str__(self):
        return self.parent_name


class ChildModel(ParentModel):
    child_name = models.CharField(max_length=255)
    file = models.FileField(upload_to="test", blank=True)
    genericrelatedmodel_set = GenericRelation("reversion_compare_test_app.GenericRelatedModel")

    def __str__(self):
        return u"%s > %s" % (self.parent_name, self.child_name)

    class Meta:
        verbose_name = _("child model")
        verbose_name_plural = _("child models")


class RelatedModel(models.Model):
    child_model = models.ForeignKey(ChildModel)
    related_name = models.CharField(max_length=255)
    file = models.FileField(upload_to="test", blank=True)

    def __str__(self):
        return self.related_name


class GenericRelatedModel(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.TextField()
    child_model = GenericForeignKey()
    generic_related_name = models.CharField(max_length=255)

    def __str__(self):
        return self.generic_related_name


class FlatExampleModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, blank=True, null=True)
    content = models.TextField(help_text="Here is a content text field and this line is the help text from the model field.")
    child_model = models.ForeignKey(ChildModel, blank=True, null=True)

"""


