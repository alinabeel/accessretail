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

""" Region Type"""
urlpatterns += [
    path('<slug:country_code>/region-type-list-ajax/', RegionTypeListViewAjax.as_view(), name='region-type-list-ajax'),
    path('<slug:country_code>/region-type-list/', RegionTypeListView.as_view(), name='region-type-list'),
    path('<slug:country_code>/region-type-create/', RegionTypeCreateView.as_view(), name='region-type-create'),
    path('<slug:country_code>/region-type-update/<int:pk>', RegionTypeUpdateView.as_view(), name='region-type-update'),
    path('<slug:country_code>/region-type-delete/<int:pk>', RegionTypeDeleteView.as_view(), name='region-type-delete'),
]


""" Region """
urlpatterns += [
    path('<slug:country_code>/region-list-ajax/', RegionListViewAjax.as_view(), name='region-list-ajax'),
    path('<slug:country_code>/region-list/', RegionListView.as_view(), name='region-list'),
    path('<slug:country_code>/region-create/', RegionCreateView.as_view(), name='region-create'),
    path('<slug:country_code>/region-update/<int:pk>', RegionUpdateView.as_view(), name='region-update'),
    path('<slug:country_code>/region-delete/<int:pk>', RegionDeleteView.as_view(), name='region-delete'),
]

""" Index Setup """
urlpatterns += [
    path('<slug:country_code>/indexsetup-list/', IndexSetupListView.as_view(), name='indexsetup-list'),
    path('<slug:country_code>/indexsetup-create/', IndexSetupCreateView.as_view(), name='indexsetup-create'),
    path('<slug:country_code>/indexsetup-update/<int:pk>', IndexSetupUpdateView.as_view(), name='indexsetup-update'),
    path('<slug:country_code>/indexsetup-delete/<int:pk>', IndexSetupDeleteView.as_view(), name='indexsetup-delete'),
]

""" Category """
urlpatterns += [
    path('<slug:country_code>/category-list-ajax/', CategoryListViewAjax.as_view(), name='category-list-ajax'),
    path('<slug:country_code>/category-list/', CategoryListView.as_view(), name='category-list'),
    path('<slug:country_code>/category-create/', CategoryCreateView.as_view(), name='category-create'),
    path('<slug:country_code>/category-update/<int:pk>', CategoryUpdateView.as_view(), name='category-update'),
    path('<slug:country_code>/category-delete/<int:pk>', CategoryDeleteView.as_view(), name='category-delete'),
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

""" Threshold """
urlpatterns += [
    path('<slug:country_code>/threshold/', ThresholdListView.as_view(), name='threshold'),
    path('<slug:country_code>/threshold-update/', ThresholdUpdateView.as_view(), name='threshold-update'),

]