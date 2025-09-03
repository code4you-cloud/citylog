from django import forms
from .models import Report

class ReportWebForm(forms.Form):
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    # Usare ChoiceField invece di CharField per garantire che typo rispetti le opzioni definite nel modello
    typo = forms.ChoiceField(
        choices=Report.TYPE_CHOICES,  # Usa le scelte dal modello
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})  # Genera un <select> nel template
    )

    image_file = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'custom-file-input',
            'accept': 'image/*'
        })
    )

    # Nuovo campo descrizione (breve)
    description = forms.CharField(
        max_length=200,  # Lunghezza massima ridotta per una breve descrizione
        required=False,  # Opzionale: permette di lasciare il campo vuoto
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Inserisci una breve descrizione dell\'upload (max 200 caratteri)...'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        city = cleaned_data.get('city')
        address = cleaned_data.get('address')
        typo = cleaned_data.get('typo')
        image_file = cleaned_data.get("image_file")

        if not city or not address:
            raise forms.ValidationError("Città e indirizzo sono campi obbligatori.")

        return cleaned_data


class ReportForm(forms.ModelForm):
    typo = forms.ChoiceField(  # ✅ Campo definito a livello di classe
        choices=Report.TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Report
        fields = ["city", "address", "typo", "description", "image_file"]
        widgets = {
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "image_file": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
