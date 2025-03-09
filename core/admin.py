from django.contrib import admin

# Register your models here.
from .models import EmailsEmaildata

@admin.register(EmailsEmaildata)
class EmailsEmaildataAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'address', 'image_time')
    search_fields = ('city', 'address')
    list_filter = ('status',)

