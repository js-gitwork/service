from django.shortcuts import render
from django.urls import reverse
from django.utils.html import format_html
import io
import qrcode
from django.http import HttpResponse
import base64
from .models import Asset  # Importer Asset her (undgå import inde i funktioner)

def qr_print_button(obj):
    """Knappen vises altid (da vi genererer QR dynamisk)."""
    return format_html(
        '<a href="{}" target="_blank" class="button">Print QR</a>',
        reverse('print_qr', args=[obj.id])  # Brug 'print_qr' (ikke 'admin:print_qr')
    )

def print_qr_view(request, asset_id):
    """
    Generer QR-kode i 5x5 cm (300 DPI = 590x590 px) med VPID.
    Returnerer en side med QR-koden og aktivets informationer.
    """
    try:
        asset = Asset.objects.get(id=asset_id)
    except Asset.DoesNotExist:
        return HttpResponse("Aktiv ikke fundet", status=404)

    # Opret QR-kode (størrelse tilpasset 5x5 cm @ 300 DPI = 590x590 px)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,  # Justeret for at passe til 5x5 cm (box_size * (2*border + version*25) = størrelse)
        border=2,
    )
    qr.add_data(f"VPID: {asset.VPID}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Gem som PNG i memory
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Returner template med QR-kode og aktivets data
    return render(request, 'assets/print_qr.html', {
        'asset': asset,
        'qr_code': qr_base64,
        'page_title': f"QR-kode for {asset.VPID} - {asset.name}"
    })
