# rifiuti/views.py

from django.views.generic import TemplateView, View
from django.http import JsonResponse
import json

# ✅ Importa il modello CORRETTO
from .models import EmailsEmaildata  # ← Questo è il modello giusto!
from .services import StatisticheService

class StatisticheDashboardView(TemplateView):
    template_name = 'rifiuti/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        service = StatisticheService()

        # KPI rifiuti
        context['kpi'] = service.get_kpi().to_dict()

        # Grafici rifiuti
        context['chart_attuali_data'] = json.dumps(service.get_trend())
        context['chart_tipologia_data'] = json.dumps(service.get_tipologie())
        context['chart_quartieri_data'] = json.dumps(service.get_quartieri())

        # ✅ NUOVE METRICHE PER RIFIUTI
        context['medie_temporali'] = service.get_medie_temporali()
        context['top_indirizzi'] = service.get_top_indirizzi(10)

        # Lista quartieri (solo quelli con rifiuti)
        context['quartieri_list'] = list(
            EmailsEmaildata.objects.using('segnalazioni_db')
            .filter(typo='rifiuti')
            .values_list('quartiere', flat=True)
            .distinct()
        )

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
