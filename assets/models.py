from django.db import models
from django.utils.translation import gettext_lazy as _
from io import BytesIO
from PIL import Image, ImageDraw
import qrcode
from django.core.files import File
import os
from django.conf import settings

# --- KATEGORI ---
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Navn"))

    class Meta:
        verbose_name = _("Kategori")
        verbose_name_plural = _("Kategorier")

    def __str__(self):
        return self.name

# --- UDSTYR ---
class Equipment(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Navn"))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_("Kategori"))
    description = models.TextField(blank=True, verbose_name=_("Beskrivelse"))
    location = models.CharField(max_length=100, blank=True, verbose_name=_("Lokation"))

    class Meta:
        verbose_name = _("Udstyr")
        verbose_name_plural = _("Udstyr")

    def __str__(self):
        return self.name

# --- ASSET ---
class Asset(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Navn"))
    description = models.TextField(blank=True, verbose_name=_("Beskrivelse"))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Kategori"))
    location = models.CharField(max_length=100, blank=True, verbose_name=_("Lokation"))

    class Meta:
        verbose_name = _("Aktiv")
        verbose_name_plural = _("Aktiver")

    def __str__(self):
        return self.name

# --- SERVICE RAPPORT ---
class ServiceReport(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, verbose_name=_("Udstyr"))
    report_date = models.DateField(auto_now_add=True, verbose_name=_("Rapportdato"))
    description = models.TextField(verbose_name=_("Beskrivelse"))
    technician = models.CharField(max_length=100, blank=True, verbose_name=_("Tekniker"))
    completed = models.BooleanField(default=False, verbose_name=_("Afsluttet"))
    scheduled_for_now = models.BooleanField(default=False, verbose_name=_("Skal repareres nu"))

    class Meta:
        verbose_name = _("Service rapport")
        verbose_name_plural = _("Service rapporter")

    def __str__(self):
        return f"Service Rapport for {self.equipment.name} på {self.report_date}"

# --- FEJLRAPPORT ---
class FaultReport(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Titel"))
    description = models.TextField(verbose_name=_("Beskrivelse"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Oprettet"))
    image = models.ImageField(upload_to='fault_reports/', blank=True, null=True, verbose_name=_("Billede"))
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True, verbose_name=_("QR-kode"))
    repair_status = models.BooleanField(default=False, verbose_name=_("Reparationsstatus"))
    location = models.CharField(max_length=100, blank=True, verbose_name=_("Lokation"))
    machine = models.CharField(max_length=100, blank=True, verbose_name=_("Maskine"))
    status = models.CharField(
        max_length=20,
        choices=[
            ('NEW', _('Ny')),
            ('IN_PROGRESS', _('I gang')),
            ('COMPLETED', _('Afsluttet')),
        ],
        default='NEW',
        verbose_name=_("Status")
    )

    # Oversættelsesfelter
    title_en = models.CharField(max_length=200, blank=True, verbose_name="Title (English)")
    description_en = models.TextField(blank=True, verbose_name="Description (English)")
    title_de = models.CharField(max_length=200, blank=True, verbose_name="Titel (Deutsch)")
    description_de = models.TextField(blank=True, verbose_name="Beschreibung (Deutsch)")
    title_pl = models.CharField(max_length=200, blank=True, verbose_name="Tytuł (Polski)")
    description_pl = models.TextField(blank=True, verbose_name="Opis (Polski)")

    class Meta:
        verbose_name = _("Fejlrapport")
        verbose_name_plural = _("Fejlrapporter")

    def __str__(self):
        return self.title

    def generate_qr_code(self):
        if not self.qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(f"Fault Report: {self.id}")
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            self.qr_code.save(f"qr_{self.id}.png", File(buffer), save=False)
            buffer.close()

    def save_image(self, image):
        if image:
            img = Image.open(image)
            img.thumbnail((800, 800))

            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            buffer.seek(0)

            self.image.save(f"fault_{self.id}.jpg", File(buffer), save=False)
            buffer.close()

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.generate_qr_code()

        if self.title:
            self.title_en = self._translate(self.title, 'en') if not self.title_en else self.title_en
            self.title_de = self._translate(self.title, 'de') if not self.title_de else self.title_de
            self.title_pl = self._translate(self.title, 'pl') if not self.title_pl else self.title_pl

        if self.description:
            self.description_en = self._translate(self.description, 'en') if not self.description_en else self.description_en
            self.description_de = self._translate(self.description, 'de') if not self.description_de else self.description_de
            self.description_pl = self._translate(self.description, 'pl') if not self.description_pl else self.description_pl

        super().save(*args, **kwargs)

    def _translate(self, text, language):
        try:
            from googletrans import Translator
            translator = Translator()
            return translator.translate(text, dest=language).text
        except Exception as e:
            print(f"Could not translate '{text}': {e}")
            return text

    def get_title(self, language_code='da'):
        if language_code == 'en':
            return self.title_en or self.title
        elif language_code == 'de':
            return self.title_de or self.title
        elif language_code == 'pl':
            return self.title_pl or self.title
        return self.title

    def get_description(self, language_code='da'):
        if language_code == 'en':
            return self.description_en or self.description
        elif language_code == 'de':
            return self.description_de or self.description
        elif language_code == 'pl':
            return self.description_pl or self.description
        return self.description
