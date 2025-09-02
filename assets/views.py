from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import json
import base64
from .models import Asset, FaultReport
from .forms import AssetForm

# --- Hjælpefunktioner ---
def save_image_from_base64(image_data, report):
    """Gem base64-billede som ImageField."""
    if not image_data:
        return
    try:
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        report.image.save(
            f"report_{report.id}_{timezone.now().timestamp()}.{ext}",
            ContentFile(base64.b64decode(imgstr)),
            save=False
        )
    except Exception as e:
        print(f"Kunne ikke gemme billede: {e}")

# --- API: Hent liste af aktiver (JSON) ---
@csrf_exempt
def asset_list_api(request):
    """Returner liste af aktiver som JSON (til mobilappen)."""
    assets = Asset.objects.values('VPID', 'name', 'id')
    return JsonResponse(list(assets), safe=False)

# --- API: Indsend fejlrapport ---
@csrf_exempt
def submit_report(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Metode ikke tilladt'}, status=405)

    try:
        data = json.loads(request.body)
        vpid = data.get('VPID')
        description = data.get('description', '')
        image_data = data.get('image')

        # Opret rapporten
        report = FaultReport.objects.create(
            title=f"Fejlrapport for {vpid}",
            description=description,
            vpid=vpid,
            priority=2,  # Standard-prioritet ("Normal")
            status="Ny"
        )

        # Gem billedet (hvis der er et)
        if image_data:
            save_image_from_base64(image_data, report)
            report.save()  # Gem igen for at sikre billedet bliver gemt

        return JsonResponse({
            'status': 'success',
            'report_id': report.id
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

# --- Vis liste af aktiver (HTML) ---
def asset_list(request):
    """Vis liste af aktiver i browser (med fokuseret aktiv)."""
    assets = Asset.objects.all().order_by('VPID')
    focus_id = request.GET.get('focus', None)
    return render(request, 'assets/assets_list.html', {
        'assets': assets,
        'focus_id': focus_id
    })

# --- Rediger aktiv ---
def edit_asset(request, pk):
    """Rediger et aktiv via formular."""
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == "POST":
        form = AssetForm(request.POST, request.FILES, instance=asset)
        if form.is_valid():
            form.save()
            return redirect('asset_list')
    else:
        form = AssetForm(instance=asset)
    return render(request, 'assets/edit_asset.html', {
        'form': form,
        'asset': asset
    })

# --- Mekaniker-visning ---
@login_required
def mechanic_view(request):
    """Vis tildelte fejlrapporter til mekanikeren."""
    reports = FaultReport.objects.filter(
        assigned_to=request.user,
        completed_at__isnull=True  # Kun ikke-afsluttede
    ).order_by('-priority', 'created_at')
    return render(request, 'mechanic_reports.html', {'reports': reports})

# --- Opdater rapport-status ---
@csrf_exempt
@login_required
def update_report_status(request, report_id, action):
    """Markér rapport som påbegyndt/afsluttet."""
    report = get_object_or_404(FaultReport, id=report_id)

    if action == 'start':
        report.started_at = timezone.now()
        report.save()
        return JsonResponse({'status': 'success'})

    elif action == 'complete':
        report.completed_at = timezone.now()
        report.completed_by = request.user
        report.repair_status = True
        report.save()
        return JsonResponse({'status': 'success'})

    else:
        return JsonResponse({'status': 'error', 'message': 'Ugyldig handling'}, status=400)
