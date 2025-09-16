from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import models
from django.db.models import Case, When, Value, IntegerField, Q
from django.utils.translation import gettext as _
import json
import base64
from .models import Asset, FaultReport
from .forms import AssetForm
from translator import oversæt
from django.contrib.auth.models import User
from django.contrib.auth import login, logout

# Hjælpefunktion til at vise prioritet som tekst
def get_priority_display(priority):
    """Konverterer numerisk prioritet til tekst."""
    priority_map = {
        1: 'Høj',
        2: 'Mellem',
        3: 'Lav',
    }
    return priority_map.get(priority, 'Ukendt')

def asset_list_api(request):
    """API-endpoint til søgning efter aktiver (VPID, navn, beskrivelse)."""
    search_term = request.GET.get('search', '')
    if search_term:
        assets = Asset.objects.filter(
            Q(VPID__icontains=search_term) |
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term)
        ).values('VPID', 'name', 'description')
    else:
        assets = Asset.objects.all().values('VPID', 'name', 'description')
    return JsonResponse(list(assets), safe=False)

@csrf_exempt
def submit_report(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            description = data.get('description', '')
            vpid = data.get('VPID', '')
            sprog = data.get('sprog', 'de')
            image_data = data.get('image', None)
            print(f"Oversætter fra {sprog} til dansk: '{description}'")
            translated_desc = oversæt(description, fra_sprog=sprog, mål_sprog='da')
            print(f"Resultat: '{translated_desc}'")
            report = FaultReport.objects.create(
                title=f"Rapport for {vpid}",
                description=translated_desc,
                original_description=description,
                vpid=vpid,
                sprog=sprog,
                created_at=timezone.now()
            )
            if image_data:
                save_image_from_base64(image_data, report)
            return JsonResponse({
                'status': 'success',
                'report_id': report.id,
                'message': _('Rapport indsendt! Tak for din indsats.'),
                'oversat': translated_desc
            })
        except Exception as e:
            print("Fejl i submit_report:", str(e))
            return JsonResponse({
                'status': 'error',
                'message': _('Der opstod en fejl. Prøv venligst igen.')
            }, status=400)

def save_image_from_base64(image_data, report):
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
    assets = Asset.objects.all().order_by('VPID')  # Hent alle aktiver
    return render(request, 'index.html', {'assets': assets})  # Send dem til templaten

@csrf_exempt
def asset_list_api(request):
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
def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    return render(request, 'assets/asset_detail.html', {'asset': asset})

@login_required
def open_reports(request):
    """
    Viser ALLE åbne fejlrapporter, grupperet efter VPID.
    Tildelte rapporter vises øverst (sorteret efter prioritet),
    utildelte rapporter vises bagerst (også sorteret efter prioritet).
    """
    open_reports = FaultReport.objects.filter(
        completed_at__isnull=True
    ).annotate(
        # Marker tildelte med 0 (øverst), utildelte med 1 (bagerst)
        is_assigned=Case(
            When(assigned_to__isnull=False, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        ),
        # Sikker prioritering (1=Høj, 2=Mellem, 3=Lav, 4=Ukendt)
        safe_priority=Case(
            When(priority=1, then=Value(1)),
            When(priority=2, then=Value(2)),
            When(priority=3, then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by(
        'is_assigned',  # Tildelte først (0), så utildelte (1)
        'safe_priority', # Derefter efter prioritet
        '-created_at'   # Nyeste først inden for hver gruppe
    )

    # Grupper efter VPID
    reports_by_vpid = {}
    for report in open_reports:
        vpid = report.vpid
        if vpid not in reports_by_vpid:
            reports_by_vpid[vpid] = []
        reports_by_vpid[vpid].append(report)

    context = {
        'reports_by_vpid': reports_by_vpid,
        'title': 'Åbne fejlrapporter (tildelte først, sorteret efter prioritet)',
        'last_updated': timezone.now(),
        'user': request.user,
    }
    return render(request, 'open_reports.html', context)


@login_required
def repair_report(request, report_id):
    report = get_object_or_404(FaultReport, id=report_id)
    asset = get_object_or_404(Asset, VPID=report.vpid)
    repair_history = FaultReport.objects.filter(vpid=report.vpid).exclude(id=report_id).order_by('-created_at')

    if request.method == 'POST':
        # Tjek om 'complete' eller 'pause' er sendt med anmodningen
        if 'complete' in request.POST:
            report.completed_at = timezone.now()
            report.completed_by = request.user
            report.repair_status = True
            report.mechanic_report = request.POST.get('mechanic_report', '')
            report.status = 'Completed'  # Sørg for at sætte status til 'Completed'
            report.save()
            messages.success(request, f"Opgave {report.vpid} afsluttet!")
            return redirect('mechanic_reports')

        elif 'pause' in request.POST:
            report.status = 'Paused'
            report.save()
            messages.info(request, f"Opgave {report.vpid} sat på pause.")
            return redirect('mechanic_reports')

        else:
            # Hvis hverken 'complete' eller 'pause' er sendt, vis en fejl
            messages.error(request, "Ugyldig anmodning. Prøv igen.")
            return redirect('mechanic_task', report_id=report_id)

    # Håndter GET-anmodninger (vis siden)
    context = {
        'report': report,
        'asset': asset,
        'repair_history': repair_history,
    }
    return render(request, 'assets/repair_report.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Mekaniker').exists(), login_url='/accounts/login/')
def mechanic_view(request):
    # Tildelte opgaver (kun for den nuværende bruger)
    assigned_reports = FaultReport.objects.filter(
        assigned_to=request.user,
        completed_at__isnull=True
    ).order_by('priority', '-created_at')

    # Utildelte opgaver (ingen mekaniker tildelt)
    unassigned_reports = FaultReport.objects.filter(
        assigned_to__isnull=True,
        completed_at__isnull=True
    ).order_by('priority', '-created_at')

    # Hent alle mekanikere (til dropdown)
    all_mechanics = User.objects.filter(groups__name='Mekaniker')

    return render(request, 'assets/mechanic_view.html', {
        'assigned_reports': assigned_reports,
        'unassigned_reports': unassigned_reports,
        'last_updated': timezone.now(),
        'current_mechanic': request.user,  # Kun den nuværende bruger
        'all_mechanics': all_mechanics,
    })


@login_required
def mechanic_task(request, report_id):
    report = get_object_or_404(FaultReport, id=report_id)
    asset = get_object_or_404(Asset, VPID=report.vpid) if report.vpid else None
    repair_history = FaultReport.objects.filter(vpid=report.vpid).exclude(id=report_id).order_by('-created_at')
    equipment_list = asset.equipment.all() if asset else []

    # Hent mekanikere (og tving en fejl, hvis listen er tom)
    all_mechanics = list(User.objects.filter(groups__name='Mekaniker'))
    if not all_mechanics:
        raise ValueError("INGEN MEKANIKERE FUNDET! Tjek om gruppen 'Mekaniker' findes og har brugere.")
    print("DEBUG: Mekanikere sendt til template:", [u.username for u in all_mechanics])  # Skal vises i terminalen

    if request.method == 'POST':
        if 'complete' in request.POST:
            report.mechanic_report = request.POST.get('mechanic_report', '')
            report.completed_at = timezone.now()
            report.completed_by = request.user
            report.status = 'Completed'
            report.repair_status = True
            report.save()
            messages.success(request, f"Opgave {report.vpid} er afsluttet!")
            return redirect('mechanic_reports')
        elif 'pause' in request.POST:
            report.status = 'Paused'
            report.save()
            messages.info(request, f"Opgave {report.vpid} er sat på pause.")
            return redirect('mechanic_reports')

    context = {
        'report': report,
        'asset': asset,
        'equipment_list': equipment_list,
        'repair_history': repair_history,
        'all_mechanics': all_mechanics,  # Sørg for, at denne linje er til stede
    }
    return render(request, 'assets/mechanic_task.html', context)



@login_required
def assign_report_to_me(request, report_id):
    print("\n--- DEBUG assign_report_to_me ---")  # Ny linje
    print("report_id:", report_id)               # Ny linje
    print("POST data:", request.POST)            # Ny linje
    print("User:", request.user)                 # Ny linje
    try:
        report = get_object_or_404(FaultReport, id=report_id)
        print("Rapport fundet:", report.vpid)    # Ny linje
        report.assigned_to = request.user
        report.save()
        messages.success(request, f"Rapport {report.vpid} er nu tildelt dig!")
        return redirect('mechanic_reports')
    except Exception as e:
        print("FEJL:", str(e))                   # Ny linje
        raise  # Lad fejlen bubble op

@login_required
def mechanic_task(request, report_id):
    report = get_object_or_404(FaultReport, id=report_id)
    all_mechanics = User.objects.filter(groups__name='Mekaniker')  # Tilføj denne linje
    return render(request, 'assets/mechanic_task.html', {
        'report': report,
        'all_mechanics': all_mechanics,  # Tilføj denne linje
    })


@csrf_exempt
@login_required
def update_report_status(request, report_id, action):
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
        return JsonResponse({'status': 'error', 'message': 'Ugyldig handling'}, status=400
        )

@login_required
def switch_mechanic(request):
    if request.method == 'POST':
        mechanic_id = request.POST.get('mechanic_id')
        if mechanic_id:
            logout(request)  # Log ud som nuværende bruger
            mechanic = User.objects.get(pk=mechanic_id)
            mechanic.backend = 'django.contrib.auth.backends.ModelBackend'  # Krævet!
            login(request, mechanic)  # Log ind som ny mekaniker
            messages.success(request, f"Du er nu logget ind som {mechanic.get_full_name}.")
        return redirect('mechanic_reports')
    return redirect('mechanic_reports')


@login_required
def switch_back(request):
    if 'original_user_id' in request.session:
        original_user = User.objects.get(pk=request.session['original_user_id'])
        logout(request)
        original_user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, original_user)
        del request.session['original_user_id']  # Ryd sessionen
        messages.success(request, f"Velkommen tilbage!")
    return redirect('mechanic_reports')  # eller en anden standard-side

@login_required
def print_qr_view(request, asset_id):
    from io import BytesIO
    import qrcode
    import base64
    asset = get_object_or_404(Asset, id=asset_id)
    # Generer QR-kode (50x50mm = ~200x200px ved 150 DPI)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(asset.VPID)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    # Gem som base64
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    return render(request, 'assets/print_qr.html', {
        'page_title': f"QR-kode: {asset.VPID}",
        'asset': asset,
        'qr_code': qr_base64,
    })
