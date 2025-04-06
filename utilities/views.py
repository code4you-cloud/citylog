from django.shortcuts import render, redirect

# Create your views here.
from .models import Segnalazione
from .ai_utils import classify_image
from .predizione_rifiuti import prevedi_zone_critiche
from datetime import date

def nuova_segnalazione(request):
    if request.method == "POST":
        immagine = request.FILES.get('immagine')
        segnalazione = Segnalazione.objects.create(immagine=immagine)

        # Classificazione AI
        categoria_predetta = classify_image(segnalazione.immagine.path)
        segnalazione.categoria = categoria_predetta
        segnalazione.save()

        return redirect('citylog:lista_segnalazioni')

    return render(request, "citylog/nuova_segnalazione.html")


from .predizione_rifiuti import prevedi_zone_critiche
from datetime import date

def analisi_predittiva(request):
    risultato = prevedi_zone_critiche(str(date.today()))
    return render(request, "citylog/analisi.html", {"risultato": risultato})


