from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Kategorinavn"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = _("Kategorier")

class Equipment(models.Model):
    Navn = models.CharField(max_length=100, verbose_name=_("Udstyrsnavn"))  # Ændret fra 'name' til 'Navn'
    Beskrivelse = models.TextField(blank=True, verbose_name=_("Beskrivelse"))  # Ændret fra 'description' til 'Beskrivelse'
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Kategori")
    )

    def __str__(self):
        return self.Navn  # Ændret fra 'name' til 'Navn'

    class Meta:
        verbose_name_plural = _("Udstyr")

class Asset(models.Model):
    VPID = models.CharField(max_length=50, unique=True, verbose_name=_("VPID"))
    name = models.CharField(max_length=100, verbose_name=_("Navn"))
    description = models.TextField(blank=True, verbose_name=_("Beskrivelse"))
    image = models.ImageField(upload_to='assets/', blank=True, null=True, verbose_name=_("Billede"))
    last_service_date = models.DateField(blank=True, null=True, verbose_name=_("Sidste service"))
    last_inspection_date = models.DateField(blank=True, null=True, verbose_name=_("Sidste syn"))
    location = models.CharField(max_length=100, blank=True, verbose_name=_("Lokation"))
    is_active = models.BooleanField(default=True, verbose_name=_("Aktiv"))
    in_workshop = models.BooleanField(default=False, verbose_name=_("I værksted"))
    workshop_from_date = models.DateField(blank=True, null=True, verbose_name=_("Værksted fra"))
    workshop_expected_return = models.DateField(blank=True, null=True, verbose_name=_("Forventet retur"))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Kategori"))
    qr_code = models.CharField(max_length=100, blank=True, verbose_name=_("QR-kode"))
    equipment = models.ManyToManyField(Equipment, blank=True, verbose_name=_("Tilknyttet udstyr"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Oprettet"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Opdateret"))

    def __str__(self):
        return f"{self.VPID} - {self.name}"

class FaultReport(models.Model):
    LANGUAGE_CHOICES = [
        ('de', _("Tysk")),
        ('pl', _("Polsk")),
        ('en', _("Engelsk")),
    ]

    PRIORITY_CHOICES = [
        (1, _("Høj")),
        (2, _("Normal")),
        (3, _("Lav (vent til service)")),
    ]

    STATUS_CHOICES = [
        ('Active', _("Aktiv")),
        ('Paused', _("På pause")),
        ('Completed', _("Afsluttet")),
    ]

    title = models.CharField(max_length=100, verbose_name=_("Titel"))
    description = models.TextField(verbose_name=_("Beskrivelse (oversat)"))
    original_description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Original beskrivelse")
    )
    sprog = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='de',
        verbose_name=_("Originalt sprog")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Oprettet"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Opdateret"))
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Active',
        verbose_name=_("Status")
    )
    qr_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="",
        verbose_name=_("QR-kode")
    )
    image = models.ImageField(
        upload_to='fault_reports/',
        blank=True,
        verbose_name=_("Billede")
    )
    repair_status = models.BooleanField(
        default=False,
        verbose_name=_("Reparationsstatus")
    )
    machine = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="",
        verbose_name=_("Maskine")
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="",
        verbose_name=_("Lokation")
    )
    vpid = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("VPID")
    )
    asset = models.ForeignKey(
        'Asset',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Aktiv")
    )
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=2,
        verbose_name=_("Prioritet")
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Tildelt mekaniker"),
        related_name='assigned_reports'
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Arbejde påbegyndt")
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Afsluttet")
    )
    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Udført af"),
        related_name='completed_reports'
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Noter (til mekaniker)")
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_("Godkendt")
    )
    mechanic_report = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Mekanikerrapport")
    )

    def __str__(self):
        return f"Rapport for {self.vpid or self.machine} ({self.created_at})"

    def current_status(self):
        return self.get_status_display()
    current_status.short_description = _("Nuværende status")
