# rifiuti/views.py
import json

from django.views.generic import TemplateView, ListView, DetailView, View
from django.http import JsonResponse

from django.shortcuts import render, redirect

# ✅ Importa il modello CORRETTO
# per evitare conflitto con from .models import EmailsEmaildata  # ← Questo è il modello giusto!
from rifiuti.models import EmailsEmaildata
#from .models import EmailsEmaildata  # ← Questo è il modello giusto!
from .services import StatisticheService

# Vista per la lista di segnalazioni rifiuti
class StradeListView(ListView):
     model = EmailsEmaildata
     template_name = "strade/emailsemaildata_list.html"
     context_object_name = "segnalazioni"

     def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)

         # Ottieni il parametro dalla query string (es. ?tipo=ambiente)
         page_type = self.request.GET.get("typo", "default")

         # Definisci i titoli e le descrizioni in base al tipo di pagina
         page_titles = {
            "strade": ("Log.Strade", "Monitora le tue strade, i dissesti stradali pericolosi per la tua incolumità e viabilità."),
            "default": ("CityLog", "Citylog è una piattaforma civica..."),
         }

         # Imposta i valori di default se il tipo non è riconosciuto
         context["page_title"], context["page_description"] = page_titles.get(page_type, page_titles["default"])
         context["page_type"] = page_type if page_type in page_titles else "default" # Passa il tipo per gestire l'icona nel template
         return context

     def get_queryset(self):
         queryset = super().get_queryset()
         tipo = self.request.GET.get("typo")
         if tipo == "strade":
             queryset = queryset.filter(typo__in=["strade"])
         else:
             queryset = queryset.filter(typo=tipo)

         # Ordina il queryset per image_time in ordine decrescente
         queryset = queryset.order_by('-image_time')

         return queryset

# Vista per il dettaglio di una segnalazione specifica
class StradeDetailView(DetailView):
    model = EmailsEmaildata
    template_name = "strade/rifiuti_detail.html"
    context_object_name = "segnalazione"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['MEDIA_URL'] = settings.MEDIA_URL  # Passa MEDIA_URL al template
        return context

class StatisticheDashboardView(TemplateView):
    template_name = 'strade/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ✅ Definisci i tipi per STRADE
        STRADE_TIPI = ["strade", "buche", "dissesto"]

        service = StatisticheService()

        # KPI
        context['kpi'] = service.get_kpi(typo_list=STRADE_TIPI)

        # Grafici
        context['chart_attuali_data'] = json.dumps(
            service.get_trend(typo_list=STRADE_TIPI),
            default=str
        )
        context['chart_tipologia_data'] = json.dumps(
            service.get_tipologie(typo_list=STRADE_TIPI),
            default=str
        )
        context['chart_quartieri_data'] = json.dumps(
            service.get_quartieri(typo_list=STRADE_TIPI),
            default=str
        )

        # Top indirizzi
        context['top_indirizzi'] = service.get_top_indirizzi(10, typo_list=STRADE_TIPI)

        # Lista quartieri (solo con tipi STRADE)
        context['quartieri_list'] = list(
            EmailsEmaildata.objects.using('segnalazioni_db')
            .filter(typo__in=STRADE_TIPI)
            .values_list('quartiere', flat=True)
            .distinct()
        )

        # ✅ Statistiche per singolo tipo (STRADE)
        context['statistiche_per_tipo'] = {
            'strade': EmailsEmaildata.objects.using('segnalazioni_db')
                .filter(typo='strade').count(),
            'buche': EmailsEmaildata.objects.using('segnalazioni_db')
                .filter(typo='buche').count(),
            'dissesto': EmailsEmaildata.objects.using('segnalazioni_db')
                .filter(typo='dissesto').count(),
        }

        # ✅ Totale segnalazioni strade
        context['totale_strade'] = EmailsEmaildata.objects.using('segnalazioni_db') \
            .filter(typo__in=STRADE_TIPI).count()

        return context

class StatisticheAPIView(View):
    def get(self, request, *args, **kwargs):
        action = request.GET.get('action', 'dashboard')
        quartiere = request.GET.get('quartiere')

        service = StatisticheService()

        # ✅ FILTRA IL QUERYSET UNA VOLTA PER TUTTE
        if quartiere and quartiere != 'all':
            service.queryset = service.queryset.filter(quartiere=quartiere)

        actions = {
            'kpi': lambda: service.get_kpi().to_dict(),
            'trend': lambda: service.get_trend(),
            'tipologie': lambda: service.get_tipologie(),
            'quartieri': lambda: service.get_quartieri(),
            'top_indirizzi': lambda: service.get_top_indirizzi(10),  # ✅ USA service già filtrato
            'dashboard': lambda: self._get_dashboard_data(service),  # ✅ USA service già filtrato
        }

        data = actions.get(action, lambda: {'error': 'Azione non valida'})()
        return JsonResponse(data)

    def _get_dashboard_data(self, service):
        """Raccoglie tutti i dati per la dashboard (service è già filtrato)"""
        return {
            'kpi': service.get_kpi().to_dict(),
            'trend': service.get_trend(),
            'tipologie': service.get_tipologie(),
            'quartieri': service.get_quartieri(),
            'top_indirizzi': service.get_top_indirizzi(10),  # ✅ service già filtrato
        }
