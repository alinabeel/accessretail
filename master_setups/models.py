from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError

from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from core.mixinsModels import UpperCaseCharField,CodeNameMixIn,CreateUpdateMixIn
# from master_data.models import Upload

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


class UserIndex(CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_index = models.ManyToManyField(IndexSetup)

    def get_user_indexes(self):
        return ", ".join([a.code for a in self.user_index.all()])

    def get_user_indexe_list(self):
        ui ={a.code:a.name for a in self.user_index.all()}
        return ui

    def __str__(self):
        return str('{0} :: {1} :: {2}'.format(self.country, self.user.email, self.user_index))

    class Meta:
        unique_together = (('country', 'user',))
        db_table = 'user_index'
        verbose_name = 'User Index'
        verbose_name_plural = 'User Indexes'

class Threshold(CreateUpdateMixIn, models.Model):
    country = models.OneToOneField(Country, on_delete=models.CASCADE,unique = True)
    audited_data_purchase_min= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='-10')
    audited_data_purchase_max= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='10')

    audited_data_stock_min= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='-10')
    audited_data_stock_max= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='10')

    audited_data_price_min= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='-10')
    audited_data_price_max= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='10')


    audited_data_sales_min= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='-10')
    audited_data_sales_max= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='10')

    outlet_factor_numaric_min= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='0')
    outlet_factor_numaric_max= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='1')
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



