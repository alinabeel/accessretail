from django.urls import path
from .views import *

app_name = "reports"


urlpatterns = [
    # """ Import Logs """
    path('<slug:country_code>/import-logs-ajax/', ImportsLogsListViewAjax.as_view(), name='import-logs-ajax'),
    path('<slug:country_code>/import-logs/', ImportsLogsListView.as_view(), name='import-logs'),

    # """ Cell Summary """
    # path('<slug:country_code>/cell-summary-list-api-view/', CellSummaryListAPIView.as_view(), name='cell-summary-list-api-view'),
    # path('<slug:country_code>/cell-summary-ajax/', CellSummaryAJAX.as_view(), name='cell-summary-ajax'),
    path('<slug:country_code>/cell-summary-ajax/', CellSummaryAJAX.as_view(), name='cell-summary-ajax'),
    path('<slug:country_code>/cell-summary-list-view/', CellSummaryListView.as_view(), name='cell-summary-list-view'),

    # """ RBD Summary """
    path('<slug:country_code>/rbd-summary-ajax/', RBDSummaryAJAX.as_view(), name='rbd-summary-ajax'),
    path('<slug:country_code>/rbd-summary-list-view/', RBDSummaryListView.as_view(), name='rbd-summary-list-view'),

    # """ RBD Summary Overview """
    path('<slug:country_code>/rbd-summary-overview-ajax/', RBDSummaryOverviewAJAX.as_view(), name='rbd-summary-overview-ajax'),
    path('<slug:country_code>/rbd-summary-overview-list-view/', RBDSummaryOverviewListView.as_view(), name='rbd-summary-overview-list-view'),

    # """ Cell Summary Overview """
    path('<slug:country_code>/cell-summary-overview-ajax/', CellSummaryOverviewAJAX.as_view(), name='cell-summary-overview-ajax'),
    path('<slug:country_code>/cell-summary-overview-list-view/', CellSummaryOverviewListView.as_view(), name='cell-summary-overview-list-view'),

    # """ Cell and Shop Inspection """
    path('<slug:country_code>/cell-shop-inspection-ajax/', CellShopInspectionAJAX.as_view(), name='cell-shop-inspection-ajax'),
    path('<slug:country_code>/cell-shop-inspection-list-view/', CellShopInspectionListView.as_view(), name='cell-shop-inspection-list-view'),

    # """ RBD and Shop Inspection """
    path('<slug:country_code>/rbd-shop-inspection-ajax/', RBDShopInspectionAJAX.as_view(), name='rbd-shop-inspection-ajax'),
    path('<slug:country_code>/rbd-shop-inspection-list-view/', RBDShopInspectionListView.as_view(), name='rbd-shop-inspection-list-view'),

    # """ Client Reporting """
    path('<slug:country_code>/client-reporting-view/', ClientReportingView.as_view(), name='client-reporting-view'),

]
