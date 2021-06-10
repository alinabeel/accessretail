from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

from django.shortcuts import redirect
from django.views.generic import RedirectView

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
from master_setups.views import DashboardView, IndexPageView,HomeView,change_password
import debug_toolbar


from rest_framework import routers

router = routers.DefaultRouter()



# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.


urlpatterns = [
    path('superadmin/', admin.site.urls),
    path('', IndexPageView.as_view(), name='index'),
    path('home/', HomeView.as_view(), name='home'),

    path('<slug:country_code>/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('master-setups/',  include('master_setups.urls', namespace="master-setups")),

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
    path('api/', include(router.urls)),

]
# Use static() to add url mapping to serve static files during development (only)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin Site Config
admin.sites.AdminSite.site_header = 'Access Retail Admin Panel'
admin.sites.AdminSite.site_title = 'Administration Panel'
admin.sites.AdminSite.index_title = 'Dashboard'
