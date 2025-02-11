# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AlembicVersion(models.Model):
    version_num = models.CharField(primary_key=True, max_length=32)

    class Meta:
        managed = False
        db_table = 'alembic_version'


class ApiKeys(models.Model):
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    key = models.CharField(unique=True, max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_keys'

class EmailsEmaildata(models.Model):
    id = models.BigIntegerField(primary_key=True)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    image_time = models.DateTimeField(blank=True, null=True)
    image_id = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)
    image_file = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50)
    typo = models.CharField(max_length=20)

    class Meta:
        managed = True
        db_table = 'emails_emaildata'


class Trees(models.Model):
    id = models.AutoField(primary_key=True)  # Aggiunto ID automatico
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    info = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'trees'


class Users(models.Model):
    id = models.AutoField(primary_key=True)  # Aggiunto ID automatico
    username = models.CharField(unique=True, max_length=255)
    hashed_password = models.CharField(max_length=255)
    api_key = models.CharField(unique=True, max_length=255, blank=True, null=True)
    can_regenerate_key = models.BooleanField(blank=True, null=True)
    api_key_creation_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'users'
