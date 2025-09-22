from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Case, When, Value, IntegerField
from django.urls import reverse
from .models import Asset, Category, Equipment, FaultReport

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    exclude = ('qr_code',)
    list_display = (
        'VPID', 'name', 'last_inspection_date',
        'last_service_date', 'in_workshop',
        'workshop_from_date', 'workshop_expected_return',
        'qr_print_button', 'open_in_assets', 'latest_fault_report_date'
    )
    list_editable = (
        'in_workshop',
        'workshop_from_date',
        'workshop_expected_return',
    )
    list_filter = (
        'category', 'is_active',
        'last_inspection_date', 'last_service_date',
        'in_workshop',
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
        url = reverse('admin:assets_asset_change', args=[obj.pk])
        return format_html('<a href="{}">Ret</a>', url)
    open_in_assets.short_description = "Ret"

    def latest_fault_report_date(self, obj):
        latest_report = obj.faultreport_set.order_by('-created_at').first()
        if latest_report and latest_report.expected_workshop_date:
            return format_html(
                '<a href="{}" style="color: #337ab7;">{}</a>',
                reverse('admin:assets_faultreport_change', args=[latest_report.id]),
                latest_report.expected_workshop_date.strftime("%d-%m-%Y %H:%M")
            )
        return "-"
    latest_fault_report_date.short_description = "Forventet værksted"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('faultreport_set')

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('Navn', 'Beskrivelse')
    search_fields = ('Navn',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(FaultReport)
class FaultReportAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'vpid', 'priority', 'colored_status',
        'expected_workshop_date', 'created_at', 'assigned_to'
    )
    list_filter = ('priority', 'status', 'assigned_to', 'sprog', 'expected_workshop_date')
    search_fields = ('title', 'vpid', 'description', 'original_description')
    readonly_fields = (
        'created_at', 'updated_at', 'vpid', 'priority',
        'started_at', 'completed_at', 'completed_by'
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            sort_order=Case(
                When(status='Completed', then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('sort_order', '-priority', '-created_at')

    def colored_status(self, obj):
        if obj.status == 'Completed':
            return format_html('<span style="color: green;">{}</span>', obj.get_status_display())
        elif obj.status == 'Paused':
            return format_html('<span style="color: orange;">{}</span>', obj.get_status_display())
        else:
            return format_html('<span style="color: red;">{}</span>', obj.get_status_display())
    colored_status.short_description = 'Status'

    fieldsets = (
        ('Grundlæggende information', {
            'fields': ('title', 'vpid', 'priority'),
            'description': 'VPID og prioritet er låst efter oprettelse.'
        }),
        ('Beskrivelser', {
            'fields': ('description', 'original_description'),
            'classes': ('collapse',),
        }),
        ('Værkstedsplanlægning', {  # Ny sektion for værkstedsdato
            'fields': ('expected_workshop_date',),
            'description': 'Aftalt tidspunkt for indkaldelse til værksted (kan redigeres her).',
            'classes': ('collapse',),
        }),
        ('Tidsstempler (automatisk)', {
            'fields': ('started_at', 'completed_at', 'completed_by'),
            'description': format_html(
                '<strong>OBS:</strong> Disse felter udfyldes <em>automatisk</em> '
                'når mekanikeren starter/afslutter opgaven. <strong>Rediger ikke manuelt!</strong>'
            ),
            'classes': ('collapse',),
        }),
        ('Reparationsrapport', {
            'fields': ('mechanic_report',),
            'classes': ('collapse',),
        }),
        ('Billeder', {
            'fields': ('image',),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'sprog' in form.base_fields:
            form.base_fields['sprog'].widget = forms.HiddenInput()
        return form

admin.site.site_header = "Service Administration"
admin.site.site_title = "Service Admin"
admin.site.index_title = "Velkommen til Service Admin"
