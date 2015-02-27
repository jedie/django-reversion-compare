# coding: UTF-8

from __future__ import unicode_literals, print_function

from django.test import TestCase

from .models import SimpleModel

class SimpleModelTest(TestCase):
    def test_textile(self):
        instance = SimpleModel.objects.create(text="foo bar!")
        self.assertEqual(instance.text, "foo bar!")
