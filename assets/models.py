from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.files.base import ContentFile
from io import BytesIO
import qrcode

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Kategori"))

    class Meta:
        verbose_name = _("Kategori")
        verbose_name_plural = _("Kategorier")

    def __str__(self):
        return self.name

class Asset(models.Model):
    VPID = models.CharField(max_length=100, verbose_name=_("VPID"))
    description = models.TextField(verbose_name=_("Beskrivelse"))
    name = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Navn"))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Kategori"))
    location = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Lokation"))
    title_en = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Titel (EN)"))
    description_en = models.TextField(blank=True, default="", verbose_name=_("Beskrivelse (EN)"))
    title_de = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Titel (DE)"))
    description_de = models.TextField(blank=True, default="", verbose_name=_("Beskrivelse (DE)"))
    title_pl = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Titel (PL)"))
    description_pl = models.TextField(blank=True, default="", verbose_name=_("Beskrivelse (PL)"))
    image = models.ImageField(upload_to='assets/', blank=True, verbose_name=_("Billede"))
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True, verbose_name=_("QR-kode"))
    is_active = models.BooleanField(default=True, verbose_name=_("Aktiv"))  # ← NYT FELT: Markér som udgået

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
    status = models.CharField(max_length=100, blank=True, verbose_name=_("Status"))
    qr_code = models.CharField(max_length=100, blank=True, default="", verbose_name=_("QR-kode"))
    image = models.ImageField(upload_to='fault_reports/', blank=True, verbose_name=_("Billede"))
    repair_status = models.BooleanField(default=False, verbose_name=_("Reparationsstatus"))
    machine = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Maskine"))
    location = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Lokation"))
    vpid = models.CharField(max_length=100, blank=True, verbose_name=_("VPID"))
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Aktiv"))
    priority = models.IntegerField(default=2, choices=[
        (1, _("Høj")),
        (2, _("Normal")),
        (3, _("Lav (vent til service)"))
    ], verbose_name=_("Prioritet"))

    class Meta:
        verbose_name = _("Fejlrapport")
        verbose_name_plural = _("Fejlrapporter")

    def __str__(self):
        return f"{self.asset.VPID if self.asset else self.vpid}: {self.title}"
