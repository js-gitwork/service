from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Asset, Category, Equipment, ServiceReport, FaultReport

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
    list_display = ('call_name', 'registration_number', 'category')
    list_filter = ('category',)
    search_fields = ('call_name', 'registration_number', 'description')
    verbose_name = _("Aktiv")
    verbose_name_plural = _("Aktiver")

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('assets',)
    verbose_name = _("Udstyr")
    verbose_name_plural = _("Udstyr")

@admin.register(ServiceReport)
class ServiceReportAdmin(admin.ModelAdmin):
    list_display = ('asset', 'created_at', 'is_completed', 'scheduled_for_now')
    list_filter = ('is_completed', 'scheduled_for_now', 'asset__category')
    search_fields = ('asset__call_name', 'asset__registration_number', 'description')

    # Handlinger til at markere service som "færdig" eller "skal repareres nu"
    actions = ['mark_as_completed', 'mark_as_scheduled_now']

    def mark_as_completed(self, request, queryset):
        queryset.update(is_completed=True)
    mark_as_completed.short_description = _("Marker som færdig")

    def mark_as_scheduled_now(self, request, queryset):
        queryset.update(scheduled_for_now=True)
    mark_as_scheduled_now.short_description = _("Marker som 'Skal repareres nu'")

    verbose_name = _("Service rapport")
    verbose_name_plural = _("Service rapporter")

@admin.register(FaultReport)
class FaultReportAdmin(admin.ModelAdmin):
    list_display = ('asset', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'asset__category')
    search_fields = ('asset__call_name', 'asset__registration_number', 'description')

    # Handling til at markere fejl som "løst"
    actions = ['mark_as_resolved']

    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
    mark_as_resolved.short_description = _("Marker som løst")

    verbose_name = _("Fejlrapport")
    verbose_name_plural = _("Fejlrapporter")
