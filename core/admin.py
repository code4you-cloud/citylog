from django.contrib import admin

# Register your models here.
from .models import EmailsEmaildata

@admin.register(EmailsEmaildata)
class EmailsEmaildataAdmin(admin.ModelAdmin):
    list_display = ('id', 'luogo', 'stato', 'data_segnalazione')
    search_fields = ('luogo', 'descrizione')
    list_filter = ('stato',)

