from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db.models import Manager, Q
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey

from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from datetime import date, timezone
from core.mixinsModels import *


# from django.contrib.auth import get_user_model
# UserModel = get_user_model()


class User(AbstractUser):
    COUNTRYMANAGER = '1'
    MANAGER = '2'
    SUPERWISER = '3'
    AUDITOR = '4'

    ROLE_CHOICES = [
      (COUNTRYMANAGER, 'Country Manager'),
      (MANAGER, 'Manager'),
      (SUPERWISER, 'Superwiser'),
      (AUDITOR, 'Auditor'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES,default=COUNTRYMANAGER)
    username = models.CharField(max_length = 50, blank = True, null = True, unique = True)
    email = models.CharField(max_length = 50, unique = True)
    city = models.CharField(max_length = 50,blank = True, null = True,)
    state = models.CharField(max_length = 50,blank = True, null = True,)
    zip = models.CharField(max_length = 50,blank = True, null = True,)
    country = models.CharField(max_length = 50,blank = True, null = True,)
    phone_no = models.CharField(max_length = 50,blank = True, null = True,)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name', 'last_name']
    def __str__(self):
        return '{0} {1}({2})'.format(self.first_name, self.last_name,self.email)

    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Country(CreateUpdateMixIn, models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return str('{0}, {1}'.format(self.code, self.name))
    class Meta:
        db_table = 'country'
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('master-setups:country-list',
                       kwargs={
                           'country_code': self.code
                       })
    def get_data_import_url(self):
        return reverse('master-setups:country-list',
                       kwargs={
                           'country_code': self.code
                       })
    def get_country_list_url(self):
        return reverse('master-setups:country-list',
                       kwargs={
                           'country_code': self.code
                       })

def handle_upload_logs(instance, filename):
    return f"masterdata/{instance.country.code}/{instance.frommodel}/{filename}"

class Upload(CreateUpdateMixIn, models.Model):

    APPEND = 'APPEND'
    APPENDUPDATE = 'APPENDUPDATE'
    COPY = 'COPY'

    CHOICES = [
      (APPEND, 'Append: Add records in the table.'),
      (APPENDUPDATE, 'Append/Update: If  records exist update otherwise add.'),
      (COPY, 'Copy: Delete all records and repopulate from the source.'),
    ]

    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ERROR = "ERROR"

    IS_PROCESSING_CHOICES = [
        (UPLOADING, 'Uploading'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Completed'),
        (ERROR, 'Error'),
    ]

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    import_mode = models.CharField(max_length=20, choices=CHOICES)
    frommodel = models.CharField(max_length=50)
    file = models.FileField(upload_to=handle_upload_logs)
    is_processing = models.CharField(max_length=20, choices=IS_PROCESSING_CHOICES,blank=True, null=True)
    process_message = models.CharField(max_length=255, blank=True, null=True)
    skiped_records = models.IntegerField(blank=True, null=True)
    updated_records = models.IntegerField(blank=True, null=True)
    created_records = models.IntegerField(blank=True, null=True)
    log = models.TextField(blank=True, null=True)

    def __str__(self):
        return str('{0} - {1}'.format(self.country.code, self.file))

    class Meta:
        db_table = 'upload'
        verbose_name = 'Upload'
        verbose_name_plural = 'Uploads'



class UserCountry(CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    user = models.ManyToManyField(User)

    def __str__(self):
        return str('user from {0}'.format( self.country.name))
        # return str('{0} from {1}'.format(self.user.email, self.get_role_display()))

    class Meta:
        db_table = 'user_country'
        verbose_name = 'UserCountry'
        verbose_name_plural = 'User Countries'



class RegionType(CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('country','name',),)
        db_table = 'region_type'
        verbose_name = 'Region Type'
        verbose_name_plural = 'Region Types'
        ordering = ['name']

class Region(CodeNameMixIn,CreateUpdateMixIn,MPTTModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, related_name="region_uplaod", on_delete=models.CASCADE, null=True, blank=True)
    region_type = models.ForeignKey(RegionType, on_delete=models.CASCADE,)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True,blank=True, related_name='child')
    description = models.TextField(blank=True,default='')
    order_insertion_by = ['name']

    class Meta:
        unique_together = (('country','code','parent',),)
        db_table = 'region'
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'
        ordering = ['name']

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class Category(CreateUpdateMixIn,CodeNameMixIn,MPTTModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, related_name="category_uploads", on_delete=models.CASCADE, null=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True,blank=True, related_name='child')
    description = models.TextField(blank=True,default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = (('country','parent', 'code',))
        db_table = 'category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class IndexSetup(CodeNameMixIn,CreateUpdateMixIn,models.Model):

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    description = models.TextField(max_length=300)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        # return str('{0}({1})'.format(self.name,self.code))
        return self.name

    class Meta:
        unique_together = (('country', 'code',))
        db_table = 'index_setup'
        verbose_name = 'Index Setup'
        verbose_name_plural = 'Index Setups'
        ordering = ['name']



class IndexCategory(CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    index_setup = models.ForeignKey(IndexSetup, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category)

    def __str__(self):
        return str('{0}'.format(self.index_setup.name))

    class Meta:
        db_table = 'index_category'
        verbose_name = 'Index Category'
        verbose_name_plural = 'Index Categries'


class OutletType(CodeNameMixIn,CreateUpdateMixIn,MPTTModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, null=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True,blank=True, related_name='child')
    urbanity = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True,  blank=True,default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = (('country','parent', 'code',))
        db_table = 'outlet_type'
        verbose_name = 'Outlet Type'
        verbose_name_plural = 'Outlet Types'
        ordering = ['name']

    def __str__(self):
        return self.name

class Outlet(CreateUpdateMixIn, models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    code = UpperCaseCharField(max_length=50,validators=[validators.validate_slug])
    insert_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.code
    class Meta:
        unique_together = (('country', 'code',))
        db_table = 'outlet'
        verbose_name = 'Outlet'
        verbose_name_plural = 'Outlets'




class UserIndex(CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_index = models.ManyToManyField(IndexSetup)

    def get_user_indexes(self):
        return ", ".join([a.code for a in self.user_index.all()])

    def __str__(self):
        return str('{0} :: {1}'.format(self.country, self.user.email))

    class Meta:
        unique_together = (('country', 'user',))
        db_table = 'user_index'
        verbose_name = 'User Index'
        verbose_name_plural = 'User Indexes'

class Threshold(CreateUpdateMixIn, models.Model):
    country = models.OneToOneField(Country, on_delete=models.CASCADE,unique = True)
    audited_data_purchase_min= models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True,default='-10')
    audited_data_purchase_max= models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True,default='10')

    audited_data_stock_min= models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True,default='-10')
    audited_data_stock_max= models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True,default='10')

    audited_data_price_min= models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True,default='-10')
    audited_data_price_max= models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True,default='10')


    audited_data_sales_min= models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True,default='-10')
    audited_data_sales_max= models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True,default='10')

    outlet_factor_numaric_min= models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True,default='0')
    outlet_factor_numaric_max= models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True,default='1')
    def __str__(self):
        return str('{0}'.format(self.country))

    class Meta:
        db_table = 'threshold'
        verbose_name = 'Threshold'
        verbose_name_plural = 'Thresholds'



class CountrySetting(CreateUpdateMixIn, models.Model):
    country = models.OneToOneField(Country, on_delete=models.CASCADE,unique = True)
    logo = models.ImageField(upload_to='logos',null=True,blank=True)
    timezone = models.CharField(max_length=50,null=True,blank=True)

    def __str__(self):
        return str('{0}'.format(self.country))

    class Meta:
        db_table = 'country_setting'
        verbose_name = 'Country Setting'
        verbose_name_plural = 'Country Settings'
        ordering = ['country']


