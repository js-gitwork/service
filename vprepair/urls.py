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
)
from assets.qr_utils import print_qr_view

urlpatterns = [
    # System- og API-relaterede URLs (ikke-sprogafhængige)
    path('admin/', admin.site.urls),
    path('rosetta/', include('rosetta.urls')),  # Rosetta for oversættelsesadmin
    path('i18n/', include('django.conf.urls.i18n')),  # Django's i18n URLs
    path('accounts/', include('django.contrib.auth.urls')),  # Auth (login/logout)
    path('', index, name='index'),  # Forsiden (altid index.html, uanset sprog)

    # API-endpoints (ikke-sprogafhængige)
    path('api/assets/', asset_list_api, name='asset_list_api'),
    path('api/reports/', submit_report, name='submit_report'),
]

# Sprogafhængige URLs (brug i18n_patterns)
urlpatterns += i18n_patterns(
    # Mechanic-relaterede sider
    path('mechanic/', mechanic_view, name='mechanic_reports'),
    path('report/<int:report_id>/<str:action>/', update_report_status, name='update_report_status'),

    # Asset-redigering (sprogafhængig)
    path('assets/<int:pk>/edit/', edit_asset, name='edit_asset'),

    # QR-print (sprogafhængig)
    path('print_qr/<int:asset_id>/', print_qr_view, name='print_qr'),
)
