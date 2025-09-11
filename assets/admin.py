from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Asset, Category, Equipment, FaultReport

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        'VPID', 'name', 'last_inspection_date',
        'last_service_date', 'qr_print_button', 'open_in_assets'
    )
    list_filter = ('category', 'is_active', 'last_inspection_date', 'last_service_date')
    search_fields = ('VPID', 'name', 'description')
    filter_horizontal = ('equipment',)
    actions = None

    def qr_print_button(self, obj):
        return format_html('<a href="{}" target="_blank">Print QR</a>', reverse('admin:qr_print', args=[obj.id]))
    qr_print_button.short_description = "Print QR-kode"

    def open_in_assets(self, obj):
        return format_html('<a href="{}" target="_blank">Åbn</a>', reverse('asset_detail', args=[obj.id]))
    open_in_assets.short_description = "Åbn i aktiver"

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')  # Rettet fra 'Navn', 'Beskrivelse'
    search_fields = ('name',)  # Rettet fra 'Navn'

@admin.register(FaultReport)
class FaultReportAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'asset', 'priority', 'current_status',
        'created_at', 'assigned_to', 'sprog'  # Tilføjet 'sprog'
    )
    list_filter = ('priority', 'status', 'assigned_to', 'sprog')  # Tilføjet 'sprog'
    search_fields = ('title', 'vpid', 'description', 'original_description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'asset', 'vpid', 'priority', 'sprog')
        }),
        ('Beskrivelser', {
            'fields': ('description', 'original_description')
        }),
        ('Status', {
            'fields': ('status', 'assigned_to', 'started_at', 'completed_at', 'completed_by', 'repair_status')
        }),
        ('Billeder', {
            'fields': ('image',)
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.site_header = "Service Administration"
admin.site.site_title = "Service Admin"
admin.site.index_title = "Velkommen til Service Admin"
