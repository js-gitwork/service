from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Navn")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategorier"

class Asset(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.TextField(verbose_name="Beskrivelse")
    call_name = models.CharField(max_length=100, verbose_name="Kaldenavn")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategori")
    registration_number = models.CharField(max_length=50, unique=True, verbose_name="Registreringsnummer")
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, verbose_name="QR-kode")
    image = models.ImageField(upload_to='assets/', blank=True, verbose_name="Billede")

    def __str__(self):
        return f"{self.call_name} ({self.registration_number})"

    class Meta:
        verbose_name = "Aktiv"
        verbose_name_plural = "Aktiver"

class Equipment(models.Model):
    name = models.CharField(max_length=100, verbose_name="Navn")
    assets = models.ManyToManyField(Asset, related_name='equipment', verbose_name="Aktiver")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Udstyr"
        verbose_name_plural = "Udstyr"

class ServiceReport(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name="Aktiv")
    description = models.TextField(verbose_name="Beskrivelse")
    image = models.ImageField(upload_to='service_reports/', blank=True, verbose_name="Billede")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Oprettet")
    is_completed = models.BooleanField(default=False, verbose_name="Færdiggjort")
    scheduled_for_now = models.BooleanField(default=False, verbose_name="Skal repareres nu")

    def __str__(self):
        return f"Service for {self.asset} ({self.created_at})"

    class Meta:
        verbose_name = "Service rapport"
        verbose_name_plural = "Service rapporter"

class FaultReport(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name="Aktiv")
    description = models.TextField(verbose_name="Beskrivelse")
    image = models.ImageField(upload_to='fault_reports/', blank=True, verbose_name="Billede")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Oprettet")
    is_resolved = models.BooleanField(default=False, verbose_name="Løst")

    def __str__(self):
        return f"Fejlrapport for {self.asset} ({self.created_at})"

    class Meta:
        verbose_name = "Fejlrapport"
        verbose_name_plural = "Fejlrapporter"
