from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse  # ← Tilføj denne import!
from django.urls import path
from .models import Asset, Category, Equipment, FaultReport
from .qr_utils import qr_print_button, print_qr_view

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        'VPID', 'name', 'last_inspection_date',
        'last_service_date', 'qr_print_button', 'open_in_assets'
    )
    list_filter = ('category', 'is_active', 'last_inspection_date', 'last_service_date')
    search_fields = ('VPID', 'name', 'description')
    filter_horizontal = ('equipment',)
    actions = None  # Fjerner "Handlinger"-menuen (inkl. "Slet valgte aktiver")

    def qr_print_button(self, obj):
        return format_html(
            '<a href="{}" target="_blank" class="button">Print QR</a>',
            reverse('print_qr', args=[obj.id])  # Nu virker dette
        )
    qr_print_button.short_description = _("Print QR-kode")
    qr_print_button.allow_tags = True

    def open_in_assets(self, obj):
        return format_html(
            '<a href="/admin/assets/asset/{}/change/" class="button" target="_blank">{}</a>',
            obj.pk,
            _("Redigér")
        )
    open_in_assets.short_description = _("Redigér")

    def has_delete_permission(self, request, obj=None):
        """Forhindrer sletning af aktiver."""
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:asset_id>/print_qr/', print_qr_view, name='print_qr'),
        ]
        return custom_urls + urls

# --- Resten af din admin.py (EquipmentAdmin, CategoryAdmin, FaultReportAdmin) ---
@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('Navn', 'Beskrivelse')
    search_fields = ('Navn', 'Beskrivelse')
    list_display_links = ('Navn',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(FaultReport)
class FaultReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'vpid', 'get_priority', 'repair_status', 'assigned_to', 'created_at')
    list_filter = ('priority', 'repair_status', 'assigned_to', 'created_at')
    search_fields = ('title', 'vpid', 'description', 'asset__VPID')

    def get_priority(self, obj):
        return obj.get_priority_display()
    get_priority.short_description = _("Prioritet")
