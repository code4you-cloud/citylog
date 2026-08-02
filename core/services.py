# rifiuti/services.py - VERSIONE CORRETTA

from dataclasses import dataclass
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from core.models import EmailsEmaildata
import json  # ✅ Aggiungi questo import

@dataclass
class KPIMetrics:
    totale: int
    in_attesa: int
    risolte: int

    def to_dict(self):
        return {
            'totale': self.totale,
            'in_attesa': self.in_attesa,
            'risolte': self.risolte
        }

class StatisticheService:
    def __init__(self, queryset=None):
        # ✅ FILTRA SOLO RIFIUTI!
        if queryset is None:
            self.queryset = EmailsEmaildata.objects.using('segnalazioni_db').filter(typo='rifiuti')
        else:
            self.queryset = queryset.filter(typo='rifiuti')

        print(f"🔍 Segnalazioni rifiuti: {self.queryset.count()}")

    # ❌ RIMUOVI QUESTO METODO - NON DEVE ESSERE QUI!
    # def get_context_data(self, **kwargs):
    #     ...

    def get_kpi(self) -> KPIMetrics:
        oggi = timezone.now().date()
        trenta_giorni_fa = oggi - timedelta(days=30)

        return KPIMetrics(
            totale=self.queryset.count(),
            in_attesa=self.queryset.filter(status__in=['in_attesa', 'in_lavorazione']).count(),
            risolte=self.queryset.filter(status='risolta', image_time__date__gte=trenta_giorni_fa).count()
        )

    # rifiuti/services.py

    def get_trend(self, days=365):  # ← CAMBIA DA 30 A 365 (o più)
        """Trend solo per rifiuti - ultimi `days` giorni"""
        start_date = timezone.now().date() - timedelta(days=days)
        data = (
            self.queryset
            .filter(image_time__date__gte=start_date)
            .values('image_time__date')
            .annotate(count=Count('id'))
            .order_by('image_time__date')
        )
        return {
            'labels': [d['image_time__date'].strftime('%Y-%m-%d') for d in data],
            'series': [d['count'] for d in data]
        }

    def get_trend_(self, days=30):
        """Trend solo per rifiuti"""
        start_date = timezone.now().date() - timedelta(days=days)
        data = (
            self.queryset
            .filter(image_time__date__gte=start_date)
            .extra(select={'date': "DATE(image_time)"})
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        return {
            'labels': [d['date'].strftime('%Y-%m-%d') for d in data],
            'series': [d['count'] for d in data]
        }

    def get_tipologie(self):
        """Solo rifiuti (ma già filtrato)"""
        data = (
            self.queryset
            .values('typo')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        return {
            'labels': [d['typo'] for d in data],
            'series': [d['count'] for d in data]
        }

    def get_quartieri(self):
        """Distribuzione rifiuti per quartiere"""
        quartieri = self.queryset.values_list('quartiere', flat=True).distinct()
        result = {}

        for q in quartieri:
            if not q:
                continue

            stats = (
                self.queryset
                .filter(quartiere=q)
                .values('typo')
                .annotate(count=Count('id'))
            )

            result[q] = [s['count'] for s in stats if s['typo'] == 'rifiuti']
            if not result[q]:
                result[q] = [0]

        return result

    def get_medie_temporali(self):
        """Medie giornaliere/settimanali/mensili per rifiuti"""
        oggi = timezone.now().date()

        ultimi_7 = oggi - timedelta(days=7)
        media_giornaliera = self.queryset.filter(image_time__date__gte=ultimi_7).count() / 7

        ultime_4_settimane = oggi - timedelta(weeks=4)
        media_settimanale = self.queryset.filter(image_time__date__gte=ultime_4_settimane).count() / 4

        ultimi_6_mesi = oggi - timedelta(days=180)
        media_mensile = self.queryset.filter(image_time__date__gte=ultimi_6_mesi).count() / 6

        return {
            'giornaliera': round(media_giornaliera, 1),
            'settimanale': round(media_settimanale, 1),
            'mensile': round(media_mensile, 1)
        }

    def get_top_indirizzi(self, limit=10, quartiere=None):
        """
        Top indirizzi con più segnalazioni rifiuti
        Ora restituisce anche latitudine e longitudine di una segnalazione per la via
        """
        qs = self.queryset

        if quartiere and quartiere != 'all':
            qs = qs.filter(quartiere=quartiere)

        # Ottieni il conteggio per indirizzo
        top_indirizzi = (
            qs
            .values('address')
            .annotate(totale=Count('id'))
            .order_by('-totale')[:limit]
        )

        # Arricchisce ogni risultato con le coordinate
        result = []
        for item in top_indirizzi:
            segnalazione = qs.filter(address=item['address']).first()
            if segnalazione:
                item['latitude'] = segnalazione.latitude
                item['longitude'] = segnalazione.longitude
            else:
                item['latitude'] = ''
                item['longitude'] = ''
            result.append(item)

        return result

class QuartieriService:
    """Servizio per gestire i quartieri a livello globale (TUTTI i dati)"""

    def __init__(self, queryset=None):
        if queryset is None:
            self.queryset = EmailsEmaildata.objects.using('segnalazioni_db').all()
        else:
            self.queryset = queryset

    def get_quartieri_list(self):
        quartieri = (
            self.queryset
            .values('quartiere')
            .annotate(totale=Count('id'))
            .exclude(quartiere__isnull=True)
            .exclude(quartiere='')
            .order_by('-totale')
        )
        return list(quartieri)

    def get_quartieri_detailed(self):
        quartieri = {}

        dati = (
            self.queryset
            .values('quartiere', 'typo')
            .annotate(count=Count('id'))
            .exclude(quartiere__isnull=True)
            .exclude(quartiere='')
        )

        for item in dati:
            quartiere = item['quartiere']
            typo = item['typo']
            count = item['count']

            if quartiere not in quartieri:
                quartieri[quartiere] = {
                    'nome': quartiere,
                    'totale': 0,
                    'tipologie': {}
                }

            quartieri[quartiere]['totale'] += count
            quartieri[quartiere]['tipologie'][typo] = count

        return sorted(quartieri.values(), key=lambda x: x['totale'], reverse=True)

    def get_statistiche_quartieri(self):
        quartieri = self.get_quartieri_list()
        totale = sum(q['totale'] for q in quartieri)

        return {
            'totale_segnalazioni': totale,
            'numero_quartieri': len(quartieri),
            'quartieri': quartieri,
            'media_per_quartiere': round(totale / len(quartieri), 1) if quartieri else 0
        }

    def get_top_quartieri(self, limit=10):
        return (
            self.queryset
            .values('quartiere')
            .annotate(totale=Count('id'))
            .exclude(quartiere__isnull=True)
            .exclude(quartiere='')
            .order_by('-totale')[:limit]
        )
