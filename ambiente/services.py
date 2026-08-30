# ambiente/services.py
from django.db.models import Count, Q, Max
from .models import EmailsEmaildata

class StatisticheService:

    def get_kpi(self, typo_list=None):
        """
        Restituisce i KPI filtrati per typo_list
        """
        queryset = EmailsEmaildata.objects.using('segnalazioni_db')

        if typo_list:
            queryset = queryset.filter(typo__in=typo_list)

        # Esempio di KPI
        return {
            'totale': queryset.count(),
            # altri KPI...
        }

    def get_trend(self, typo_list=None):
        """
        Restituisce il trend filtrato per typo_list
        """
        queryset = EmailsEmaildata.objects.using('segnalazioni_db')

        if typo_list:
            queryset = queryset.filter(typo__in=typo_list)

        # Esempio di trend per data
        trend = queryset.extra(
            select={'date': 'date(image_time)'}
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        return list(trend)

    def get_tipologie(self, typo_list=None):
        """
        Restituisce le tipologie filtrate per typo_list
        """
        queryset = EmailsEmaildata.objects.using('segnalazioni_db')

        if typo_list:
            queryset = queryset.filter(typo__in=typo_list)

        tipologie = queryset.values('typo').annotate(
            count=Count('id')
        ).order_by('-count')

        return list(tipologie)

    def get_quartieri(self, typo_list=None):
        """
        Restituisce le statistiche per quartiere filtrate per typo_list
        """
        queryset = EmailsEmaildata.objects.using('segnalazioni_db')

        if typo_list:
            queryset = queryset.filter(typo__in=typo_list)

        quartieri = queryset.values('quartiere').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        return list(quartieri)

    def get_medie_temporali(self, typo_list=None):
        """
        Restituisce le medie temporali filtrate per typo_list
        """
        queryset = EmailsEmaildata.objects.using('segnalazioni_db')

        if typo_list:
            queryset = queryset.filter(typo__in=typo_list)

        # Esempio di medie per mese
        medie = queryset.extra(
            select={'month': "EXTRACT(MONTH FROM image_time)"}
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        return list(medie)

    def get_top_indirizzi(self, limit=10, typo_list=None):
        """
        Restituisce i top indirizzi filtrati per typo_list
        """
        queryset = EmailsEmaildata.objects.using('segnalazioni_db')

        if typo_list:
            queryset = queryset.filter(typo__in=typo_list)

        top = queryset.values('address', 'city').annotate(
            count=Count('id'),
            latitude=Max('latitude'),
            longitude=Max('longitude'),
        ).order_by('-count')[:limit]

        return list(top)

    def get_top_indirizzi_(self, limit=10, typo_list=None):
        """
        Restituisce i top indirizzi filtrati per typo_list
        """
        queryset = EmailsEmaildata.objects.using('segnalazioni_db')

        if typo_list:
            queryset = queryset.filter(typo__in=typo_list)

        top = queryset.values('address', 'city').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]

        return list(top)
