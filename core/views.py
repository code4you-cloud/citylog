import logging
import requests

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView

from django.shortcuts import get_object_or_404
from django.conf import settings

from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseRedirect

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from report.models import Report
from .models import EmailsEmaildata, Users, Trees

#from .models import EmailsEmaildata

logger = logging.getLogger(__name__)

# Create your views here.

class HomePage(TemplateView):
    template_name='core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        path = settings.MEDIA_ROOT
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context

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
            "buche": ("Buche", "Monitora le buche o dissesti stradali pericolosi."),
            "inquinamento": ("Inquinamento", "Visualizzate le % inquinanti."),
            "default": ("CityLog", "Citylog è una piattaforma civica che coinvolge i cittadini nel monitoraggio ambientale della propria \
                        città. Tramite citylog app, è possibile segnalare violazioni sui rifiuti, ambiente, buche/dissesti, inquinamento ambientale."),
        }

        # Imposta i valori di default se il tipo non è riconosciuto
        context["page_title"], context["page_description"] = page_titles.get(page_type, page_titles["default"])
        context["page_type"] = page_type if page_type in page_titles else "default" # Passa il tipo per gestire l'icona nel template
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        tipo = self.request.GET.get("typo")
        if tipo == "ambiente":
            queryset = queryset.filter(typo__in=["piantumazione", "tronchi", "censimento"])
            #queryset = queryset.filter(typo=tipo)
        else:
            queryset = queryset.filter(typo=tipo)

        # Ordina il queryset per image_time in ordine decrescente
        queryset = queryset.order_by('-image_time')

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

    def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)

         # Ottieni il parametro dalla query string (es. ?tipo=ambiente)
         path = self.request.path
         if '/donazioni/' in path:
            page_type = "donazioni"
         else:
            page_type = "default"
         #page_type = self.request.GET.get("page", "default")

         # Definisci i titoli e le descrizioni in base al tipo di pagina
         page_titles = {
             "donazioni": ("Donazioni", "Sostieni i servizi e lo sforzo di Citylog attraverso una donazione."),
             "default": ("Donazioni", "Sostieni i servizi e lo sforzo di Citylog attraverso una donazione."),
         }

         # Imposta i valori di default se il tipo non è riconosciuto
         context["page_title"], context["page_description"] = page_titles.get(page_type, page_titles["default"])
         context["page_type"] = page_type if page_type in page_titles else "default" # Passa il tipo per gestire l'icona nel template
         return context

# Vista per la pagina manifesto
class ManifestoView(TemplateView):
    model = EmailsEmaildata
    template_name = "core/manifesto.html"

    def get_context_data(self, **kwargs):
           context = super().get_context_data(**kwargs)

           # Ottieni il parametro dalla query string (es. ?tipo=ambiente)
           path = self.request.path
           if '/manifesto/' in path:
              page_type = "manifesto"
           else:
              page_type = "default"
           #page_type = self.request.GET.get("page", "default")

           # Definisci i titoli e le descrizioni in base al tipo di pagina
           page_titles = {
               "manifesto": ("Manifesto", "I valori che sostengono l'impegno di CityLog."),
               "default": ("API", "Utilizza gli endpoint di Citylog per estrarre dati e valori."),
           }

           # Imposta i valori di default se il tipo non è riconosciuto
           context["page_title"], context["page_description"] = page_titles.get(page_type, page_titles["default"])
           context["page_type"] = page_type if page_type in page_titles else "default" # Passa il tipo per gestire l'icona nel template
           return context

# Vista per la pagina regolamento
class RegoleView(TemplateView):
    model = EmailsEmaildata
    template_name = "core/regole.html"

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)

            # Ottieni il parametro dalla query string (es. ?tipo=ambiente)
            path = self.request.path
            if '/regole/' in path:
               page_type = "regole"
            else:
               page_type = "default"
            #page_type = self.request.GET.get("page", "default")

            # Definisci i titoli e le descrizioni in base al tipo di pagina
            page_titles = {
                "regole": ("Regole", "Le poche ma necessarie regole da seguire."),
                "default": ("Regole", "Regole."),
            }

            # Imposta i valori di default se il tipo non è riconosciuto
            context["page_title"], context["page_description"] = page_titles.get(page_type, page_titles["default"])
            context["page_type"] = page_type if page_type in page_titles else "default" # Passa il tipo per gestire l'icona nel template
            return context

