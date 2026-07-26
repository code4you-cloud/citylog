# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class EmailsEmaildata(models.Model):
    id = models.BigAutoField(primary_key=True)
    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    address = models.TextField()
    image_time = models.DateTimeField()
    image_id = models.CharField(unique=True, max_length=255, blank=True, null=True)
    image_url = models.CharField(max_length=255)
    image_file = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50)
    typo = models.CharField(max_length=20)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    status_int = models.IntegerField(blank=True, null=True)
    quartiere = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'emails_emaildata'
        app_label = 'rifiuti'  # ← Per il router


class FreeWeb(models.Model):
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    image_time = models.DateTimeField(blank=True, null=True)
    image_id = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.CharField(max_length=200, blank=True, null=True)
    image_file = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50)
    typo = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'free_web'


class Trees(models.Model):
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    info = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trees'


class UserRateLimit(models.Model):
    user = models.OneToOneField('Users', models.DO_NOTHING, primary_key=True)
    count = models.IntegerField(blank=True, null=True)
    is_banned = models.BooleanField(blank=True, null=True)
    ban_reason = models.TextField(blank=True, null=True)
    banned_until = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    sent = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_rate_limit'
        app_label = 'rifiuti'  # ← Per il router


class Users(models.Model):
    username = models.CharField(blank=True, null=True)
    hashed_password = models.CharField(blank=True, null=True)
    api_key = models.CharField(blank=True, null=True)
    can_regenerate_key = models.CharField(blank=True, null=True)
    api_key_creation_date = models.DateTimeField(blank=True, null=True)
    email = models.CharField(unique=True, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    facebook_id = models.CharField(unique=True, max_length=50, blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    google_id = models.CharField(unique=True, max_length=50, blank=True, null=True)
    avatar_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'
        app_label = 'rifiuti'  # ← Per il router
