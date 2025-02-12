from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView

from django.shortcuts import get_object_or_404

from django.conf import settings
# Create your views here.

class HomePage(TemplateView):
    template_name='core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        path = settings.MEDIA_ROOT
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context

from .models import EmailsEmaildata, Users, Trees

# Vista per la lista di segnalazioni rifiuti
class RifiutiListView(ListView):
    model = EmailsEmaildata
    template_name = "core/rifiuti_list.html"
    context_object_name = "segnalazioni"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Ottieni il parametro dalla query string (es. ?tipo=ambiente)
        page_type = self.request.GET.get("typo", "default")

        # Definisci i titoli e le descrizioni in base al tipo di pagina
        page_titles = {
            "ambiente": ("Monitoraggio Ambientale", "Scopri le segnalazioni ambientali nella tua città."),
            "rete": ("Rete Stradale", "Partecipa alla segnalazione della rete stradale."),
            "rifiuti": ("Monitoraggio Rifiuti", "Partecipa alla segnalazione dei rifiuti de.allocati nell'ambiente cittadino."),
            "default": ("CityLog", "Citylog è una piattaforma civica che coinvolge i cittadini nel monitoraggio ambientale della propria \
                        città. Tramite citylog app, è possibile segnalare violazioni sui rifiuti, ambiente, buche/dissesti, inquinamento ambientale."),
        }

        # Imposta i valori di default se il tipo non è riconosciuto
        context["page_title"], context["page_description"] = page_titles.get(page_type, page_titles["default"])
        context["page_type"] = page_type  # Passa il tipo per gestire l'icona nel template

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        tipo = self.request.GET.get("typo")
        if tipo:
            queryset = queryset.filter(typo=tipo)
        return queryset


# Vista per il dettaglio di una segnalazione specifica
class RifiutiDetailView(DetailView):
    model = EmailsEmaildata
    template_name = "core/rifiuti_detail.html"
    context_object_name = "segnalazione"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['MEDIA_URL'] = settings.MEDIA_URL  # Passa MEDIA_URL al template
        return context

# Vista per la pagina donazioni
class DonazioniView(TemplateView):
    model = EmailsEmaildata
    template_name = "core/donazioni.html"

# Vista per la pagina manifesto
class ManifestoView(TemplateView):
    model = EmailsEmaildata
    template_name = "core/manifesto.html"

