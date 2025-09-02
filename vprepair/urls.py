from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth import views as auth_views
from assets.views import index, asset_list_api, submit_report, mechanic_view, update_report_status, asset_list, edit_asset
from assets.qr_utils import print_qr_view

urlpatterns = [
    # URLs der IKKE skal oversættes (inkl. forsiden!)
    path('admin/', admin.site.urls),
    path('rosetta/', include('rosetta.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', index, name='index'),  # ← Forsiden bruger ALTID index.html (uanset sprog)

    # API-endpoints (oversættes ikke)
    path('api/assets/', asset_list_api, name='asset_list_api'),
    path('api/reports/', submit_report, name='submit_report'),
]

# URLs der SKAL oversættes (men IKKE forsiden)
urlpatterns += i18n_patterns(
    path('print_qr/<int:asset_id>/', print_qr_view, name='print_qr'),
    path('mechanic/', mechanic_view, name='mechanic_reports'),
    path('report/<int:report_id>/<str:action>/', update_report_status, name='update_report_status'),
    path('assets/', asset_list, name='asset_list'),
    path('assets/<int:pk>/edit/', edit_asset, name='edit_asset'),
)
