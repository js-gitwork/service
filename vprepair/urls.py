from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth import views as auth_views
from assets.views import (
    index,
    asset_list_api,
    submit_report,
    mechanic_view,
    update_report_status,
    edit_asset,
    open_reports,
    print_qr_view,
    asset_detail,
    assign_report_to_me,
)

urlpatterns = [
    # System- og API-URLs (sproguafhængige)
    path('admin/', admin.site.urls),
    path('rosetta/', include('rosetta.urls')),  # Til oversættelsesadmin (kun for dig)
    path('i18n/', include('django.conf.urls.i18n')),  # Sprogskift (kun for index.html)

    # API-endpoints (sproguafhængige)
    path('api/assets/', asset_list_api, name='asset_list_api'),
    path('api/reports/', submit_report, name='submit_report'),

    # Danske sider (sproguafhængige URLs, viser altid dansk)
    path('assets/<int:pk>/', asset_detail, name='asset_detail'),  # <-- Tilføj denne linje
    path('open_reports/', open_reports, name='open_reports'),
    path('mechanic/', mechanic_view, name='mechanic_reports'),
    path('report/<int:report_id>/<str:action>/', update_report_status, name='update_report_status'),
    path('assets/<int:pk>/edit/', edit_asset, name='edit_asset'),
    path('print_qr/<int:asset_id>/', print_qr_view, name='print_qr'),
    path('assign_report/<int:report_id>/', assign_report_to_me, name='assign_report_to_me'),


    # Forside (index.html) - SKAL være sprogafhængig (for indtastning)
    path('', index, name='index'),
]
