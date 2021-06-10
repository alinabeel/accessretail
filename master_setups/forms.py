from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField,UserChangeForm
from mptt.forms import TreeNodeChoiceField

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit

from django.contrib.auth.models import User
from master_setups.models import *

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
            'index_setup',
            'category',

        )


class UploadModalForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = (
            'import_mode',
            'file'
        )

class CategoryListFormHelper(FormHelper):
    model = Category
    form_tag = False
    form_method = 'GET'
    layout = Layout(
        'name',
        Submit('submit', 'Filter'),
    )
class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name','code', 'parent', 'description', 'is_active', )



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
        fields = ('audited_data_purchase_min', 'audited_data_purchase_max', 'audited_data_stock_min', 'audited_data_stock_max', 'audited_data_price_min', 'audited_data_price_max', 'audited_data_sales_min', 'audited_data_sales_max', 'outlet_factor_numaric_min', 'outlet_factor_numaric_max', )


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


