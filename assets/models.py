from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.files.base import ContentFile
from io import BytesIO
import qrcode
from django.utils import timezone
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Kategori"))

    class Meta:
        verbose_name = _("Kategori")
        verbose_name_plural = _("Kategorier")

    def __str__(self):
        return self.name

class Asset(models.Model):
    VPID = models.CharField(max_length=100, verbose_name=_("VPID"))
    name = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Navn"))
    description = models.TextField(verbose_name=_("Beskrivelse"))
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Kategori")
    )
    location = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Lokation"))
    image = models.ImageField(upload_to='assets/', blank=True, verbose_name=_("Billede"))
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True, verbose_name=_("QR-kode"))
    is_active = models.BooleanField(default=True, verbose_name=_("Aktiv"))
    last_inspection_date = models.DateField(
        verbose_name=_("Sidste synsdato"),
        blank=True,
        null=True,
        help_text=_("Dato for seneste syn")
    )
    last_service_date = models.DateField(
        verbose_name=_("Sidste servicedato"),
        blank=True,
        null=True,
        help_text=_("Dato for seneste service")
    )
    equipment = models.ManyToManyField(
        'Equipment',
        verbose_name=_("Udstyr på aktivet"),
        blank=True,
        help_text=_("Udstyr monteret på dette aktiv")
    )

    class Meta:
        verbose_name = _("Aktiv")
        verbose_name_plural = _("Aktiver")

    def __str__(self):
        return f"{self.VPID} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.VPID)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            self.qr_code.save(f'qr_{self.VPID}.png', ContentFile(buffer.getvalue()), save=False)
        super().save(*args, **kwargs)

class Equipment(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Navn"))  # Rettet fra "Navn" → "name"
    description = models.TextField(blank=True, verbose_name=_("Beskrivelse"))  # Rettet fra "Beskrivelse" → "description"

    class Meta:
        verbose_name = _("Udstyr")
        verbose_name_plural = _("Udstyr")

    def __str__(self):
        return self.name  # Rettet fra "Navn" → "name"

class FaultReport(models.Model):
    LANGUAGE_CHOICES = [
        ('de', _("Tysk")),
        ('pl', _("Polsk")),
        ('en', _("Engelsk")),
    ]

    title = models.CharField(max_length=100, verbose_name=_("Titel"))
    description = models.TextField(verbose_name=_("Beskrivelse (oversat)"))
    original_description = models.TextField(blank=True, null=True, verbose_name=_("Original beskrivelse"))
    sprog = models.CharField(  # NYT FELT: Gemmer det originale sprog
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='de',
        verbose_name=_("Originalt sprog")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Oprettet"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Opdateret"))
    status = models.CharField(max_length=100, blank=True, verbose_name=_("Status"))
    qr_code = models.CharField(max_length=100, blank=True, default="", verbose_name=_("QR-kode"))
    image = models.ImageField(upload_to='fault_reports/', blank=True, verbose_name=_("Billede"))
    repair_status = models.BooleanField(default=False, verbose_name=_("Reparationsstatus"))
    machine = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Maskine"))
    location = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Lokation"))
    vpid = models.CharField(max_length=100, blank=True, verbose_name=_("VPID"))
    asset = models.ForeignKey(
        'Asset', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Aktiv")
    )
    priority = models.IntegerField(
        default=2,
        choices=[
            (1, _("Høj")),
            (2, _("Normal")),
            (3, _("Lav (vent til service)"))
        ],
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

    class Meta:
        verbose_name = _("Fejlrapport")
        verbose_name_plural = _("Fejlrapporter")
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.asset.VPID if self.asset else self.vpid}: {self.title} ({self.get_priority_display()})"

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def current_status(self):
        if self.completed_at:
            return _("Færdig")
        elif self.started_at:
            return _("Igang")
        elif self.assigned_to:
            return _("Tildelt")
        else:
            return _("Ny")
