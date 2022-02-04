from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField,UserChangeForm
from mptt.forms import TreeNodeChoiceField

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit

from django.contrib.auth.models import User
from master_setups.models import *
from master_data.models import *

User = get_user_model()

class UserCreateModelForm(UserCreationForm):
    email = forms.EmailField()
    username = UsernameField
    class Meta:
        model = User
        fields = [
            'email', 'password1', 'password2','role',
            'first_name', 'last_name','phone_no','city','state','zip','country',
            'is_active', 'is_superuser',
        ]

class UserChangeModelForm(UserChangeForm):
    email = forms.EmailField()
    username = UsernameField
    class Meta:
        model = User
        fields = [
            'email','password','role',
            'first_name', 'last_name','phone_no','city','state','zip','country',
            'is_active', 'is_superuser',
        ]

class CountryModelForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = (
            'code',
            'name',
        )

class IndexSetupModelForm(forms.ModelForm):
    class Meta:
        model = IndexSetup
        fields = (
            'name',
            'code',
            'description',
            'is_active',
        )

class IndexCategoryModelForm(forms.ModelForm):
    class Meta:
        model = IndexCategory
        fields = (
            'index',
            'category',

        )

class UserIndexModelForm(forms.ModelForm):
    class Meta:
        model = UserIndex
        fields = (
            'user',
            'user_index',
        )



class UserCountryModelForm(forms.ModelForm):
    # user = forms.MultipleChoiceField(choices=Country.objects.all(), widget=forms.CheckboxSelectMultiple())

    class Meta:
        model = UserCountry
        fields = (
            'user',
        )
        user = forms.ModelMultipleChoiceField(
                queryset=UserCountry.objects.all(),
                widget=forms.CheckboxSelectMultiple
            )
class ThresholdModelForm(forms.ModelForm):
    class Meta:
        model = Threshold
        # fields = (
        #         'audited_data_purchase_min', 'audited_data_purchase_max',
        #         'audited_data_stock_min', 'audited_data_stock_max',
        #         'audited_data_price_min', 'audited_data_price_max',
        #         'audited_data_sales_min', 'audited_data_sales_max',
        #         'outlet_factor_numaric_min', 'outlet_factor_numaric_max',
        #         )

        fields = ('audited_data_purchase_min',
            'audited_data_purchase_max',
            'audited_data_sales_min',
            'audited_data_sales_max',
            'audited_data_stock_min',
            'audited_data_stock_max',
            'audited_data_price_min',
            'audited_data_price_max',
            'audited_data_stddev',
            'stddev_sample',
            'common_outlet_accept',
            'new_outlet_accept_a',
            'new_outlet_drop_a',
            'new_outlet_accept_b',
            'new_outlet_drop_b',
            'drop_outlet_copy_once_status',
            'weighted_store',
            'weighted_cell',
            )
class RegionTypeModelForm(forms.ModelForm):
    class Meta:
        model = RegionType
        fields = ('name',)
        # parent = TreeNodeChoiceField(queryset=Region.objects.all().filter(country__code='NP'))



class RegionModelForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        self.country_code = kwargs.pop('country_code')
        super (RegionModelForm,self ).__init__(*args,**kwargs) # populates the post
        # instance = kwargs.get('instance')
        self.fields['parent'].queryset = Region.objects.filter(country__code = self.country_code)

    def clean_code(self):
        code = self.cleaned_data.get('code')
        # if (code == ''):
        #     raise forms.ValidationError('This field cannot be left blank')
        # for instance in Region.objects.filter(country__code = self.country_code):
        #     if instance.code == code:
        #         raise forms.ValidationError(code + ' is already exist.')
        return code

    class Meta:
        model = Region
        fields = ('name','code', 'region_type', 'parent', 'description')
        # parent = TreeNodeChoiceField(queryset=Region.objects.all().filter(country__code='NP'))


class MonthModelForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        self.country_code = kwargs.pop('country_code')
        super (self.__class__,self ).__init__(*args,**kwargs) # populates the post

    def clean(self):
        data = self.cleaned_data
        code = data.get('code')
        name = data.get('name')
        year = data.get('year')

        todays_date = date.today()
        current_year = todays_date.year

        if (code == '' or name == ''):
            raise forms.ValidationError('This field cannot be left blank')

        if (len(str(year)) < 4 or len(str(year)) > 4 ):
             raise forms.ValidationError({'year': 'year must be 4 digt long'})
        if (year > current_year):
             raise forms.ValidationError({'year': 'year must be less than or equal to current year'})

        if self.instance.pk is None:  # adding new value
            for instance in Month.objects.filter(country__code = self.country_code):
                if instance.code == code:
                    raise forms.ValidationError({'code': code + ' is already exist.'})
        else: #updating value
            for instance in Month.objects.filter(country__code = self.country_code).exclude(pk = self.instance.pk):
                if instance.code == code:
                    raise forms.ValidationError({'code': code + ' is already exist.'})

        return data

    class Meta:
        model = Month
        fields = ('name','code','year','is_locked')

class ColLabelModelForm(forms.ModelForm):
    class Meta:
        model = ColLabel
        # fields = ('model_name','col_name','col_label')
        exclude = ('country',)

    def __init__(self, *args, **kwargs):
        super(ColLabelModelForm, self).__init__(*args, **kwargs)
        self.fields['model_name'].disabled = True
        self.fields['col_name'].disabled = True
