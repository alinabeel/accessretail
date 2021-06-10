from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from master_setups.models import *

from django_mptt_admin.admin import DjangoMpttAdmin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


from import_export.admin import ImportExportModelAdmin


# from custom_field.custom_field import CustomFieldAdmin
# class CFAdmin(CustomFieldAdmin):
#     list_display = ("content_type", "name")
#     list_filter = ("content_type",)
#     search_fields = ("content_type__name", "name")


@admin.register(User)
class UserAdmin(BaseUserAdmin,ImportExportModelAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    fieldsets = (
        (None, {'fields': ('email', 'password', 'role')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name','phone_no','city','state','zip','country')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                        'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),

    )
    add_fieldsets = (
        (None, {'classes': ('wide', ),'fields': ('email', 'password1', 'password2','role'),}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',)}),
        (_('Personal info'), {'fields': ('first_name', 'last_name','phone_no','city','state','zip','country')}),

    )
    list_display = ['email', 'first_name', 'last_name','phone_no','role','is_staff','is_superuser',]
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff','is_superuser')
    ordering = ('email', )


# class CountrySettingResource(resources.ModelResource):
#     class Meta:
#         model = CountrySetting

@admin.register(Threshold)
class ThresholdAdmin(ImportExportModelAdmin):
    # resource_class = CountrySettingResource
    fieldsets = (
        (None, {'classes': ('wide', ),'fields': ('country',),}),
        (_('Audited Data Threashold (in %)'), {'fields': (
            ('audited_data_purchase_min', 'audited_data_purchase_max'),
            ('audited_data_stock_min', 'audited_data_stock_max'),
            ('audited_data_price_min','audited_data_price_max'),
            ('audited_data_sales_min','audited_data_sales_max'),
            )}),
        (_('Outlet Factors Threashold (in %)'), {'fields': (('outlet_factor_numaric_min', 'outlet_factor_numaric_max'))}),
    )
@admin.register(CountrySetting)
class CountrySettingAdmin(ImportExportModelAdmin):
    # resource_class = CountrySettingResource
    fieldsets = (
        (None, {'classes': ('wide', ),'fields': ('country', 'logo',),}),
    )


@admin.register(UserCountry)
class UserCountryAdmin(ImportExportModelAdmin):
    search_fields = ['user','country' ]
    list_filter = ['country' ]
    list_display = ('country', )
    filter_horizontal = ['user', ]

@admin.register(UserIndex)
class UserIndexAdmin(ImportExportModelAdmin):
    search_fields = ['country', 'user', 'user_index']
    list_filter = ['country',  ]
    list_display = ('country', 'user','get_user_indexes')
    filter_horizontal = ['user_index', ]

@admin.register(IndexSetup)
class IndexSetupAdmin(ImportExportModelAdmin):
    search_fields = ['country', 'code', 'name']
    list_filter = ['country',  'is_active']
    list_display = ('code', 'name', 'is_active')


admin.site.register(Country,ImportExportModelAdmin)




# admin.site.register(User, UserAdmin)
# admin.site.register(CountrySetting,CountrySettingAdmin)
# admin.site.register(UserCountry,UserCountryAdmin)
# admin.site.register(UserIndex,UserIndexAdmin)
# admin.site.register(IndexSetup,IndexSetupAdmin)
