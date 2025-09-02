import qrcode
from io import BytesIO
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.utils.html import format_html
from django.urls import reverse
from .models import Asset
import base64

def generate_qr_code(data):
    """Generer en QR-kode og returner som bytes."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def qr_print_button(obj):
    """Knappen vises i admin-listen for at printe QR-kode."""
    return format_html(
        '<a href="{}" target="_blank" class="button">Print QR</a>',
        reverse('print_qr', args=[obj.id])
    )

def print_qr_view(request, asset_id):
    """Vis en side med QR-kode for det valgte aktiv."""
    try:
        asset = Asset.objects.get(id=asset_id)
    except Asset.DoesNotExist:
        return HttpResponse("Aktiv ikke fundet", status=404)

    qr_data = generate_qr_code(f"VPID: {asset.VPID}")
    qr_base64 = base64.b64encode(qr_data).decode("utf-8")

    return render(request, 'assets/print_qr.html', {
        'asset': asset,
        'qr_code': qr_base64,
        'page_title': f"QR-kode for {asset.VPID} - {asset.name}"
    })
