from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView

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

