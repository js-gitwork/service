from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import render
from .models import Asset, Category, Equipment, FaultReport
from .qr_utils import qr_print_button, print_qr_view

# Admin-site konfiguration
admin.site.site_header = _("VPRepair Administration")
admin.site.site_title = _("VPRepair Admin")
admin.site.index_title = _("Velkommen til administrationen")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    # Standard rediger/slet er aktiv (ingen ændringer nødvendige)

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('VPID', 'name', 'description', 'qr_print_button', 'open_in_assets')
    list_filter = ('category',)
    search_fields = ('VPID', 'name', 'description')

    def qr_print_button(self, obj):
        return qr_print_button(obj)
    qr_print_button.short_description = _("Print QR-kode")
    qr_print_button.allow_tags = True

    def open_in_assets(self, obj):
        return format_html(
            '<a href="/assets/?focus={}" target="_blank" class="button">Redigér</a>',
            obj.pk
        )
    open_in_assets.short_description = 'Redigér'
    open_in_assets.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:asset_id>/print_qr/', print_qr_view, name='print_qr'),
        ]
        return custom_urls + urls

    def print_qr_view(self, request, asset_id):
        asset = Asset.objects.get(id=asset_id)
        return render(request, 'admin/print_qr.html', {'asset': asset})

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('Navn', 'Beskrivelse')
    search_fields = ('Navn', 'Beskrivelse')

@admin.register(FaultReport)
class FaultReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'asset', 'created_at', 'get_priority_display', 'repair_status')
    list_filter = ('asset', 'priority', 'repair_status')
    search_fields = ('asset__VPID', 'title', 'description')
    actions = [
        'mark_as_resolved',
        'set_priority_high',
        'set_priority_normal',
        'set_priority_low',
    ]

    def mark_as_resolved(self, request, queryset):
        queryset.update(repair_status=True)
    mark_as_resolved.short_description = _("Marker som løst")

    def set_priority_high(self, request, queryset):
        queryset.update(priority=1)
    set_priority_high.short_description = _("Sæt prioritet til Høj")

    def set_priority_normal(self, request, queryset):
        queryset.update(priority=2)
    set_priority_normal.short_description = _("Sæt prioritet til Normal")

    def set_priority_low(self, request, queryset):
        queryset.update(priority=3)
    set_priority_low.short_description = _("Sæt prioritet til Lav (vent til service)")
