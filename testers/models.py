from django.db import models

class TesterRegistration(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="Nome Completo")
    email = models.EmailField(
        unique=True,
        verbose_name="Email Account Google / Play Store",
        help_text="L'indirizzo email associato al tuo dispositivo Android."
    )
    agreed_to_terms = models.BooleanField(
        default=False,
        verbose_name="Accetto di tenere l'app installata per almeno 14 giorni"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Iscrizione Tester"
        verbose_name_plural = "Iscrizioni Tester"

    def __str__(self):
        return f"{self.full_name} ({self.email})"
