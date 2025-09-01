from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Asset, Category, Equipment, FaultReport

# Tilpas admin-sidens overskrifter til dansk
admin.site.site_header = _("VPRepair Administration")
admin.site.site_title = _("VPRepair Admin")
admin.site.index_title = _("Velkommen til administrationen")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    verbose_name = _("Kategori")
    verbose_name_plural = _("Kategorier")

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('VPID', 'name', 'category', 'location')  # VPID er vigtigst
    list_filter = ('category',)
    search_fields = ('VPID', 'name', 'description', 'location')
    ordering = ('VPID',)

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('Navn', 'Beskrivelse')  # Matcher din database
    search_fields = ('Navn', 'Beskrivelse')
    verbose_name = _("Udstyr")
    verbose_name_plural = _("Udstyr")

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
        'export_to_excel'
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

    def export_to_excel(self, request, queryset):
        # Din eksisterende Excel-eksport-funktion
        pass
    export_to_excel.short_description = _("Eksporter til Excel")


    def get_queryset(self, request):
        return super().get_queryset(request).select_related('asset')

    def asset_vpid(self, obj):
        return obj.asset.VPID
    asset_vpid.admin_order_field = 'asset__VPID'
    asset_vpid.short_description = _("Maskine (VPID)")
