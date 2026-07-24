# rifiuti/services.py

from dataclasses import dataclass
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from core.models import EmailsEmaildata

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

    def get_kpi(self) -> KPIMetrics:
        oggi = timezone.now().date()
        trenta_giorni_fa = oggi - timedelta(days=30)

        return KPIMetrics(
            totale=self.queryset.count(),
            in_attesa=self.queryset.filter(status__in=['in_attesa', 'in_lavorazione']).count(),
            risolte=self.queryset.filter(status='risolta', image_time__date__gte=trenta_giorni_fa).count()
        )

    def get_trend(self, days=30):
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

            # Conta solo rifiuti per quartiere
            stats = (
                self.queryset
                .filter(quartiere=q)
                .values('typo')
                .annotate(count=Count('id'))
            )

            # Solo rifiuti (dovrebbe essere già filtrato)
            result[q] = [s['count'] for s in stats if s['typo'] == 'rifiuti']
            if not result[q]:
                result[q] = [0]

        return result

    def get_medie_temporali(self):
        """Medie giornaliere/settimanali/mensili per rifiuti"""
        oggi = timezone.now().date()

        # Media giornaliera (ultimi 7 giorni)
        ultimi_7 = oggi - timedelta(days=7)
        media_giornaliera = self.queryset.filter(image_time__date__gte=ultimi_7).count() / 7

        # Media settimanale (ultime 4 settimane)
        ultime_4_settimane = oggi - timedelta(weeks=4)
        media_settimanale = self.queryset.filter(image_time__date__gte=ultime_4_settimane).count() / 4

        # Media mensile (ultimi 6 mesi)
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
        Se quartiere è specificato, filtra solo quel quartiere
        """
        qs = self.queryset

        # ✅ Se quartiere è passato, filtra
        if quartiere and quartiere != 'all':
            qs = qs.filter(quartiere=quartiere)

        return (
            qs
            .values('address', 'quartiere')
            .annotate(totale=Count('id'))
            .order_by('-totale')[:limit]
        )
