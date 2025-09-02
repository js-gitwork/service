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

    # Nye felter (korrekt indrykning!)
    last_inspection_date = models.DateField(
        verbose_name=_("Sidste synsdato"),  # ← Oversæt også disse!
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

    def __str__(self):
        return f"{self.VPID} - {self.name}"

    class Meta:
        verbose_name = _("Aktiv")
        verbose_name_plural = _("Aktiver")
    def __str__(self):
        return self.name or self.VPID

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
    Navn = models.CharField(max_length=100, verbose_name=_("Navn"))
    Beskrivelse = models.TextField(blank=True, verbose_name=_("Beskrivelse"))

    class Meta:
        verbose_name = _("Udstyr")
        verbose_name_plural = _("Udstyr")

    def __str__(self):
        return self.Navn

class FaultReport(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("Titel"))
    description = models.TextField(verbose_name=_("Beskrivelse"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Oprettet"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Opdateret"))  # ← Ny: Spor ændringer
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

    # Prioritet (dine eksisterende valg bevares)
    priority = models.IntegerField(
        default=2,
        choices=[
            (1, _("Høj")),
            (2, _("Normal")),
            (3, _("Lav (vent til service)"))
        ],
        verbose_name=_("Prioritet")
    )

    # NYE FELTER TIL ARBEJDSFLOW:
    assigned_to = models.ForeignKey(  # ← Tildel til mekaniker
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Tildelt mekaniker"),
        related_name='assigned_reports'
    )
    started_at = models.DateTimeField(  # ← Hvornår mekanikeren startede
        null=True,
        blank=True,
        verbose_name=_("Arbejde påbegyndt")
    )
    completed_at = models.DateTimeField(  # ← Hvornår reparationen blev færdiggjort
        null=True,
        blank=True,
        verbose_name=_("Afsluttet")
    )
    completed_by = models.ForeignKey(  # ← Hvem afsluttede opgaven
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Udført af"),
        related_name='completed_reports'
    )
    notes = models.TextField(  # ← Noter fra værkfører/mekaniker
        blank=True,
        verbose_name=_("Noter (til mekaniker)")
    )
    is_approved = models.BooleanField(  # ← Godkendt af værkfører (valgfrit)
        default=False,
        verbose_name=_("Godkendt")
    )

    class Meta:
        verbose_name = _("Fejlrapport")
        verbose_name_plural = _("Fejlrapporter")
        ordering = ['-priority', '-created_at']  # ← Sorter efter prioritet og dato

    def __str__(self):
        return f"{self.asset.VPID if self.asset else self.vpid}: {self.title} ({self.get_priority_display()})"

    def save(self, *args, **kwargs):
        # Opdater `updated_at` ved hver gem
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def current_status(self):
        """Hjælpefunktion til at vise status på dansk."""
        if self.completed_at:
            return _("Færdig")
        elif self.started_at:
            return _("Igang")
        elif self.assigned_to:
            return _("Tildelt")
        else:
            return _("Ny")
