from django.shortcuts import render

# Create your views here.
import uuid
import logging
import os
import requests

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .forms import ReportWebForm
from .models import Report
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from django.conf import settings

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

@require_http_methods(["GET", "POST"])
def create_report(request):
    if request.method == "POST":
        form = ReportWebForm(request.POST, request.FILES)

        if form.is_valid():
            city = form.cleaned_data['city']
            address = form.cleaned_data['address']
            upload_image = form.cleaned_data.get('upload_image')

            logger.info(f"Ricevuta richiesta freeweb con city={city}, address={address}")

            # Genera un UUID per image_id
            image_id = str(uuid.uuid4())

            # Coordiante e timestamp
            latitude, longitude = None, None
            image_time = datetime.now()

            # Se c'è un'immagine, estrai i dati EXIF
            file_path = None
            if upload_image:
                # Salva temporaneamente l'immagine
                #file_path = f"temp/{upload_image.name}"
                #os.makedirs("temp", exist_ok=True)

                temp_dir = os.path.join(settings.MEDIA_ROOT, "uploaded_images/report")
                os.makedirs(temp_dir, exist_ok=True)

                # Percorso completo del file
                file_path = os.path.join(temp_dir, upload_image.name)

                with open(file_path, "wb+") as destination:
                    for chunk in upload_image.chunks():
                        destination.write(chunk)

                # Estrai dati EXIF e coordinate GPS
                exif_data = get_exif_data(file_path)
                gps_info = get_gps_info(exif_data) if exif_data else None

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
                latitude=latitude,
                longitude=longitude,
                city=city or 'Sconosciuta',
                address=address,
                image_time=image_time,
                image_id=image_id,
                image_url=None,
                image_file=upload_image if upload_image else None,
                status="pending",
                typo="web",
            )
            report.save()

            # Pulisci il file temporaneo se necessario
            if file_path and os.path.exists(file_path):
                os.remove(file_path)

            logger.info(f"Report salvato con successo, ID: {report.id}")

            # Se la richiesta vuole JSON, restituisci JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Segnalazione inviata con successo',
                    'report_id': report.id
                })

            # Altrimenti, reindirizza con messaggio di successo
            from django.contrib import messages
            messages.success(request, 'Segnalazione inviata con successo!')
            return redirect('report_success')

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

def report_success(request):
    return render(request, 'report/report_success.html')
