from django.contrib import admin
from master_setups.models import *
from monthly_setups_and_data.models import *
from import_export.admin import ImportExportModelAdmin

# @admin.register(OutletType)
# class OutletTypeAdmin(ImportExportModelAdmin):
#     search_fields = ['country', 'code', 'name']
#     list_filter = ['country',  ]
#     list_display = ('country', 'code','name')


# @admin.register(Outlet)
# class OutletAdmin(ImportExportModelAdmin):
#     search_fields = ['country', 'code', 'name', 'address', 'postal_code', 'area', 'district', 'city', 'village', 'provice', 'ward_number', 'phone', 'mobile', 'outlet_type', 'locality_type']
#     list_filter = ['country', 'postal_code', 'area', 'district', 'city', 'village', 'provice', 'ward_number', 'outlet_type', 'locality_type' ]
#     list_display = ('country', 'code', 'name', 'address', 'postal_code', 'area', 'district', 'city', 'village', 'provice', 'ward_number', 'phone', 'mobile', 'outlet_type', 'locality_type')

