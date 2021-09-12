from django.urls import path
from master_data.views import *

app_name = "master-data"

""" Census """
urlpatterns = [
    path('<slug:country_code>/census-list', CensusListView.as_view(), name='census-list'),
    path('<slug:country_code>/census-list-ajax', census_list_ajax, name='census-list-ajax'),
    path('<slug:country_code>/census-list-pivot', census_list, name='census-list-pivot'),

    path('<slug:country_code>/census-upload/', CensusUploadView.as_view(), name='census-upload'),

    path('<slug:country_code>/census-import/',import_census, name="census-import"),
    path('<slug:country_code>/census-detail/<int:pk>/', CensusDetailView.as_view(), name='census-detail'),
    path('<slug:country_code>/census-update/<int:pk>/', CensusUpdateView.as_view(), name='census-update'),
    path('<slug:country_code>/census-delete/<int:pk>/', CensusDeleteView.as_view(), name='census-delete'),

]
""" Category """
urlpatterns += [
    path('<slug:country_code>/category-list-ajax/', CategoryListViewAjax.as_view(), name='category-list-ajax'),
    path('<slug:country_code>/category-list/', CategoryListView.as_view(), name='category-list'),
    path('<slug:country_code>/category-create/', CategoryCreateView.as_view(), name='category-create'),
    path('<slug:country_code>/category-update/<int:pk>', CategoryUpdateView.as_view(), name='category-update'),
    path('<slug:country_code>/category-delete/<int:pk>', CategoryDeleteView.as_view(), name='category-delete'),
    path('<slug:country_code>/category-import/', CategoryImportView.as_view(), name='category-import'),
]

""" Outlet Type """
urlpatterns += [
    path('<slug:country_code>/outlet-type-list-ajax/', OutletTypeListViewAjax.as_view(), name='outlet-type-list-ajax'),
    path('<slug:country_code>/outlet-type-list/', OutletTypeListView.as_view(), name='outlet-type-list'),
    path('<slug:country_code>/outlet-type-create/', OutletTypeCreateView.as_view(), name='outlet-type-create'),
    path('<slug:country_code>/outlet-type-update/<int:pk>', OutletTypeUpdateView.as_view(), name='outlet-type-update'),
    path('<slug:country_code>/outlet-type-delete/<int:pk>', OutletTypeDeleteView.as_view(), name='outlet-type-delete'),
    path('<slug:country_code>/outlet-type-import/', OutletTypeImportView.as_view(), name='outlet-type-import'),
]


""" Panel Profile """
urlpatterns += [

    path('<slug:country_code>/panel-profile-list-ajax/', PanelProfileListViewAjax.as_view(), name='panel-profile-list-ajax'),
    path('<slug:country_code>/panel-profile-list/', PanelProfileListView.as_view(), name='panel-profile-list'),
    path('<slug:country_code>/panel-profile-import/', PanelProfileImportView.as_view(), name='panel-profile-import'),
    path('<slug:country_code>/panel-profile-update/', PanelProfileUpdateView.as_view(), name='panel-profile-update'),
]

""" Usable Outlets """
urlpatterns += [
    path('<slug:country_code>/usable-outlet-import/', UsableOutletImportView.as_view(), name='usable-outlet-import'),
    path('<slug:country_code>/usable-outlet-list-ajax/', UsableOutletListViewAjax.as_view(), name='usable-outlet-list-ajax'),
    path('<slug:country_code>/usable-outlet-list/', UsableOutletListView.as_view(), name='usable-outlet-list'),
    path('<slug:country_code>/usable-outlet-create/', UsableOutletCreateView.as_view(), name='usable-outlet-create'),
    path('<slug:country_code>/usable-outlet-update/<int:pk>', UsableOutletUpdateView.as_view(), name='usable-outlet-update'),
    path('<slug:country_code>/usable-outlet-delete/<int:pk>', UsableOutletDeleteView.as_view(), name='usable-outlet-delete'),

]

""" Product List """
urlpatterns += [
    path('<slug:country_code>/product-list-ajax/', ProductListViewAjax.as_view(), name='product-list-ajax'),
    path('<slug:country_code>/product-list/', ProductListView.as_view(), name='product-list'),
    path('<slug:country_code>/product-import/', ProductImportView.as_view(), name='product-import'),
]

""" Audit Data """
urlpatterns += [
    path('<slug:country_code>/product-audit-list-ajax/', ProductAuditListViewAjax.as_view(), name='product-audit-list-ajax'),
    path('<slug:country_code>/product-audit-list/', ProductAuditListView.as_view(), name='product-audit-list'),
    path('<slug:country_code>/product-audit-import/', ProductAuditImportView.as_view(), name='product-audit-import'),
]

""" RBD """
urlpatterns += [

    path('<slug:country_code>/panel-profile-rbd-list-json/', PanelProfileRBDListing.as_view(), name='panel-profile-rbd-list-json'),
    path('<slug:country_code>/panel-profile-rbd-list-json/<int:pk>', PanelProfileRBDListing.as_view(), name='panel-profile-rbd-list-json'),

    path('<slug:country_code>/rbd-list-ajax/', RBDListViewAjax.as_view(), name='rbd-list-ajax'),
    path('<slug:country_code>/rbd-list/', RBDListView.as_view(), name='rbd-list'),
    path('<slug:country_code>/rbd-create/', RBDCreateView.as_view(), name='rbd-create'),
    path('<slug:country_code>/rbd-update/<int:pk>', RBDUpdateView.as_view(), name='rbd-update'),
    path('<slug:country_code>/rbd-delete/<int:pk>', RBDDeleteView.as_view(), name='rbd-delete'),
]


""" CELL """
urlpatterns += [

    path('<slug:country_code>/cell-panel-profile-ajax/', CellPanelProfileAJAX.as_view(), name='cell-panel-profile-ajax'),

    path('<slug:country_code>/panel-profile-cell-list-json/', PanelProfileCellListing.as_view(), name='panel-profile-cell-list-json'),
    path('<slug:country_code>/panel-profile-cell-list-json/<int:pk>', PanelProfileCellListing.as_view(), name='panel-profile-cell-list-json'),

    path('<slug:country_code>/cell-list-ajax/', CellListViewAjax.as_view(), name='cell-list-ajax'),
    path('<slug:country_code>/cell-list/', CellListView.as_view(), name='cell-list'),
    path('<slug:country_code>/cell-create/', CellCreateView.as_view(), name='cell-create'),
    path('<slug:country_code>/cell-update/<int:pk>', CellUpdateView.as_view(), name='cell-update'),
    path('<slug:country_code>/cell-delete/<int:pk>', CellDeleteView.as_view(), name='cell-delete'),
]