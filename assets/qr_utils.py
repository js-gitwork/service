from django.shortcuts import render
from django.urls import reverse
from django.utils.html import format_html
import io
import qrcode
from django.http import HttpResponse
import base64

def qr_print_button(obj):
    """Knappen vises altid (da vi genererer QR dynamisk)."""
    return format_html(
        '<a href="{}" target="_blank" class="button">📷 Print QR</a>',
        reverse('admin:print_qr', args=[obj.id])
    )

def print_qr_view(request, asset_id):
    """Generer QR-kode i 5x5 cm (300 DPI) med VPID under."""
    from .models import Asset
    asset = Asset.objects.get(id=asset_id)

    # Opret QR-kode (størrelse tilpasset 5x5 cm @ 300 DPI = 590x590 px)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,  # Juster for at fylde 5x5 cm
        border=2,
    )
    qr.add_data(f"VPID: {asset.VPID}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Gem som PNG i memory
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return render(request, 'assets/print_qr.html', {
        'asset': asset,
        'qr_code': qr_base64,
    })
