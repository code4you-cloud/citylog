from django.shortcuts import render

# Create your views here.
import uuid
import logging
import os
import requests

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from .forms import ReportWebForm, ReportForm
from .models import Report, get_image_path  # Assicurati di importarlo correttamente
from core.models import Users
#from utilities.ai_utils import classify_image

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.generic import ListView
from django.contrib import messages

from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

logger = logging.getLogger(__name__)

def get_exif_data(image_path):
    """Estrae i dati EXIF da un'immagine"""
    try:
        image = Image.open(image_path)
        exif_data = {}

        if hasattr(image, '_getexif') and image._getexif():
            exif = image._getexif()
            for tag, value in exif.items():
                decoded = TAGS.get(tag, tag)
                exif_data[decoded] = value

        return exif_data
    except Exception as e:
        logger.error(f"Errore nell'estrazione EXIF: {e}")
        return None

def get_gps_info(exif_data):
    """Estrae le coordinate GPS dai dati EXIF"""
    if not exif_data or 'GPSInfo' not in exif_data:
        return None

    try:
        gps_info = {}
        for key, value in exif_data['GPSInfo'].items():
            decoded = GPSTAGS.get(key, key)
            gps_info[decoded] = value

        # Conversione delle coordinate in formato decimale
        if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
            lat_data = gps_info['GPSLatitude']
            lon_data = gps_info['GPSLongitude']

            lat_ref = gps_info.get('GPSLatitudeRef', 'N')
            lon_ref = gps_info.get('GPSLongitudeRef', 'E')

            lat = float(lat_data[0]) + float(lat_data[1])/60 + float(lat_data[2])/3600
            lon = float(lon_data[0]) + float(lon_data[1])/60 + float(lon_data[2])/3600

            if lat_ref == 'S':
                lat = -lat
            if lon_ref == 'W':
                lon = -lon

            return (lat, lon)

        return None
    except Exception as e:
        logger.error(f"Errore nell'estrazione coordinate GPS: {e}")
        return None

def geocode_address(address, city=None):
    """Geocodifica un indirizzo per ottenere le coordinate"""
    try:
        query = f"{address}, {city}" if city else address
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
        headers = {"User-Agent": "CityLogApp/1.0"}

        response = requests.get(url, headers=headers)
        data = response.json()

        if data and len(data) > 0:
            return float(data[0]["lat"]), float(data[0]["lon"])
        else:
            logger.warning(f"Nessun risultato per l'indirizzo: {address}")
            return None
    except Exception as e:
        logger.error(f"Errore nella geocodifica: {e}")
        return None

def geocode_city(city):
    """Geocodifica una città per ottenere le coordinate"""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
        headers = {"User-Agent": "CityLogApp/1.0"}

        response = requests.get(url, headers=headers)
        data = response.json()

        if data and len(data) > 0:
            return float(data[0]["lat"]), float(data[0]["lon"])
        else:
            logger.warning(f"Nessun risultato per la città: {city}")
            return None
    except Exception as e:
        logger.error(f"Errore nella geocodifica: {e}")
        return None

@login_required
@require_http_methods(["GET", "POST"])
def create_report(request):
    if request.method == "GET":
        form = ReportWebForm()
        return render(request, 'report/create_report.html', {'form': form})

    form = ReportWebForm(request.POST, request.FILES)
    if not form.is_valid():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return render(request, 'report/create_report.html', {'form': form})

    city = form.cleaned_data['city']
    address = form.cleaned_data['address']
    description = form.cleaned_data['description']
    image_file = form.cleaned_data['image_file']

    logger.info(f"Ricevuta richiesta report con city={city}, address={address}")

    # RECUPERA L'UTENTE DA Users
    auth_user = request.user._wrapped if hasattr(request.user, '_wrapped') else request.user

    logger.warning(f"=== AUTH_USER ===")
    logger.warning(f"ID: {auth_user.id}")
    logger.warning(f"Username: '{auth_user.username}'")
    logger.warning(f"Email: '{auth_user.email}'")

    # 🔹 CERCA IN Users PER SOCIAL ID
    user = None
    social_id = auth_user.username

    # Prova in facebook_id
    try:
        user = Users.objects.get(facebook_id=social_id)
        logger.info(f"✅ Trovato in facebook_id: ID={user.id}")
    except (Users.DoesNotExist, AttributeError):
        pass

    # Prova in google_id
    if not user:
        try:
            user = Users.objects.get(google_id=social_id)
            logger.info(f"✅ Trovato in google_id: ID={user.id}")
        except (Users.DoesNotExist, AttributeError):
            pass

    # Prova in username con prefisso
    if not user:
        # Prova con fb_
        try:
            user = Users.objects.get(username=f"fb_{social_id}")
            logger.info(f"✅ Trovato in username con fb_: ID={user.id}")
        except Users.DoesNotExist:
            pass

    if not user:
        # Prova con google_
        try:
            user = Users.objects.get(username=f"google_{social_id}")
            logger.info(f"✅ Trovato in username con google_: ID={user.id}")
        except Users.DoesNotExist:
            pass

    # Prova per email (se esiste)
    if not user and auth_user.email:
        try:
            user = Users.objects.get(email=auth_user.email)
            logger.info(f"✅ Trovato per email: ID={user.id}")
        except Users.DoesNotExist:
            pass

    if not user:
        logger.error(f"❌ UTENTE NON TROVATO! social_id='{social_id}', email='{auth_user.email}'")
        messages.error(request, "Utente non trovato nel sistema")
        return redirect('login')

    logger.warning(f"=== UTENTE TROVATO ===")
    logger.warning(f"ID: {user.id}")
    logger.warning(f"Username: {user.username}")
    logger.warning(f"Email: {user.email}")

    # Genera UUID
    image_id = str(uuid.uuid4())
    image_time = timezone.now()

    # Estrai coordinate
    latitude, longitude = None, None

    if image_file:
        exif_data = get_exif_data(image_file.file)
        gps_info = get_gps_info(exif_data) if exif_data else None
        if gps_info:
            latitude, longitude = gps_info

    if not (latitude and longitude) and address:
        geo_result = geocode_address(address, city)
        if geo_result:
            latitude, longitude = geo_result

    if not (latitude and longitude) and city:
        geo_result = geocode_city(city)
        if geo_result:
            latitude, longitude = geo_result

    # Crea report
    report = Report(
        user=user,
        latitude=latitude,
        longitude=longitude,
        city=city or 'Sconosciuta',
        address=address,
        image_time=image_time,
        image_id=image_id,
        image_file=image_file if image_file else None,
        status="pending",
        typo="web",
        description=description,
    )

    report.save()
    logger.info(f"✅ Report salvato: ID={report.id}, user_id={report.user_id}")

    if report.image_file:
        report.image_url = report.image_file.url
        report.save(update_fields=['image_url'])

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Segnalazione inviata con successo',
            'report_id': report.id
        })

    messages.success(request, 'Segnalazione inviata con successo!')
    return redirect(reverse('reports:report_success', kwargs={'report_id': report.id}))

