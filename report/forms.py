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
    upload_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'custom-file-input',
            'accept': 'image/*'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        city = cleaned_data.get('city')
        address = cleaned_data.get('address')

        if not city or not address:
            raise forms.ValidationError("Città e indirizzo sono campi obbligatori.")

        return cleaned_data
