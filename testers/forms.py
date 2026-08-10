from django import forms
from .models import TesterRegistration

class TesterRegistrationForm(forms.ModelForm):
    class Meta:
        model = TesterRegistration
        fields = ['full_name', 'email', 'agreed_to_terms']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Es. Mario Rossi'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'nome@gmail.com'
            }),
            'agreed_to_terms': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_agreed_to_terms(self):
        agreed = self.cleaned_data.get('agreed_to_terms')
        if not agreed:
            raise forms.ValidationError("Devi accettare di mantenere l'app installata per 14 giorni per procedere.")
        return agreed