# Vista per la pagina regolamento
class ApiView(TemplateView):
    model = EmailsEmaildata
    template_name = "core/api.html"

    def get_context_data(self, **kwargs):
          context = super().get_context_data(**kwargs)

          # Ottieni il parametro dalla query string (es. ?tipo=ambiente)
          path = self.request.path
          if '/api-docs/' in path:
             page_type = "api"
          else:
             page_type = "default"
          #page_type = self.request.GET.get("page", "default")

          # Definisci i titoli e le descrizioni in base al tipo di pagina
          page_titles = {
              "api": ("API", "Utilizza gli endpoint di Citylog per estrarre dati e valori."),
              "default": ("API", "Utilizza gli endpoint di Citylog per estrarre dati e valori."),
          }

          # Imposta i valori di default se il tipo non è riconosciuto
          context["page_title"], context["page_description"] = page_titles.get(page_type, page_titles["default"])
          context["page_type"] = page_type if page_type in page_titles else "default" # Passa il tipo per gestire l'icona nel template
          return context

# Vista per la pagina regolamento
class StatisticheView(TemplateView):
    model = EmailsEmaildata
    template_name = "core/statistiche.html"

    def get_context_data(self, **kwargs):
           context = super().get_context_data(**kwargs)

           # Ottieni il parametro dalla query string (es. ?tipo=ambiente)
           path = self.request.path
           if '/statistiche/' in path:
              page_type = "statistiche"
           else:
              page_type = "default"
           #page_type = self.request.GET.get("page", "default")

           # Definisci i titoli e le descrizioni in base al tipo di pagina
           page_titles = {
               "statistiche": ("Statistiche", "Visualizza percentuali-dati-valori ambientali della tua citta+."),
               "default": ("Statistiche", "Statistiche."),
           }

           # Imposta i valori di default se il tipo non è riconosciuto
           context["page_title"], context["page_description"] = page_titles.get(page_type, page_titles["default"])
           context["page_type"] = page_type if page_type in page_titles else "default" # Passa il tipo per gestire l'icona nel template
           return context

def facebook_callback(request):
    code = request.GET.get("code")
    if not code:
        return redirect("core:home")

    # Scambio del codice con un access token
    token_url = f"https://graph.facebook.com/v17.0/oauth/access_token"
    params = {
        "client_id": settings.FACEBOOK_APP_ID,
        "redirect_uri": settings.FACEBOOK_REDIRECT_URI,
        "client_secret": settings.FACEBOOK_APP_SECRET,
        "code": code,
    }
    response = requests.get(token_url, params=params)
    token_data = response.json()

    access_token = token_data.get("access_token")
    if not access_token:
        return redirect("core:home")

    # Ottenere i dati dell'utente
    user_info_url = "https://graph.facebook.com/me"
    user_params = {
        "fields": "id,name,email,picture",
        "access_token": access_token,
    }
    user_response = requests.get(user_info_url, params=user_params)
    user_data = user_response.json()

    facebook_id = user_data.get("id")
    name = user_data.get("name")
    email = user_data.get("email")
    picture_url = user_data.get("picture", {}).get("data", {}).get("url")

    if not email:
        return redirect("core:home")

    # Creazione o autenticazione dell'utente
    user, created = User.objects.get_or_create(username=email, defaults={"first_name": name, "email": email})
    #user.profile.picture = picture_url  # Salviamo l'URL dell'immagine nel profilo
    #user.profile.save()

    # get facebook picture and name
    request.session['facebook_picture'] = picture_url
    request.session['facebook_name'] = name
    request.sessiom = picture_url  # Salviamo l'URL dell'immagine nel profilo

    login(request, user)
    return redirect("dashboard")  # Reindirizza alla dashboard


@login_required
def dashboard(request):
    user_reports = Report.objects.filter(user=request.user).order_by('-image_time')  # Filtra per utente autenticato
    return render(request, 'core/dashboard.html', {'reports': user_reports, "MEDIA_URL": settings.MEDIA_URL})
