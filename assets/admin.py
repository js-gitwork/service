from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Asset, Category, Equipment, FaultReport

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        'VPID', 'name', 'last_inspection_date',
        'last_service_date', 'in_workshop',  # <-- Tilføjet
        'workshop_from_date',                # <-- Tilføjet
        'workshop_expected_return',          # <-- Tilføjet
        'qr_print_button', 'open_in_assets'
    )
    list_editable = (
        'in_workshop',                      # <-- Tilføjet
        'workshop_from_date',               # <-- Tilføjet
        'workshop_expected_return',         # <-- Tilføjet
    )
    list_filter = (
        'category', 'is_active',
        'last_inspection_date', 'last_service_date',
        'in_workshop',                      # <-- Tilføjet (valgfrit)
    )
    search_fields = ('VPID', 'name', 'description')
    filter_horizontal = ('equipment',)
    actions = None


    def qr_print_button(self, obj):
        return format_html(
            '<a href="{}" target="_blank" style="background: #417690; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; display: inline-block;">Print QR</a>',
            reverse('print_qr', args=[obj.id])
        )
    qr_print_button.short_description = "Print QR-kode"

    def open_in_assets(self, obj):
         return format_html(
            '<a href="{}" target="_blank" class="button">Ret</a>',
            reverse('edit_asset', args=[obj.pk])  # <-- Brug `obj.pk` i stedet for `obj.id`
        )

    open_in_assets.short_description = "Ret"

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('Navn', 'Beskrivelse')
    search_fields = ('Navn',)

@admin.register(FaultReport)
class FaultReportAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'asset', 'priority', 'current_status',
        'created_at', 'assigned_to', 'sprog'
    )
    list_filter = ('priority', 'status', 'assigned_to', 'sprog')
    search_fields = ('title', 'vpid', 'description', 'original_description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('title', 'asset', 'vpid', 'priority', 'sprog')}),
        ('Beskrivelser', {'fields': ('description', 'original_description')}),
        ('Status', {'fields': ('status', 'assigned_to', 'started_at', 'completed_at', 'completed_by', 'repair_status')}),
        ('Billeder', {'fields': ('image',)}),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.site_header = "Service Administration"
admin.site.site_title = "Service Admin"
admin.site.index_title = "Velkommen til Service Admin"
