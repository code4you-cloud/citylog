# Create your views here.
from django.shortcuts import render, redirect
from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from .forms import TesterRegistrationForm

from django.contrib import messages
from .models import TesterRegistration

# Sostituisci questi valori con i tuoi link reali
GOOGLE_GROUP_URL = "https://groups.google.com/g/citylog-beta-tester"
PLAY_STORE_TEST_URL = "https://play.google.com/apps/testing/com.code4you.geodumb"

class RegisterTesterView(FormView):
    """
    Pagina 1: Raccoglie e valida i dati senza salvare nulla nel Database.
    Salva i dati temporaneamente nella sessione dell'utente.
    """
    form_class = TesterRegistrationForm
    template_name = 'testers/register.html'
    success_url = reverse_lazy('testers:success')

    def get_initial(self):
        # Pre-popola il form con i dati presenti in sessione se l'utente torna indietro
        initial = super().get_initial()
        saved_data = self.request.session.get('pending_tester_data', {})
        initial.update(saved_data)
        return initial

    def form_valid(self, form):
        # Salva i dati puliti del form nella sessione HTTP
        # Usiamo dict conversion per assicurarci che i dati siano serializzabili in JSON
        self.request.session['pending_tester_data'] = {
            k: v for k, v in form.cleaned_data.items()
        }
        return super().form_valid(form)

class SuccessView(TemplateView):
    """
    Pagina 2: Riceve l'utente, effettua la creazione REALE nel DB
    e pulisce la sessione per evitare duplicati.
    """
    template_name = 'testers/success.html'

    def dispatch(self, request, *args, **kwargs):
        # Verifichiamo se ci sono dati pendenti in sessione
        tester_data = request.session.get('pending_tester_data')

        # Se l'utente tenta di accedere direttamente a /success senza aver compilato il form
        if not tester_data and not request.session.get('tester_registered'):
            messages.warning(request, "Compila prima il modulo di registrazione.")
            return redirect('testers:register') # Sostituisci con il name corretto della tua rotta di registro

        # Se ci sono dati pendenti in sessione, effettuiamo la registrazione nel DB ORA
        if tester_data:
            email = tester_data.get('email')

            # Controllo di sicurezza prima di scrivere su DB
            if not TesterRegistration.objects.filter(email=email).exists():
                TesterRegistration.objects.create(**tester_data)

            # Impostiamo un flag per ricordare che la registrazione è avvenuta ed eliminiamo i dati pendenti
            request.session['tester_registered'] = True
            del request.session['pending_tester_data']

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_group_url'] = GOOGLE_GROUP_URL
        context['play_store_test_url'] = PLAY_STORE_TEST_URL
        return context

class SuccessView__(TemplateView):
    template_name = 'testers/success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_group_url'] = GOOGLE_GROUP_URL
        context['play_store_test_url'] = PLAY_STORE_TEST_URL
        return context
