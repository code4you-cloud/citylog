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

from .forms import ReportWebForm, ReportForm
from .models import Report, get_image_path  # Assicurati di importarlo correttamente
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

#def create_report_(request):
#    if request.method == "POST":
#        form = ReportForm(request.POST, request.FILES)
#        if form.is_valid():
#            report = form.save()  # il file sarà salvato in remoto grazie a CustomRemoteStorage
#            return redirect(reverse('reports:report_success', kwargs={'report_id': report.id}))
#    else:
#        form = ReportForm()
#    return render(request, 'report/create_report.html', {'form': form})
#

@login_required
@require_http_methods(["GET", "POST"])
def create_report(request):
    if request.method == "POST":
        form = ReportWebForm(request.POST, request.FILES)

        if form.is_valid():
            city = form.cleaned_data['city']
            address = form.cleaned_data['address']
            description = form.cleaned_data['description']
            image_file = form.cleaned_data['image_file']

            logger.info(f"Ricevuta richiesta freeweb con city={city}, address={address}")

            # Genera un UUID per image_id
            image_id = str(uuid.uuid4())

            # Coordiante e timestamp
            latitude, longitude = None, None
            image_time = datetime.now()

            # Se c'è un'immagine, estrai i dati EXIF
            file_path = None
            if image_file:
                # Salva temporaneamente l'immagine
                #file_path = f"temp/{upload_image.name}"
                #os.makedirs("temp", exist_ok=True)

                ##temp_dir = os.path.join(settings.MEDIA_ROOT, "uploaded_images/report")
                ##os.makedirs(temp_dir, exist_ok=True)

                # Percorso completo del file
                ##file_path = os.path.join(temp_dir, upload_image.name)

                ##with open(file_path, "wb+") as destination:
                ##    for chunk in upload_image.chunks():
                ##        destination.write(chunk)

                # Estrai dati EXIF e coordinate GPS
                exif_data = get_exif_data(image_file.file)
                gps_info = get_gps_info(exif_data) if exif_data else None
                #exif_data = get_exif_data(file_path)
                #gps_info = get_gps_info(exif_data) if exif_data else None

                if gps_info:
                    latitude, longitude = gps_info
                    logger.info(f"Coordinate da EXIF: {latitude}, {longitude}")

            # Se non abbiamo coordinate dall'EXIF, geocodifica l'indirizzo
            if not (latitude and longitude) and address:
                geo_result = geocode_address(address, city)
                if geo_result:
                    latitude, longitude = geo_result
                    logger.info(f"Coordinate da indirizzo: {latitude}, {longitude}")

            # Se ancora non abbiamo coordinate, geocodifica la città
            if not (latitude and longitude) and city:
                geo_result = geocode_city(city)
                if geo_result:
                    latitude, longitude = geo_result
                    logger.info(f"Coordinate da città: {latitude}, {longitude}")

            # Crea e salva il report
            report = Report(
                user=request.user,  # 🔹 Associa il report all'utente autenticato
                latitude=latitude,
                longitude=longitude,
                city=city or 'Sconosciuta',
                address=address,
                image_time=image_time,
                image_id=image_id,
                #image_url=None,
                #image_url=image_file.url if image_file.url else None,
                image_file=image_file if image_file else None,
                status="pending",
                typo="web",
                description=description,
            )

            # Classificazione AI Enable AI
            #categoria_predetta = classify_image(segnalazione.immagine.path)
            #report.typo = categoria_predetta

            #report.save()

            # Ora assegna il valore corretto a image_url e salva di nuovo
            if report.image_file:
                report.image_url = report.image_file.url
                #report.image_url = f"{get_image_path(report, image_file.name)}"
                report.save()
                logger.warning(f"Risultato per image_file: {report.image_file}")
                logger.warning(f"Risultato per image_file_url: {report.image_file.url}")

            # Pulisci il file temporaneo se necessario
            #if file_path and os.path.exists(file_path):
            #    os.remove(file_path)

            #logger.info(f"Report salvato con successo, ID: {report.id}")

            # Se la richiesta vuole JSON, restituisci JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Segnalazione inviata con successo',
                    'report_id': report.id
                })

            # Altrimenti, reindirizza con messaggio di successo
            messages.success(request, 'Segnalazione inviata con successo!')

            # Reindirizza alla pagina di successo con l'ID del report
            return redirect(reverse('reports:report_success', kwargs={'report_id': report.id}))
            #return redirect('reports:report_success')

        else:
            # Se ci sono errori di validazione
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'errors': form.errors
                }, status=400)
    else:
        # GET: mostra il form vuoto
        form = ReportWebForm()

    return render(request, 'report/create_report.html', {'form': form})

def report_success(request, report_id):
    # Ottieni il report dal database (opzionale, se vuoi mostrare ulteriori dettagli)
    report = get_object_or_404(Report, id=report_id)

    # Passa l'ID troncato (o altri dettagli) al template
    image_id = str(report.image_id)[:6]  # Tronca l'ID ai primi 6 caratteri
    context = {
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



