from django.urls import path
from .views import *

app_name = "reports"


urlpatterns = [
    # """ Import Logs """
    path('<slug:country_code>/import-logs-ajax/', ImportsLogsListViewAjax.as_view(), name='import-logs-ajax'),
    path('<slug:country_code>/import-logs/', ImportsLogsListView.as_view(), name='import-logs'),

    # """ RBD """
    path('<slug:country_code>/rbd-list-ajax/', RBDListViewAjax.as_view(), name='rbd-list-ajax'),
    path('<slug:country_code>/rbd-list/', RBDListView.as_view(), name='rbd-list'),

    # """ Cell Summary """
    path('<slug:country_code>/cell-summary-ajax/<int:pk>/<str:cat>', CellSummaryAJAX.as_view(), name='cell-summary-ajax'),
    path('<slug:country_code>/cell-summary/<int:pk>', CellSummaryListView.as_view(), name='cell-summary'),

    # """ Cell Summary Overview """
    path('<slug:country_code>/cell-summary-overview-ajax/', CellSummaryOverviewAJAX.as_view(), name='cell-summary-overview-ajax'),
    path('<slug:country_code>/cell-summary-overview-list-view/', CellSummaryOverviewListView.as_view(), name='cell-summary-overview-list-view'),

    # """ Cell and Shop Inspection """
    path('<slug:country_code>/cell-shop-inspection-ajax/', CellShopInspectionAJAX.as_view(), name='cell-shop-inspection-ajax'),
    path('<slug:country_code>/cell-shop-inspection-list-view/', CellShopInspectionListView.as_view(), name='cell-shop-inspection-list-view'),

    # """ Client Reporting """
    path('<slug:country_code>/client-reporting-view/', ClientReportingView.as_view(), name='client-reporting-view'),

    # """ Sample Maintenance """
    path('<slug:country_code>/sample-maintenance/', SampleMaintenanceView.as_view(), name='sample-maintenance'),



]
