import logging
import requests
import traceback
import json
import os

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView, View

from django.shortcuts import get_object_or_404
from django.conf import settings

from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import messages

from django.contrib.auth import login, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from report.models import Report
from .models import EmailsEmaildata, Users, Trees
from .services import QuartieriService

from facebook_auth.client import FacebookAuthClient
from facebook_auth.exceptions import FacebookAuthError

from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import TruncDay

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache

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
            "ambiente": ("Log.Ambiente", "Scopri le segnalazioni ambientali nella tua città. Le segnalazioni evidenziano: erosione-arboreo - censimento arboreo - nuove piantumazioni arboree"),
            "rete": ("Log.Traffico", "Partecipa alla segnalazione della rete stradale."),
            "rifiuti": ("Log.Rifiuti", "Partecipa alla segnalazione dei rifiuti de.allocati nell'ambiente cittadino."),
            "strade": ("Log.Strade", "Monitora le tue strade, i dissesti stradali pericolosi per la tua incolumità e viabilità."),
            "inquinamento": ("Log.Aria", "Visualizzate le % inquinanti."),
            "dashboard": ("Dashboard", "La tua Dashboard personale."),
            "statistiche": ("Statistiche", "Statistiche."),
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

# Vista per la pagina trasparenza
class TrasparenzaView(TemplateView):
    model = EmailsEmaildata
    template_name = "core/trasparenza.html"

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)

            # Ottieni il parametro dalla query string (es. ?tipo=ambiente)
            path = self.request.path
            if '/trasparenza/' in path:
               page_type = "trasparenza"
            else:
               page_type = "default"
            #page_type = self.request.GET.get("page", "default")

            # Definisci i titoli e le descrizioni in base al tipo di pagina
            page_titles = {
                "trasparenza": ("Trasparenza", "La nostra Roadmap trasparente."),
                "default": ("Trasparenza", "Trasparenza."),
            }

            # Imposta i valori di default se il tipo non è riconosciuto
            context["page_title"], context["page_description"] = page_titles.get(page_type, page_titles["default"])
            context["page_type"] = page_type if page_type in page_titles else "default" # Passa il tipo per gestire l'icona nel template
            return context


# Vista per la pagina guida-foto
class GuidaFotoView(TemplateView):
    model = EmailsEmaildata
    template_name = "core/guida-foto.html"

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)

            # Ottieni il parametro dalla query string (es. ?tipo=ambiente)
            path = self.request.path
            if '/guida-foto/' in path:
               page_type = "guida-foto"
            else:
               page_type = "default"
            #page_type = self.request.GET.get("page", "default")

            # Definisci i titoli e le descrizioni in base al tipo di pagina
            page_titles = {
                "guida-foto": ("Guida Foto", "Alcuni consigli come segnalare."),
                "default": ("Guida Foto", "Guida Foto."),
            }

            # Imposta i valori di default se il tipo non è riconosciuto
            context["page_title"], context["page_description"] = page_titles.get(page_type, page_titles["default"])
            context["page_type"] = page_type if page_type in page_titles else "default" # Passa il tipo per gestire l'icona nel template
            return context

