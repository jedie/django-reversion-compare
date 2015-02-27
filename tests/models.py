from django.db import models
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class SimpleModel(models.Model):
    text = models.CharField(max_length=255)
    def __str__(self):
        return "SimpleModel pk: %r text: %r" % (self.pk, self.text)