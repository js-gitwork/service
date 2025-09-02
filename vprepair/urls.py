from django.contrib import admin
from django.urls import path, include
from assets import views  # ← Tilføj denne linje
from assets.qr_utils import print_qr_view

urlpatterns = [
     path('print_qr/<int:asset_id>/', print_qr_view, name='print_qr'),
    path('admin/', admin.site.urls),
    path('assets/', views.asset_list, name='asset_list'),
    path('assets/<int:pk>/edit/', views.edit_asset, name='edit_asset'),
]
