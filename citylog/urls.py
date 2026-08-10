"""citylog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LogoutView

from core.views import facebook_callback, elimina_utente, elimina_dati_personali, privacy_policy #dashboard


# URL patterns dall'app "blog"
privacy_urls = [
    path('elimina_utente/', elimina_utente, name='elimina_utente'),
    path('elimina_dati_personali/', elimina_dati_personali, name='elimina_dati_personali'),
    path('privacy/', privacy_policy, name='privacy_policy'),  # Nuovo endpoint
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('report/', include('report.urls', namespace='report')),
    path('rifiuti/', include('rifiuti.urls', namespace='rifiuti')),
    path('ambiente/', include('ambiente.urls', namespace='ambiente')),
    path('strade/', include('strade.urls', namespace='strade')),
    path('account/', include('django_users_accounts.urls')),
    path("facebook/callback/", facebook_callback, name="facebook-callback"),
    path('auth/', include('google_auth.urls')),  # 👈 Questo!
    path('testers/', include('testers.urls',namespace='testers')),
    #path("logout/", LogoutView.as_view(), name="logout"),
    #path("dashboard/", dashboard, name="dashboard"),
] + privacy_urls


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
