from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
import json
import base64
from deep_translator import MyMemoryTranslator

from .models import Asset, FaultReport
from .forms import AssetForm

from deep_translator import MyMemoryTranslator

def translate_to_danish(text):
    """
    Oversætter tekst til dansk ved hjælp af MyMemoryTranslator.
    Returnerer originalen ved fejl.
    """
    if not text or text.strip() == "":
        return text

    try:
        # Oversæt teksten
        translated = MyMemoryTranslator(source='auto', target='da').translate(text)
        print(f"Original tekst: {text}")  # Debug: Vis original tekst
        print(f"Oversat tekst: {translated}")  # Debug: Vis oversat tekst
        return translated
    except Exception as e:
        print(f"Fejl ved oversættelse: {e}")  # Debug: Vis fejl
        return text  # Returner originalen hvis oversættelse fejler


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
    """
    API: Modtager og gemmer en ny fejlrapport.
    Oversætter beskrivelsen til dansk.
    Forventer JSON med: VPID, description, image (base64).
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Metode ikke tilladt'}, status=405)

    try:
        data = json.loads(request.body)
        vpid = data.get('VPID')
        description = data.get('description', '')

        if not vpid:
            return JsonResponse({'status': 'error', 'message': 'VPID mangler'}, status=400)

        # Oversæt beskrivelsen
        translated_desc = translate_to_danish(description)

        # Opret rapport med BEGGE beskrivelser
        report = FaultReport.objects.create(
            title=f"Fejlrapport for {vpid}",
            description=translated_desc,  # Oversat version
            original_description=description,  # Original version
            vpid=vpid,
            priority=2,  # Standard: "Normal"
            status="Ny"
        )

        # Gem billedet (hvis der er et)
        image_data = data.get('image')
        if image_data and not save_image_from_base64(image_data, report):
            print("Billedet kunne ikke gemmes.")

        report.save()
        return JsonResponse({
            'status': 'success',
            'report_id': report.id,
            'message': 'Rapport modtaget!'
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Ugyldig JSON'}, status=400)
    except Exception as e:
        print(f"Fejl i submit_report: {str(e)}")  # Debug: Vis fejl
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

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
