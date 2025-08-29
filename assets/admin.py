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
    list_display = ('name', 'category', 'location')  # Rettet: Brug 'name' i stedet for 'call_name'
    list_filter = ('category',)
    search_fields = ('name', 'description', 'location')  # Rettet: Fjernet 'registration_number'
    verbose_name = _("Aktiv")
    verbose_name_plural = _("Aktiver")

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'description')
    verbose_name = _("Udstyr")
    verbose_name_plural = _("Udstyr")
    # Note: 'filter_horizontal = ('assets',)' er fjernet, da 'Equipment' ikke har et 'assets'-felt.
    # Hvis du senere tilføjer det, kan du genaktivere denne linje.

@admin.register(ServiceReport)
class ServiceReportAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'report_date', 'completed')  # Rettet: Brug 'completed' i stedet for 'is_completed'
    list_filter = ('completed', 'report_date', 'equipment__category')  # Rettet: Brug 'completed' og 'equipment__category'
    search_fields = ('equipment__name', 'description')
    actions = ['mark_as_completed', 'mark_as_scheduled_now']

    def mark_as_completed(self, request, queryset):
        queryset.update(completed=True)  # Rettet: Brug 'completed' i stedet for 'is_completed'
    mark_as_completed.short_description = _("Marker som færdig")

    def mark_as_scheduled_now(self, request, queryset):
        queryset.update(scheduled_for_now=True)  # Dette felt eksisterer ikke i din nuværende model.
        # Hvis du vil bruge denne funktion, skal du tilføje 'scheduled_for_now' til ServiceReport-modellen.
    mark_as_scheduled_now.short_description = _("Marker som 'Skal repareres nu'")
    verbose_name = _("Service rapport")
    verbose_name_plural = _("Service rapporter")

@admin.register(FaultReport)
class FaultReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'repair_status')  # Rettet: Brug 'title' og 'repair_status'
    list_filter = ('repair_status', 'created_at')  # Rettet: Brug 'repair_status'
    search_fields = ('title', 'description', 'location', 'machine')  # Rettet: Brug 'title' i stedet for 'asset__call_name'
    actions = ['mark_as_resolved']

    def mark_as_resolved(self, request, queryset):
        queryset.update(repair_status=True)  # Rettet: Brug 'repair_status' i stedet for 'is_resolved'
    mark_as_resolved.short_description = _("Marker som løst")
    verbose_name = _("Fejlrapport")
    verbose_name_plural = _("Fejlrapporter")
