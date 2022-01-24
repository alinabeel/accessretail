from django.urls import path
from .views import *

app_name = "correction"

""" Audit Data """
urlpatterns = [
    path('<slug:country_code>/audit-data-list-ajax/', AuditDataListViewAjax.as_view(), name='audit-data-list-ajax'),
    path('<slug:country_code>/audit-data-list/', AuditDataListView.as_view(), name='audit-data-list'),
]
