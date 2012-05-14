# coding: utf-8

"""
    models
    ~~~~~~
    
    All example models would be used for django-reversion-compare unittests, too.

    :copyleft: 2012 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
import reversion


class SimpleModel(models.Model):
    text = models.CharField(max_length=255)
    def __unicode__(self):
        return "SimpleModel pk: %r text: %r" % (self.pk, self.text)

#------------------------------------------------------------------------------

"""
models with relationships

Manufacturer & Car would be registered in admin.py
Person & Pet would be registered here with the follow information, so that
related data would be also stored in django-reversion

see "Advanced model registration" here:
    https://github.com/etianen/django-reversion/wiki/Low-level-API
"""


class Manufacturer(models.Model):
    name = models.CharField(max_length=128)
    def __unicode__(self):
        return self.name

class Car(models.Model):
    name = models.CharField(max_length=128)
    manufacturer = models.ForeignKey(Manufacturer)
    def __unicode__(self):
        return self.name


class Pet(models.Model):
    name = models.CharField(max_length=100)
    def __unicode__(self):
        return self.name

class Person(models.Model):
    name = models.CharField(max_length=100)
    pets = models.ManyToManyField(Pet, blank=True)
    def __unicode__(self):
        return self.name

reversion.register(Person, follow=["pets"])
reversion.register(Pet, follow=["person_set"])

#------------------------------------------------------------------------------

"""

class ParentModel(models.Model):
    parent_name = models.CharField(max_length=255)
    def __unicode__(self):
        return self.parent_name


class ChildModel(ParentModel):
    child_name = models.CharField(max_length=255)
    file = models.FileField(upload_to="test", blank=True)
    genericrelatedmodel_set = GenericRelation("reversion_compare_test_app.GenericRelatedModel")

    def __unicode__(self):
        return u"%s > %s" % (self.parent_name, self.child_name)

    class Meta:
        verbose_name = _("child model")
        verbose_name_plural = _("child models")


class RelatedModel(models.Model):
    child_model = models.ForeignKey(ChildModel)
    related_name = models.CharField(max_length=255)
    file = models.FileField(upload_to="test", blank=True)

    def __unicode__(self):
        return self.related_name


class GenericRelatedModel(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.TextField()
    child_model = GenericForeignKey()
    generic_related_name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.generic_related_name


class FlatExampleModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, blank=True, null=True)
    content = models.TextField(help_text="Here is a content text field and this line is the help text from the model field.")
    child_model = models.ForeignKey(ChildModel, blank=True, null=True)

"""


