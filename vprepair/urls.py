from django.contrib import admin
from django.urls import path, include
from assets import views  # ← Tilføj denne linje

urlpatterns = [
    path('admin/', admin.site.urls),
    path('assets/', views.asset_list, name='asset_list'),
    path('assets/<int:pk>/edit/', views.edit_asset, name='edit_asset'),
]
