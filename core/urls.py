# from django.contrib import admin
# from django.urls import path

# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

from django.shortcuts import redirect
from django.views.generic import RedirectView

from rest_framework_jwt.views import obtain_jwt_token
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.urls import path, include,re_path
from accounts.views import SignupView,adminLoginProcess,NoCountry
from master_setups.views import DashboardView, IndexPageView,HomeView,HomeAjax,change_password
import debug_toolbar


from rest_framework import routers
from master_data.viewsApi import *

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.


urlpatterns = [
    path('superadmin/', admin.site.urls),
    path('', IndexPageView.as_view(), name='index'),

    path('token-auth/', obtain_jwt_token),
    path('home/', HomeView.as_view(), name='home'),
    path('home-ajax/', HomeAjax.as_view(), name='home-ajax'),

    path('<slug:country_code>/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('master-setups/',  include('master_setups.urls', namespace="master-setups")),
    path('master-data/',  include('master_data.urls', namespace="master-data")),
    path('correction/',  include('correction.urls', namespace="correction")),
    path('reports/',  include('reports.urls', namespace="reports")),



    path('signup/', SignupView.as_view(), name='signup'),

    path('reset-password/', PasswordResetView.as_view(), name='reset-password'),
    path('password-reset-done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('admin_login_process/',adminLoginProcess,name="admin_login_process"),
    path('nocountry/', NoCountry.as_view(), name='nocountry'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),


    path("data-browser/", include("data_browser.urls")),
    path('__debug__/', include(debug_toolbar.urls)),
    re_path(r'^simple_import/', include('simple_import.urls')),
    re_path(r'^report_builder/', include('report_builder.urls')),

    path('api/', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # path("", include("accounts.urls")),
    # path("", include("master_setups.urls")),
    # url(r'^advanced_filters/', include('advanced_filters.urls')),

]
# Use static() to add url mapping to serve static files during development (only)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin Site Config
admin.sites.AdminSite.site_header = str(settings.APP_NAME)+' Admin Panel'
admin.sites.AdminSite.site_title = 'Administration Panel'
admin.sites.AdminSite.index_title = 'Dashboard'
