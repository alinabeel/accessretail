from django.db import models
from django.core import validators

class UpperCaseCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        if value:
            value = value.upper()
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(self.__class__, self).pre_save(model_instance, add)

class CodeNameMixIn(models.Model):
    name = models.CharField(max_length=150)
    code = UpperCaseCharField(max_length=50,validators=[validators.validate_slug])

    class Meta:
        abstract = True

    def __str__(self):
        return self.code


class CreateUpdateMixIn(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True
