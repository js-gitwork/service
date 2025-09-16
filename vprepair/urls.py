from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from assets import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Bruger din eksisterende login.html
    path('', views.index, name='index'),
    path('mechanic/', views.mechanic_view, name='mechanic_reports'),
    path('mechanic/switch/', views.switch_mechanic, name='switch_mechanic'),
    path('reports/<int:report_id>/assign/', views.assign_report_to_me, name='assign_report'),
    path('reports/<int:report_id>/<str:action>/', views.update_report_status, name='update_report_status'),
    path('open_reports/', views.open_reports, name='open_reports'),
    path('api/assets/', views.asset_list_api, name='asset_list_api'),
    path('api/reports/', views.submit_report, name='submit_report'),
    path('assets/<int:pk>/edit/', views.edit_asset, name='edit_asset'),
    path('assets/<int:pk>/', views.asset_detail, name='asset_detail'),
    path('assets/<int:asset_id>/qr/', views.print_qr_view, name='print_qr'),
    path('task/<int:report_id>/', views.mechanic_task, name='mechanic_task'),
    path('mechanic/switch_back/', views.switch_back, name='switch_back'),
    path('logout/', LogoutView.as_view(), name='logout'),  # Fjernet next_page='login' (vi styrer det i templaten)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
