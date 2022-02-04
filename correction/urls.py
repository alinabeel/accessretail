from django.urls import path
from .views import *

app_name = "correction"

""" Audit Data """
urlpatterns = [
    path('<slug:country_code>/audit-data-list-ajax/', AuditDataListViewAjax.as_view(), name='audit-data-list-ajax'),
    path('<slug:country_code>/audit-data-list/', AuditDataListView.as_view(), name='audit-data-list'),
]


""" Panel profile child """
urlpatterns += [
    path('<slug:country_code>/panel-profile-list-ajax/', PanelProfileListViewAjax.as_view(), name='panel-profile-list-ajax'),
    path('<slug:country_code>/panel-profile-list/', PanelProfileListView.as_view(), name='panel-profile-list'),
]


""" Inspection Summery """
urlpatterns += [
    path('<slug:country_code>/inspection-summery/', InspectionSummeryView.as_view(), name='inspection-summery'),
]
