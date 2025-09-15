from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from assets.views import (
    index,  # Din funktion hedder 'index', ikke 'index_view'
    mechanic_view,
    switch_mechanic,
    update_report_status,
    assign_report_to_me,
    open_reports,
    asset_list_api,
    submit_report,
    edit_asset,
    asset_detail,
    print_qr_view,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Hovedside
    path('', index, name='index'),  # Brug 'index' i stedet for 'index_view'

    # Mekaniker-views
    path('mechanic/', mechanic_view, name='mechanic_reports'), 
    path('mechanic/switch/', switch_mechanic, name='switch_mechanic'),

    # Fejlrapport-handling
    path('reports/<int:report_id>/start/', update_report_status, name='update_report_status_start'),
    path('reports/<int:report_id>/complete/', update_report_status, name='update_report_status_complete'),
    path('reports/<int:report_id>/assign/', assign_report_to_me, name='assign_report_to_me'),

    # Åbne fejlrapporter
    path('open_reports/', open_reports, name='open_reports'),

    # API-endpoints
    path('api/assets/', asset_list_api, name='api_assets'),
    path('api/reports/', submit_report, name='api_reports'),

    # Redigering af aktiver
    path('assets/<int:pk>/edit/', edit_asset, name='edit_asset'),
    path('assets/<int:pk>/', asset_detail, name='asset_detail'),
    path('assets/<int:asset_id>/qr/', print_qr_view, name='print_qr'),
]

# Medie-filer i development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
