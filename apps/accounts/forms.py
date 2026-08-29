from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import CustomUser


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Adresse e-mail',
        widget=forms.EmailInput(attrs={'autofocus': True, 'placeholder': 'vous@exemple.com'}),
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}),
    )
    error_messages = {
        'invalid_login': "Adresse e-mail ou mot de passe incorrect.",
        'inactive': "Ce compte a été désactivé.",
    }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'email', 'company_name', 'logo', 'public_contact_email',
            'phone', 'website', 'address',
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'vous@exemple.com'}),
            'company_name': forms.TextInput(attrs={'placeholder': "Nom de votre studio / entreprise"}),
            'public_contact_email': forms.EmailInput(attrs={'placeholder': 'contact@votrestudio.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '+33 1 23 45 67 89'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://votrestudio.com'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'email': 'Adresse e-mail (connexion)',
            'company_name': "Nom de l'entreprise",
            'logo': 'Logo du studio',
            'public_contact_email': 'E-mail de contact public',
            'phone': 'Téléphone',
            'website': 'Site web',
            'address': 'Adresse',
        }


class PhotographerInviteForm(forms.ModelForm):
    """Utilisé par l'administrateur pour créer/inviter un photographe."""

    password1 = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmation du mot de passe', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'company_name']

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Les mots de passe ne correspondent pas.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_photographer = True
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
