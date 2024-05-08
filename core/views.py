from django.shortcuts import render
from django.views.generic import TemplateView

from django.conf import settings
# Create your views here.

class HomePage(TemplateView):
    template_name='core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        path = settings.MEDIA_ROOT
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context
