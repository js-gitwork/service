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
            beskrivelse = data.get('beskrivelse', '')
            sprog = data.get('sprog', 'pl')  # Hent sprog fra frontend (f.eks. 'pl', 'de', 'en')

            # Oversæt beskrivelsen til dansk
            oversat_beskrivelse = oversæt(beskrivelse, fra_sprog=sprog, mål_sprog='da')

            # Gem rapporten i databasen (eksempel)
            FaultReport.objects.create(
                beskrivelse_original=beskrivelse,
                beskrivelse_oversat=oversat_beskrivelse,
                sprog=sprog,
                dato=timezone.now()
            )

            # Returner succesbesked (oversat via Django-rosetta)
            return JsonResponse({
                'status': 'success',
                'message': _('Rapport indsendt! Tak for din indsats.'),
                'oversat': oversat_beskrivelse
            })
        except Exception as e:
            # Returner fejlbesked (oversat via Django-rosetta)
            return JsonResponse({
                'status': 'error',
                'message': _('Der opstod en fejl. Prøv venligst igen.')
            }, status=400)

def save_image_from_base64(image_data, report):
    """
    Gemmer et base64-kodet billede til en FaultReport.
    Returnerer True ved succes, False ved fejl.
    """
    if not image_data:
        return False
    try:
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        filename = f"report_{report.id}_{timezone.now().timestamp()}.{ext}"
        report.image.save(filename, ContentFile(base64.b64decode(imgstr)), save=False)
        return True
    except Exception as e:
        print(f"Fejl ved gemning af billede: {e}")
        return False

def index(request):
    """Renderer forsiden (index.html)."""
    return render(request, 'index.html')

@csrf_exempt
def asset_list_api(request):
    """
    API: Returnerer liste af aktiver (VPID, name, description) som JSON.
    Søger i VPID, name OG description.
    """
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

@csrf_exempt
def submit_report(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            description = data.get('description', '')
            vpid = data.get('VPID', '')

            # Hårdkod sprog til polsk (midlertidig)
            sprog = 'pl'

            # Oversæt beskrivelsen til dansk
            translated_desc = oversæt(description, fra_sprog=sprog, mål_sprog='da')

            # Find det tilhørende Asset (hvis VPID er sendt)
            asset = Asset.objects.filter(VPID=vpid).first()

            # Opret fejlrapport med de korrekte felter
            report = FaultReport.objects.create(
                title=f"Rapport for {vpid}",
                description=translated_desc,  # Oversat beskrivelse
                original_description=description,  # Original beskrivelse
                vpid=vpid,
                asset=asset,
                image=data.get('image'),
                status="Ny",
                priority=2  # Default: Normal
            )

            return JsonResponse({
                'status': 'success',
                'report_id': report.id,
                'message': _('Rapport indsendt! Tak for din indsats.')
            })
        except Exception as e:
            print("Fejl i submit_report:", str(e))
            return JsonResponse({
                'status': 'error',
                'message': _('Der opstod en fejl. Prøv venligst igen.')
            }, status=400)


@login_required
def edit_asset(request, pk):
    """
    Rediger et aktiv via formular.
    Kræver login og gyldigt asset-id.
    """
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == "POST":
        form = AssetForm(request.POST, request.FILES, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, "Aktiv opdateret!")
            return redirect('index')  # Redirect til forsiden
    else:
        form = AssetForm(instance=asset)

    return render(request, 'assets/edit_asset.html', {
        'form': form,
        'asset': asset
    })

@login_required
def mechanic_view(request):
    """
    Vis åbne fejlrapporter tildelt den loggede ind bruger.
    Sorteret efter prioritet og oprettelsesdato.
    """
    reports = FaultReport.objects.filter(
        assigned_to=request.user,
        completed_at__isnull=True
    ).order_by('-priority', 'created_at')
    return render(request, 'assets/mechanic_view.html', {'reports': reports})

@csrf_exempt
@login_required
def update_report_status(request, report_id, action):
    """
    Opdaterer status for en fejlrapport.
    Gyldige actions: 'start' (påbegyndt), 'complete' (afsluttet).
    """
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