# Vista per la pagina guida-foto
class MotivazioniView(TemplateView):
    model = EmailsEmaildata
    template_name = "core/motivazioni.html"

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)

            # Ottieni il parametro dalla query string (es. ?tipo=ambiente)
            path = self.request.path
            if '/motivazioni/' in path:
               page_type = "motivazioni"
            else:
               page_type = "default"
            #page_type = self.request.GET.get("page", "default")

            # Definisci i titoli e le descrizioni in base al tipo di pagina
            page_titles = {
                "motivazioni": ("Motivazioni", "Perchè dovresti farlo."),
                "default": ("Motivazioni", "Motivazioni"),
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

class StatisticheView(TemplateView):
    template_name = "core/statistiche.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # KPI
        context["kpi"] = {
            "totale": EmailsEmaildata.objects.count(),
            "in_attesa": EmailsEmaildata.objects.filter(status="in_attesa").count(),
            "risolte": EmailsEmaildata.objects.filter(status="risolto").count(),
        }

        # Trend ultimi giorni
        context["chart_attuali_data"] = {
            "labels": ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"],
            "series": [12, 19, 3, 5, 2, 3, 9],
        }

        # Per Tipologia
        context["chart_tipologia_data"] = {
            "labels": ["Ingombranti", "Abbandono", "Cassonetto Pieno", "Verde"],
            "series": [45, 23, 15, 8],
        }

        # Mappa Dati per Quartiere (usata dal select JS)
        context["quartieri_list"] = ["Centro", "Mazzini", "San Zeno"]
        context["quartieri_dict_data"] = {
            "Centro": [15, 8, 4, 2],
            "Mazzini": [5, 12, 9, 1],
            "San Zeno": [8, 3, 14, 6],
        }

        return context

# Vista per la pagina regolamento
class StatisticheView_ori(TemplateView):
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
    try:
        logger.debug("Facebook callback GET params: %s", request.GET)

        code = request.GET.get("code")
        if not code:
            logger.warning("Nessun code fornito nella callback")
            return redirect("core:home")

        # 🔹 Scambio del code con access token
        token_url = f"https://graph.facebook.com/v17.0/oauth/access_token"
        params = {
            "client_id": settings.FACEBOOK_APP_ID,
            "redirect_uri": settings.FACEBOOK_REDIRECT_URI,
            "client_secret": settings.FACEBOOK_APP_SECRET,
            "code": code,
        }
        response = requests.get(token_url, params=params)
        token_data = response.json()
        logger.debug("Token data: %s", token_data)

        access_token = token_data.get("access_token")
        if not access_token:
            logger.error("Access token non disponibile: %s", token_data)
            return redirect("core:home")

        # 🔹 Ottieni dati utente
        user_info_url = "https://graph.facebook.com/me"
        user_params = {
            "fields": "id,name,email,picture",
            "access_token": access_token,
        }
        user_response = requests.get(user_info_url, params=user_params)
        user_data = user_response.json()
        logger.debug("Facebook user_data: %s", user_data)

        facebook_id = user_data.get("id")
        name = user_data.get("name")
        email = user_data.get("email")
        picture_url = user_data.get("picture", {}).get("data", {}).get("url")

        # 🔹 Usa facebook_id come fallback per username
        username = email or facebook_id
        if not username:
            logger.error("Né email né facebook_id disponibili, redirect")
            return redirect("core:manifesto-view")

        # 🔹 Creazione o autenticazione dell'utente
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"first_name": name or "", "email": email or ""}
        )
        logger.debug("User ottenuto: %s, creato: %s", user.username, created)

        # 🔹 Salva dati in sessione
        request.session['facebook_picture'] = picture_url
        request.session['facebook_name'] = name

        # 🔹 Autentica utente
        login(request, user, backend='facebook_auth.backends.FacebookAuthBackend')
        logger.debug("Login Django effettuato per: %s", user.username)

        return redirect("core:dashboard")

    except Exception as e:
        logger.error("Errore nella facebook_callback: %s", e)
        logger.error(traceback.format_exc())
        return redirect("core:manifesto-view")

def facebook_callback_good(request):
     code = request.GET.get("code")
     if not code:
         return redirect("core:home")

     # Scambio del codice con un access token
     token_url = "https://graph.facebook.com/v17.0/oauth/access_token"
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

     # Usa facebook_id come username se email non è disponibile
     username = email if email else facebook_id
     if not username:
         return redirect("core:manifesto-view")  # Reindirizza se né email né facebook_id sono disponibili

     # Creazione o autenticazione dell'utente
     user, created = User.objects.get_or_create(
         username=username,
         defaults={"first_name": name or "", "email": email or ""}
     )

     # Salva i dati nella sessione
     request.session['facebook_picture'] = picture_url
     request.session['facebook_name'] = name

     # Autentica l'utente
     login(request, user, backend='facebook_auth.backends.FacebookAuthBackend')
     return redirect("core:dashboard")

def facebook_callback_(request):
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


#@login_required
#def dashboard(request):
#    user_reports = Report.objects.filter(user=request.user).order_by('-image_time')  # Filtra per utente autenticato
#    return render(request, 'core/dashboard.html', {'reports': user_reports, "MEDIA_URL": settings.MEDIA_URL})

@login_required
def elimina_utente(request):
    if request.method == 'POST':
        user = request.user
        user.delete()  # Cancella l'utente e i dati collegati (se on_delete=CASCADE)
        messages.success(request, "Account eliminato con successo.")
        return redirect('home')
    return render(request, 'conferma_eliminazione.html', {'action': 'account'})

@login_required
def elimina_dati_personali(request):
    if request.method == 'POST':
        user = request.user
        # Anonimizzazione dati (esempio minimo)
        user.email = f"deleted_{user.id}@example.com"
        user.first_name = "Deleted"
        user.last_name = "User"
        user.save()
        messages.success(request, "Dati personali rimossi con successo.")
        return redirect('home')
    return render(request, 'conferma_eliminazione.html', {'action': 'dati'})

def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')

class UserDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ✅ VERIFICA CONNESSIONE DATABASE
        try:
            total_count = EmailsEmaildata.objects.using('segnalazioni_db').count()
            context['debug_total'] = total_count
            print(f"✅ Connessione OK: {total_count} record", flush=True)
        except Exception as e:
            context['debug_total'] = f"ERRORE: {e}"
            print(f"❌ Errore database: {e}", flush=True)
            return context

        # ✅ DATI GLOBALI (tutti gli utenti)
        global_queryset = EmailsEmaildata.objects.using('segnalazioni_db').all()

        context['statistiche_globale'] = {
            'totale_segnalazioni': global_queryset.count(),
            'numero_quartieri': global_queryset.values('quartiere').distinct().count(),
            'tipologie': dict(
                global_queryset.values('typo')
                .annotate(count=Count('id'))
                .values_list('typo', 'count')
            ),
        }

        # ============================================================
        # ✅ DATI PERSONALI (solo questo utente)
        # ============================================================
        # Cerca l'utente nel modello legacy tramite Facebook name
        facebook_name = self.request.session.get('facebook_name')
        if facebook_name:
            legacy_user = Users.objects.filter(name=facebook_name).first()
            print(f"🔍 Utente legacy trovato: {legacy_user}", flush=True)
        else:
            legacy_user = None

        context['legacy_user'] = legacy_user

        if legacy_user:
            # ✅ Query per le segnalazioni (NON limitata)
            user_reports = EmailsEmaildata.objects.using('segnalazioni_db') \
                .filter(user_id=legacy_user.id) \
                .order_by('-image_time')
            print(f"🔍 Segnalazioni per user_id {legacy_user.id}: {user_reports.count()}", flush=True)
        else:
            # Fallback: tutte le segnalazioni
            user_reports = EmailsEmaildata.objects.using('segnalazioni_db') \
                .order_by('-image_time')
            print(f"⚠️ Utente legacy NON trovato, mostro tutte le segnalazioni", flush=True)

        # 🔍 DEBUG: Query SQL
        context['debug_query'] = str(user_reports.query)
        context['debug_count'] = user_reports.count()


        # ✅ CALCOLA LE STATISTICHE SUL QUERYSET COMPLETO
        context['statistiche_utente'] = {
            'totale_segnalazioni': user_reports.count(),
            'tipologie': dict(
                user_reports.values('typo')
                .annotate(count=Count('id'))
                .values_list('typo', 'count')
            ),
        }

        # ✅ POI PRENDI SOLO I PRIMI 10 PER LA VISUALIZZAZIONE
        context['reports'] = list(user_reports[:10])

        # ✅ QUARTIERI PERSONALI DELL'UTENTE (conteggio)
        totale_quartieri_personali = user_reports.values('quartiere').distinct().count()
        context['totale_quartieri_personali'] = totale_quartieri_personali

        # ✅ QUARTIERI PERSONALI (lista dettagliata con conteggi per quartiere)
        quartieri_personali = list(
            user_reports.values('quartiere')
            .annotate(totale=Count('id'))
            .exclude(quartiere__isnull=True)
            .exclude(quartiere='')
            .order_by('-totale')
        )
        context['quartieri_personali'] = quartieri_personali

        # ============================================================
        # ✅ SEZIONE QUARTIERI GLOBALI (con coordinate)
        # ============================================================
        quartieri_list = list(
            global_queryset
            .values('quartiere')
            .annotate(totale=Count('id'))
            .exclude(quartiere__isnull=True)
            .exclude(quartiere='')
            .order_by('-totale')
        )
        context['debug_quartieri_raw'] = quartieri_list[:5]

        # ✅ DETTAGLIO QUARTIERI GLOBALI CON COORDINATE
        quartieri_dettaglio = {}
        dati = (
            global_queryset
            .values('quartiere', 'typo')
            .annotate(count=Count('id'))
            .exclude(quartiere__isnull=True)
            .exclude(quartiere='')
        )

        for item in dati:
            quartiere = item['quartiere']
            typo = item['typo']
            count = item['count']

            if quartiere not in quartieri_dettaglio:
                # Prendi le coordinate dalla prima segnalazione del quartiere
                prima_segnalazione = global_queryset.filter(quartiere=quartiere).first()
                quartieri_dettaglio[quartiere] = {
                    'nome': quartiere,
                    'totale': 0,
                    'tipologie': {},
                    'latitude': prima_segnalazione.latitude if prima_segnalazione else '',
                    'longitude': prima_segnalazione.longitude if prima_segnalazione else ''
                }

            quartieri_dettaglio[quartiere]['totale'] += count
            quartieri_dettaglio[quartiere]['tipologie'][typo] = count

        quartieri_dettaglio_ordinati = sorted(
            quartieri_dettaglio.values(),
            key=lambda x: x['totale'],
            reverse=True
        )

        context['user_quartieri'] = quartieri_list
        context['quartieri_dettaglio'] = quartieri_dettaglio_ordinati
        context['totale_quartieri'] = len(quartieri_list)

        # ✅ SESSIONE PER DEBUG
        context['session_keys'] = list(self.request.session.keys())
        context['session_data'] = dict(self.request.session)

        return context

class MachineLearningView(TemplateView):
    template_name = 'core/machine_learning.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total_rifiuti': 1247,
            'total_strade': 823,
            'total_verde': 456,
            'total_illuminazione': 312,
        })
        return context

#@login_required
#def mappa_segnalazioni(request):
#    path = os.path.join(settings.BASE_DIR, 'core', 'templates', 'core', 'sample_leaflet_mono65_debug4.html')
#    with open(path, encoding='utf-8') as f:
#        return HttpResponse(f.read(), content_type='text/html')
#
class MappaSegnalazioniView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cache_key = 'mappa_segnalazioni_html'
        html_content = cache.get(cache_key)

        if html_content is None:
            path = os.path.join(settings.BASE_DIR, 'core', 'templates', 'core', 'segnalazioni.html')
            with open(path, encoding='utf-8') as f:
                html_content = f.read()
                cache.set(cache_key, html_content, 3600)  # Cache per 1 ora

        return HttpResponse(html_content, content_type='text/html')