def report_success(request, report_id):
    # Ottieni il report dal database (opzionale, se vuoi mostrare ulteriori dettagli)
    report = get_object_or_404(Report, id=report_id)

    # Passa l'ID troncato (o altri dettagli) al template
    image_id = str(report.image_id)[:6]  # Tronca l'ID ai primi 6 caratteri
    context = {
        'report': report,
        'report_id': report.id,
        'image_id': report.image_id,
        'image_file': report.image_file,
    }

    return render(request, 'report/report_success.html', context)

@login_required
def confirm_report(request, report_id):
    """Permette a un utente di confermare una segnalazione."""
    report = get_object_or_404(Report, id=report_id)

    if report.confirmations.filter(username=request.user).exists():
    #if request.user in report.confirmations.filter.all():
        return JsonResponse({"error": "Hai già confermato questa segnalazione."}, status=400)

    report.confirm_report(request.user)
    return JsonResponse({"message": "Segnalazione confermata!", "confirmations": report.confirmations.count(), "status": report.status})

@login_required
@csrf_exempt  # Rimuovilo se usi il CSRF token
def delete_report_(request, report_id):
    if request.method == "DELETE":
        report = get_object_or_404(Report, id=report_id)
        report.delete()
        return JsonResponse({"success": True, "message": "Report eliminato"})
    return JsonResponse({"error": "Metodo non consentito"}, status=405)

@login_required
def delete_report(request, report_id):
    """Permette all'utente che ha creato la segnalazione o a un admin di eliminarla."""
    report = get_object_or_404(Report, id=report_id)

    if not report.delete_report(request.user):
        return JsonResponse({"error": "Non hai i permessi per eliminare questa segnalazione."}, status=403)

    return JsonResponse({"message": "Segnalazione eliminata con successo!"})

class ReportListView(ListView):
    model = Report
    template_name = "report/report_list.html"  # Template da usare
    context_object_name = "reports"  # Nome del contesto nel template
    paginate_by = 20  # Opzionale: paginazione

    def get_queryset(self):
        # Ottieni il queryset di base
        queryset = super().get_queryset()

        # Ordina i report per image_time in ordine decrescente (dal più recente al più vecchio)
        queryset = queryset.order_by('-image_time')

        return queryset

    def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)

         # Ottieni il parametro dalla query string (es. ?tipo=ambiente)
         page_type = self.request.GET.get("typo", "default")

         # Definisci i titoli e le descrizioni in base al tipo di pagina
         page_titles = {
             "ambiente": ("Monitoraggio Ambientale", "Scopri le segnalazioni ambientali nella tua città."),
             "rete": ("Rete Stradale", "Partecipa alla segnalazione della rete stradale."),
             "rifiuti": ("Monitoraggio Rifiuti", "Partecipa alla segnalazione dei rifiuti de.allocati nell'ambiente cittadino."),
             "web": ("Segnalazioni da Sito", "Partecipa come cittadino alle segnalazioni della tua citta+."),
             "default": ("CityLog", "Citylog è una piattaforma civica che coinvolge i cittadini nel monitoraggio ambientale della propria \
                         città. Tramite citylog app, è possibile segnalare violazioni sui rifiuti, ambiente, buche/dissesti, inquinamento ambientale."),
         }

         # Imposta i valori di default se il tipo non è riconosciuto
         context["page_title"], context["page_description"] = page_titles.get(page_type, page_titles["default"])
         context["page_type"] = page_type if page_type in page_titles else "default" # Passa il tipo per gestire l'icona nel template
         context["MEDIA_URL"] = settings.MEDIA_URL  # Passa MEDIA_URL al template
         return context



