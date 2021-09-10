from django.urls import path
from master_setups.views import *

app_name = "master-setups"
""" Country """
urlpatterns = [
    path('country-list/', CountryListView.as_view(), name='country-list'),
    path('country-list/', CountryListView.as_view(), name='country-list'),
    path('country-create/', CountryCreateView.as_view(), name='country-create'),
    path('country-update/<int:pk>', CountryUpdateView.as_view(), name='country-update'),
    path('country-delete/<int:pk>', CountryDeleteView.as_view(), name='country-delete'),

]

""" Code Frame"""
urlpatterns += [
    path('<slug:country_code>/code-frame-list-ajax/', CodeFrameListViewAjax.as_view(), name='code-frame-list-ajax'),
    path('<slug:country_code>/code-frame-list/', CodeFrameListView.as_view(), name='code-frame-list'),
    # path('<slug:country_code>/region-type-create/', RegionTypeCreateView.as_view(), name='region-type-create'),
    # path('<slug:country_code>/region-type-update/<int:pk>', RegionTypeUpdateView.as_view(), name='region-type-update'),
    # path('<slug:country_code>/region-type-delete/<int:pk>', RegionTypeDeleteView.as_view(), name='region-type-delete'),
    path('<slug:country_code>/code-frame-import/', CodeFrameImportView.as_view(), name='code-frame-import'),
]


""" Region Type"""
urlpatterns += [
    path('<slug:country_code>/region-type-list-ajax/', RegionTypeListViewAjax.as_view(), name='region-type-list-ajax'),
    path('<slug:country_code>/region-type-list/', RegionTypeListView.as_view(), name='region-type-list'),
    path('<slug:country_code>/region-type-create/', RegionTypeCreateView.as_view(), name='region-type-create'),
    path('<slug:country_code>/region-type-update/<int:pk>', RegionTypeUpdateView.as_view(), name='region-type-update'),
    path('<slug:country_code>/region-type-delete/<int:pk>', RegionTypeDeleteView.as_view(), name='region-type-delete'),
    path('<slug:country_code>/region-type-import/', RegionTypeImportView.as_view(), name='region-type-import'),
]


""" Region """
urlpatterns += [
    path('<slug:country_code>/region-list-ajax/', RegionListViewAjax.as_view(), name='region-list-ajax'),
    path('<slug:country_code>/region-list/', RegionListView.as_view(), name='region-list'),
    path('<slug:country_code>/region-create/', RegionCreateView.as_view(), name='region-create'),
    path('<slug:country_code>/region-update/<int:pk>', RegionUpdateView.as_view(), name='region-update'),
    path('<slug:country_code>/region-delete/<int:pk>', RegionDeleteView.as_view(), name='region-delete'),
    path('<slug:country_code>/region-import/', RegionImportView.as_view(), name='region-import'),
]

""" Month """
urlpatterns += [
    path('<slug:country_code>/month-list-ajax/', MonthListViewAjax.as_view(), name='month-list-ajax'),
    path('<slug:country_code>/month-list/', MonthListView.as_view(), name='month-list'),
    path('<slug:country_code>/month-create/', MonthCreateView.as_view(), name='month-create'),
    path('<slug:country_code>/month-update/<int:pk>', MonthUpdateView.as_view(), name='month-update'),
    path('<slug:country_code>/month-delete/<int:pk>', MonthDeleteView.as_view(), name='month-delete'),
]


""" Index Setup """
urlpatterns += [
    path('<slug:country_code>/indexsetup-list/', IndexSetupListView.as_view(), name='indexsetup-list'),
    path('<slug:country_code>/indexsetup-create/', IndexSetupCreateView.as_view(), name='indexsetup-create'),
    path('<slug:country_code>/indexsetup-update/<int:pk>', IndexSetupUpdateView.as_view(), name='indexsetup-update'),
    path('<slug:country_code>/indexsetup-delete/<int:pk>', IndexSetupDeleteView.as_view(), name='indexsetup-delete'),
]


""" Index Category """
urlpatterns += [
    path('<slug:country_code>/indexcategory-list-ajax/', IndexCategoryListViewAjax.as_view(), name='indexcategory-list-ajax'),
    path('<slug:country_code>/indexcategory-list/', IndexCategoryListView.as_view(), name='indexcategory-list'),
    path('<slug:country_code>/indexcategory-add', IndexCategoryCreateView.as_view(), name='indexcategory-add'),
    path('<slug:country_code>/indexcategory-update/<int:pk>', IndexCategoryUpdateView.as_view(), name='indexcategory-update'),
    path('<slug:country_code>/indexcategory-delete/<int:pk>', IndexCategoryDeleteView.as_view(), name='indexcategory-delete'),
]


""" User """
urlpatterns += [
    path('<slug:country_code>/password/<int:pk>', change_password, name='change_password'),

    path('<slug:country_code>/user-list-ajax/', UserListViewAjax.as_view(), name='user-list-ajax'),
    path('<slug:country_code>/user-list/', UserListView.as_view(), name='user-list'),
    path('<slug:country_code>/user-create/', UserCreateView.as_view(), name='user-create'),
    path('<slug:country_code>/user-update/<int:pk>', UserUpdateView.as_view(), name='user-update'),
    path('<slug:country_code>/user-delete/<int:pk>', UserDeleteView.as_view(), name='user-delete'),
]


""" User Country """
urlpatterns += [
    path('<slug:country_code>/usercountry-list/', UserCountryListView.as_view(), name='usercountry-list'),
    path('<slug:country_code>/usercountry-update/<int:pk>', UserCountryUpdateView.as_view(), name='usercountry-update'),
]



""" Outlet Status """
urlpatterns += [
    path('<slug:country_code>/outlet-status-list-ajax/', OutletStatusListViewAjax.as_view(), name='outlet-status-list-ajax'),
    path('<slug:country_code>/outlet-status-list/', OutletStatusListView.as_view(), name='outlet-status-list'),
    path('<slug:country_code>/outlet-status-create/', OutletStatusCreateView.as_view(), name='outlet-status-create'),
    path('<slug:country_code>/outlet-status-update/<int:pk>', OutletStatusUpdateView.as_view(), name='outlet-status-update'),
    path('<slug:country_code>/outlet-status-delete/<int:pk>', OutletStatusDeleteView.as_view(), name='outlet-status-delete'),
]


""" Threshold """
urlpatterns += [
    path('<slug:country_code>/threshold/', ThresholdListView.as_view(), name='threshold'),
    path('<slug:country_code>/threshold-update/', ThresholdUpdateView.as_view(), name='threshold-update'),

]