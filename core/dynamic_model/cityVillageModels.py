from django.db import models

class CityVillageMixIn(models.Model):
    # extra_100 =  models.CharField(max_length=500, null=True, blank=True)
    class Meta:
        abstract = True
