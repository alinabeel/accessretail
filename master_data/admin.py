from django.contrib import admin
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget

from master_setups.models import *
from master_data.models import *
from import_export.admin import ImportExportModelAdmin


# Register your models here.


@admin.register(Census)
class CensusAdmin(admin.ModelAdmin):
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
#     list_display = ['town_name', 'name_of_outlet', 'name_of_respondent', 'respondent_status_of_the_store', 'shop_no', 'floor_no', 'building_name_available', 'building_name', 'street_name_available', 'street_name', ]
#     list_filter = ('country', 'town_name')
#     search_fields = ('town_name', 'name_of_outlet', 'name_of_respondent', 'respondent_status_of_the_store', 'shop_no', 'floor_no', 'building_name_available', 'building_name', 'street_name_available', 'street_name', )
#     ordering = ('country','town_name' )

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ['code', 'name','country']
    list_filter = ['country',  ]
    search_fields = ('code', 'name', 'country')
    ordering = ('country','code' )


@admin.register(IndexCategory)
class IndexCategoryAdmin(ImportExportModelAdmin):
    search_fields = ['country', 'index', 'category']
    list_filter = ['index',  ]
    list_display = ('index','country',)
    # filter_horizontal = ['category', ]
