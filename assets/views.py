from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.utils.translation import gettext as _
import json
import base64
from .models import Asset, FaultReport
from .forms import AssetForm
from translator import oversæt

@csrf_exempt
def submit_report(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            description = data.get('description', '')
            vpid = data.get('VPID', '')
            sprog = data.get('sprog', 'de')  # Default: tysk
            image_data = data.get('image', None)

            # DEBUG: Vis input
            print(f"Oversætter fra {sprog} til dansk: '{description}'")

            # Oversæt beskrivelsen
            translated_desc = oversæt(description, fra_sprog=sprog, mål_sprog='da')

            # DEBUG: Vis output
            print(f"Resultat: '{translated_desc}'")

            # Opret rapporten...
            report = FaultReport.objects.create(
                title=f"Rapport for {vpid}",
                description=translated_desc,
                original_description=description,  # Gem originalen!
                vpid=vpid,
                sprog=sprog
            )

            # Gem billede (hvis sendt)
            if image_data:
                save_image_from_base64(image_data, report)
                report.save()

            # Sikrer korrekt encoding af specialtegn (æ, ø, å) i JSON-svar
            return JsonResponse({
                'status': 'success',
                'report_id': report.id,
                'message': _('Rapport indsendt! Tak for din indsats.'),
                'oversat': translated_desc  # Ingen ekstra encoding nødvendig (Django håndterer UTF-8 automatisk)
            })

        except Exception as e:
            print("Fejl i submit_report:", str(e))
            return JsonResponse({
                'status': 'error',
                'message': _('Der opstod en fejl. Prøv venligst igen.')
            }, status=400)


def save_image_from_base64(image_data, report):
    """Gemmer et base64-kodet billede til en FaultReport."""
    if not image_data:
        return False
    try:
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        filename = f"report_{report.id}_{timezone.now().timestamp()}.{ext}"
        report.image.save(filename, ContentFile(base64.b64decode(imgstr)), save=True)
        return True
    except Exception as e:
        print(f"Fejl ved gemning af billede: {e}")
        return False

def index(request):
    """Renderer forsiden (index.html)."""
    return render(request, 'index.html')

@csrf_exempt
def asset_list_api(request):
    """API: Returnerer liste af aktiver (VPID, name, description) som JSON."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Metode ikke tilladt'}, status=405)
    search_term = request.GET.get('search', '')
    if search_term:
        assets = Asset.objects.filter(
            models.Q(VPID__icontains=search_term) |
            models.Q(name__icontains=search_term) |
            models.Q(description__icontains=search_term)
        ).values('VPID', 'name', 'id', 'description')
    else:
        assets = Asset.objects.all().values('VPID', 'name', 'id', 'description')
    return JsonResponse(list(assets), safe=False)

@login_required
def edit_asset(request, pk):
    """Rediger et aktiv via formular."""
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == "POST":
        form = AssetForm(request.POST, request.FILES, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, "Aktiv opdateret!")
            return redirect('index')
    else:
        form = AssetForm(instance=asset)
    return render(request, 'assets/edit_asset.html', {'form': form, 'asset': asset})

@login_required
def mechanic_view(request):
    """Vis åbne fejlrapporter tildelt den loggede ind bruger."""
    reports = FaultReport.objects.filter(
        assigned_to=request.user,
        completed_at__isnull=True
    ).order_by('-priority', 'created_at')
    return render(request, 'assets/mechanic_view.html', {'reports': reports})

@csrf_exempt
@login_required
def update_report_status(request, report_id, action):
    """Opdaterer status for en fejlrapport."""
    report = get_object_or_404(FaultReport, id=report_id)
    if action == 'start':
        report.started_at = timezone.now()
        report.save()
        return JsonResponse({'status': 'success', 'message': 'Rapport påbegyndt'})
    elif action == 'complete':
        report.completed_at = timezone.now()
        report.completed_by = request.user
        report.repair_status = True
        report.save()
        return JsonResponse({'status': 'success', 'message': 'Rapport afsluttet'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Ugyldig handling'}, status=400)
