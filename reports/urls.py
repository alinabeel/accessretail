from django.urls import path
from .views import *

app_name = "reports"


urlpatterns = [
    # """ Import Logs """
    path('<slug:country_code>/import-logs-ajax/', ImportsLogsListViewAjax.as_view(), name='import-logs-ajax'),
    path('<slug:country_code>/import-logs/', ImportsLogsListView.as_view(), name='import-logs'),

    # """ CellSummaryReportView """
    path('<slug:country_code>/cell-summary-generate-report-ajax/', CellSummaryGenerateReportAjax.as_view(), name='cell-summary-generate-report-ajax'),
    path('<slug:country_code>/cell-summary-report-ajax/', CellSummaryReportViewAjax.as_view(), name='cell-summary-report-ajax'),
    path('<slug:country_code>/cell-summary-report/', CellSummaryReportView.as_view(), name='cell-summary-report'),

    # """ Cell Summary """
    # path('<slug:country_code>/cell-summary-report/<int:pk>/', CellSummaryAJAX.as_view(), name='cell-summary-ajax'),
    path('<slug:country_code>/cell-summary-report-final/<int:pk>', CellSummaryListView.as_view(), name='cell-summary-report-final'),

    # """ Cell Summary Overview """
    path('<slug:country_code>/cell-summary-overview-ajax/', CellSummaryOverviewAJAX.as_view(), name='cell-summary-overview-ajax'),
    path('<slug:country_code>/cell-summary-overview-list-view/', CellSummaryOverviewListView.as_view(), name='cell-summary-overview-list-view'),

    # """ Cell and Shop Inspection """
    path('<slug:country_code>/cell-shop-inspection-ajax/', CellShopInspectionAJAX.as_view(), name='cell-shop-inspection-ajax'),
    path('<slug:country_code>/cell-shop-inspection-list-view/', CellShopInspectionListView.as_view(), name='cell-shop-inspection-list-view'),

    # """ Client Reporting """
    path('<slug:country_code>/client-reporting-view/', ClientReportingView.as_view(), name='client-reporting-view'),

    # """ Sample Maintenance """
    path('<slug:country_code>/sample-maintenance-ajax/', SampleMaintenanceViewAjax.as_view(), name='sample-maintenance-ajax'),
    path('<slug:country_code>/sample-maintenance/', SampleMaintenanceView.as_view(), name='sample-maintenance'),
    path('<slug:country_code>/sample-maintenance-copy/', SampleMaintenanceCopyViewAjax.as_view(), name='sample-maintenance-copy'),
    path('<slug:country_code>/sample-maintenance-estimate/', SampleMaintenanceEstimateViewAjax.as_view(), name='sample-maintenance-estimate'),

]
