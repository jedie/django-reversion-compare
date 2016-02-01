#!/usr/bin/env python
# coding: utf-8

"""
    django-reversion-compare unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    I used the setup from reversion_compare_test_project !

    TODO:
        * models.OneToOneField()
        * models.IntegerField()

    :copyleft: 2012 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import unicode_literals, print_function

import datetime
import os
from decimal import Decimal
from django.conf import settings

from django.contrib.auth.models import User
from django.db.models import BigIntegerField

try:
    import django_tools
except ImportError as err:
    msg = (
        "Please install django-tools for unittests"
        " - https://github.com/jedie/django-tools/"
        " - Original error: %s"
    ) % err
    raise ImportError(msg)

try:
    from reversion import revisions as reversion
except ImportError:
    import reversion


from tests.models import SimpleModel, Person, Pet, \
    Factory, Car, VariantModel, CustomModel, Identity



class TestData(object):
    """
    Collection of all test data creation method.
    This will be also used from external scripts, too!
    """

    TEST_USERNAME="test"
    TEST_USERPASS="12345678"

    def __init__(self, verbose=False):
        self.verbose = verbose

    def create_all(self):
        """
        simple call all create_*_data() methods
        """
        for method_name in dir(self):
            if method_name.startswith("create_") and method_name.endswith("_data"):
                if self.verbose:
                    print("_"*79)
                    print(" *** %s ***" % method_name)
                func = getattr(self, method_name)
                func()


    def create_testuser_data(self):
        if self.verbose:
            print("\t+++ user name.......: %r" % self.TEST_USERNAME)
            print("\t+++ user password...: %r" % self.TEST_USERPASS)
        self.user = User(username=self.TEST_USERNAME, is_staff=True, is_superuser=True)
        self.user.set_password(self.TEST_USERPASS)
        self.user.save()

    def create_Simple_data(self):
        with reversion.create_revision():
            item1 = SimpleModel.objects.create(text="version one")

        if self.verbose:
            print("version 1:", item1)

        with reversion.create_revision():
            item1.text = "version two"
            item1.save()
            reversion.set_comment("simply change the CharField text.")

        if self.verbose:
            print("version 2:", item1)

        for no in range(5):
            with reversion.create_revision():
                if no==0:
                    item2 = SimpleModel.objects.create(text="v0")
                    reversion.set_comment("create v%i" % no)
                else:
                    item2.text = "v%i" % no
                    item2.save()
                    reversion.set_comment("change to v%i" % no)

        return item1, item2

    def create_FactoryCar_data(self):
        with reversion.create_revision():
            manufacture = Factory.objects.create(name="factory one")
            supplier1 = Factory.objects.create(name="always the same supplier")
            supplier2 = Factory.objects.create(name="would be deleted supplier")
            supplier3 = Factory.objects.create(name="would be removed supplier")
            car = Car.objects.create(
                name="motor-car one",
                manufacturer=manufacture
            )
            car.supplier.add(supplier1, supplier2, supplier3)
            car.save()
            reversion.set_comment("initial version 1")

        if self.verbose:
            print("version 1:", car)
            # motor-car one from factory one supplier(s): always the same supplier, would be deleted supplier, would be removed supplier

        """ 1 to 2 diff:

        "manufacture" ForeignKey:
            "factory one" -> "factory I"

        "supplier" ManyToManyField:
            + new, would be renamed supplier
            - would be deleted supplier
            - would be removed supplier
            = always the same supplier
        """

        with reversion.create_revision():
            manufacture.name = "factory I"
            manufacture.save()
            supplier2.delete() # - would be deleted supplier
            supplier4 = Factory.objects.create(name="new, would be renamed supplier")
            car.supplier.add(supplier4) # + new, would be renamed supplier
            car.supplier.remove(supplier3) # - would be removed supplier
            car.save()
            reversion.set_comment("version 2: change ForeignKey and ManyToManyField.")

        if self.verbose:
            print("version 2:", car)
            # motor-car one from factory I supplier(s): always the same supplier, new, would be renamed supplier

        """ 2 to 3 diff:

        "name" CharField:
            "motor-car one" -> "motor-car II"

        "manufacture" ForeignKey:
            "factory I" -> "factory II"

        "supplier" ManyToManyField:
            new, would be renamed supplier -> not new anymore supplier
            = always the same supplier
        """

        with reversion.create_revision():
            car.name = "motor-car II"
            manufacture.name = "factory II"
            supplier4.name = "not new anymore supplier"
            supplier4.save()
            car.save()
            reversion.set_comment("version 3: change CharField, ForeignKey and ManyToManyField.")

        if self.verbose:
            print("version 3:", car)
            # version 3: motor-car II from factory II supplier(s): always the same supplier, not new anymore supplier

        return car

    def create_Factory_reverse_relation_data(self):
        from django.db import transaction

        with transaction.atomic(), reversion.create_revision():
            manufacturer = Factory.objects.create(name="factory one")
            different_manufacturer = Factory.objects.create(name="factory two")
            car1 = Car.objects.create(
                name="motor-car one",
                manufacturer=manufacturer
            )
            car2 = Car.objects.create(
                name="motor-car two",
                manufacturer=manufacturer
            )
            car3 = Car.objects.create(
                name="motor-car three",
                manufacturer=manufacturer
            )
            car1.save()
            car2.save()
            car3.save()
            manufacturer.save()
            reversion.set_comment("initial version 1")

        if self.verbose:
            print("version 1:", manufacturer)
            # Factory One

        """ 1 to 2 diff:

        "manufacture" ForeignKey:
            "factory one" -> "factory I"

        "supplier" ManyToManyField:
            + new, would be renamed supplier
            - would be deleted supplier
            - would be removed supplier
            = always the same supplier
        """

        with transaction.atomic(), reversion.create_revision():
            car3.delete()
            car4 = Car.objects.create(
                name="motor-car four",
                manufacturer=manufacturer
            )
            car4.save()
            manufacturer.save()
            reversion.set_comment("version 2: discontinued car-three, add car-four")

        if self.verbose:
            print("version 2:", manufacturer)
            # motor-car one from factory I supplier(s): always the same supplier, new, would be renamed supplier

        """ 2 to 3 diff:

        "name" CharField:
            "motor-car one" -> "motor-car II"

        "manufacture" ForeignKey:
            "factory I" -> "factory II"

        "supplier" ManyToManyField:
            new, would be renamed supplier -> not new anymore supplier
            = always the same supplier
        """

        with transaction.atomic(), reversion.create_revision():
            car2.manufacturer = different_manufacturer
            car2.save()
            manufacturer.save()
            reversion.set_comment("version 3: car2 now built by someone else.")

        if self.verbose:
            print("version 3:", manufacturer)
            # version 3: motor-car II from factory II supplier(s): always the same supplier, not new anymore supplier

        return manufacturer


    def create_PersonPet_data(self):
        with reversion.create_revision():
            pet1 = Pet.objects.create(name="would be changed pet")
            pet2 = Pet.objects.create(name="would be deleted pet")
            pet3 = Pet.objects.create(name="would be removed pet")
            pet4 = Pet.objects.create(name="always the same pet")
            person = Person.objects.create(name="Dave")
            person.pets.add(pet1, pet2, pet3, pet4)
            person.save()
            reversion.set_comment("initial version 1")

        if self.verbose:
            print("version 1:", person, person.pets.all())
            # Dave [<Pet: would be changed pet>, <Pet: would be deleted pet>, <Pet: would be removed pet>, <Pet: always the same pet>]

        """ 1 to 2 diff:

        "pets" ManyToManyField:
            would be changed pet -> Is changed pet
            - would be removed pet
            - would be deleted pet
            = always the same pet
        """

        with reversion.create_revision():
            pet1.name = "Is changed pet"
            pet1.save()
            pet2.delete()
            person.pets.remove(pet3)
            person.save()
            reversion.set_comment("version 2: change follow related pets.")

        if self.verbose:
            print("version 2:", person, person.pets.all())
            # Dave [<Pet: Is changed pet>, <Pet: always the same pet>]

        return pet1, pet2, person

    def create_VariantModel_data(self):
        with reversion.create_revision():
            item = VariantModel.objects.create(
                boolean = False,
                null_boolean = None,

                char = "a",
                text = "Foo 'one'",
                # skip: models.SlugField()

                integer = 0,
                integers = "1,2,3", # CommaSeparatedIntegerField
                positive_integer = 1,
                big_integer = (-BigIntegerField.MAX_BIGINT - 1),
                # skip:
                # models.PositiveSmallIntegerField()
                # models.SmallIntegerField()

                time = datetime.time(hour=20, minute=15),
                date = datetime.date(year=1941, month=5, day=12), # Z3 was presented in germany ;)
                # PyLucid v0.0.1 release date:
                datetime = datetime.datetime(year=2005, month=8, day=19, hour=8, minute=13, second=24),

                decimal = Decimal('1.23456789'),
                float = 2.345,

                email = "one@foo-bar.com",
                url = "http://www.pylucid.org/",

                filepath = os.path.join(settings.UNITTEST_TEMP_PATH, "foo"),

                ip_address = "192.168.0.1",
                # skip: models.GenericIPAddressField()
            )
            reversion.set_comment("initial version")

        test_data = (
            ("boolean", True),
            ("null_boolean", False),
            ("char", "B"),
            ("text", "Bar 'two'"),
            # skip: models.SlugField()
            ("integer", -1),
            ("integers", "2,3,4"), # CommaSeparatedIntegerField
            ("positive_integer", 3),
            ("big_integer", BigIntegerField.MAX_BIGINT),
            # models.PositiveSmallIntegerField()
            # models.SmallIntegerField()
            ("time", datetime.time(hour=19, minute=30)),
            ("date", datetime.date(year=2099, month=12, day=31)),
            ("datetime", datetime.datetime(year=2000, month=1, day=1, hour=0, minute=0, second=1)),
            ("decimal", Decimal('3.1415926535')),
            ("float", 3.1415),
            ("email", "two@foo-bar.com"),
            ("url", "https://github.com/jedie/"),
            ("filepath", os.path.join(settings.UNITTEST_TEMP_PATH, "bar")),
            ("ip_address", "10.0.0.0"),
        )
        for no, (field_name, value) in enumerate(test_data):
            with reversion.create_revision():
                setattr(item, field_name, value)
                item.save()
                reversion.set_comment("%i change: %r field." % (no, field_name))

        return item, test_data

    def create_CustomModel_data(self):
        with reversion.create_revision():
            item1 = CustomModel.objects.create(text="version one")

        if self.verbose:
            print("version 1:", item1)

        return item1


    def create_PersonIdentity_data(self):
        with reversion.create_revision():
            person = Person.objects.create(name="Dave")
            identity = Identity.objects.create(id_numer="1234", person=person)

        if self.verbose:
            print("version 1:", person, identity)

        with reversion.create_revision():
            person.name = "John"
            person.save()
            reversion.set_comment("version 2: change person name.")

        return person, identity

