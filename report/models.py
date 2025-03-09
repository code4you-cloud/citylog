from django.db import models

# Create your models here.

# 1. MODELS (models.py)
import uuid
import os
from datetime import datetime
from django.db import models

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
        ('web', 'Web'),
        ('email', 'Email'),
        ('app', 'Applicazione'),
    )

    id = models.AutoField(primary_key=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    image_time = models.DateTimeField(default=datetime.now)
    image_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    image_url = models.URLField(null=True, blank=True)
    image_file = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    typo = models.CharField(max_length=20, choices=TYPE_CHOICES, default='web')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Report {self.id} - {self.city} ({self.status})"
