from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.fields import BooleanField
from core.mixinsModels import UpperCaseCharField,CodeNameMixIn,CreateUpdateMixIn
from master_setups.models import Country, IndexSetup, User
from master_data.models import Month,RBD,Category


class RBDReport(CreateUpdateMixIn,models.Model):
    CELLSUMMARY = 'cell-summary'
    CELLSNAPSHOT = 'cell-snapshot'

    REPORTTYPE_CHOICES = (
        (CELLSUMMARY , 'Cell Summary'),
        (CELLSNAPSHOT , 'Cell Snapshot'),
    )

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(null=True, blank=True, max_length=500,)
    rbd = models.ForeignKey(RBD, on_delete=models.CASCADE)
    index = models.ForeignKey(IndexSetup, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=50, choices=REPORTTYPE_CHOICES,default=CELLSUMMARY)
    report_html = models.TextField(null=True, blank=True)
    report_json = JSONField(null=True, blank=True)
    report_csv_source = models.CharField(null=True, blank=True, max_length=500,)


    is_confirmed = models.BooleanField(default=False)
    confirmed_on = models.DateField(null=True, blank=True)
    confirmed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT,related_name='rbd_confirmed_by_set')

    is_generated = models.SmallIntegerField(default=0)
    generated_on = models.DateField(null=True, blank=True)
    generated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT,related_name='rbd_generated_by_set')

    log = models.TextField(null=True, blank=True)

    class Meta:
        # unique_together = (('country','rbd'))
        db_table = 'rbd_report'
        verbose_name = 'RBDReport'
        verbose_name_plural = 'RBDReports'

    def __str__(self):
        return self.rbd.name



