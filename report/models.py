from django.db import models

# Create your models here.

# 1. MODELS (models.py)
import uuid
import os
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

from core.models import Users

def get_image_path(instance, filename):
    # Genera un percorso univoco per ogni immagine caricata
    ext = filename.split('.')[-1]
    filename = f"{instance.image_id}.{ext}"
    return os.path.join('uploads', filename)

class Report(models.Model):
    STATUS_CHOICES = (
        ('pending', 'In attesa'),
        ('approved', 'Approvato'),
        ('rejected', 'Rifiutato'),
    )

    TYPE_CHOICES = (
        ('rifiuti', 'Rifiuti'),
        ('tronchi', 'Tronchi'),
        ('censimento', 'Censimento'),
        ('piantumazione', 'Piantumazione'),
        ('strade', 'Strade'),
    )

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True)  # Nuovo campo
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    image_time = models.DateTimeField(default=datetime.now)
    image_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    image_url = models.CharField(max_length=255,null=True, blank=True)
    #image_file = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    image_file = models.ImageField(upload_to='reports/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    typo = models.CharField(max_length=20, choices=TYPE_CHOICES, default='web')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Nuovo campo descrizione (breve)
    description = models.CharField(
        max_length=200,  # Lunghezza massima ridotta per una breve descrizione
        blank=True,      # Opzionale: permette di lasciare il campo vuoto
        null=True,       # Opzionale: permette di salvare NULL nel database
        help_text="Inserisci una breve descrizione dell'upload (max 200 caratteri)."  # Testo di aiuto
    )
    confirmations = models.ManyToManyField(Users, related_name="confirmed_reports", blank=True)

    def confirm_report(self, user):
        """Aggiunge una conferma e verifica la segnalazione se necessario."""
        self.confirmations.add(user)
        if self.confirmations.count() >= 2:  # Cambia il numero a seconda della policy
            self.status = "verified"
        self.save()

    def delete_report(self, user):
        """Permette solo all'autore della segnalazione o a un admin di eliminarla."""
        if self.user == user or user.is_superuser:
            self.delete()
            return True
        return False

    def __str__(self):
        return f"Report {self.id} - {self.city} ({self.status})"
