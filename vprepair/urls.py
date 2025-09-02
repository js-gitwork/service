from django.contrib import admin
from django.urls import path
from assets import views  # Gendannet
from assets.qr_utils import print_qr_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('print_qr/<int:asset_id>/', print_qr_view, name='print_qr'),

    # API-endpoints
    path('api/assets/', views.asset_list_api, name='asset_list_api'),
    path('api/reports/', views.submit_report, name='submit_report'),

    # Mekaniker-flow
    path('mechanic/', views.mechanic_view, name='mechanic_reports'),
    path('report/<int:report_id>/<str:action>/', views.update_report_status, name='update_report_status'),

    # Asset-håndtering
    path('assets/', views.asset_list, name='asset_list'),
    path('assets/<int:pk>/edit/', views.edit_asset, name='edit_asset'),
]
