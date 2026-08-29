from django.conf import settings
from django import forms

from .models import Event

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_PHOTO_SIZE_BYTES = getattr(settings, 'MAX_PHOTO_SIZE_MB', 20) * 1024 * 1024


class EventForm(forms.ModelForm):
    is_paid = forms.BooleanField(
        label="Cet événement est déjà payé",
        required=False,
        help_text=(
            "Tant que non coché, le lien de partage reste inactif et le délai de 15 jours "
            "ne démarre pas. Vous pourrez marquer l'événement comme payé plus tard depuis sa fiche."
        ),
    )

    class Meta:
        model = Event
        fields = ['title', 'event_type', 'description', 'is_paid']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': "Ex : Mariage de Lise & Karim"}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Description (optionnelle)'}),
        }
        labels = {
            'title': 'Titre',
            'event_type': "Type d'événement",
            'description': 'Description',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Le statut de paiement se gère depuis la fiche événement une fois créé
        # (bouton dédié), pas en modification via ce formulaire.
        if self.instance and self.instance.pk:
            del self.fields['is_paid']


def validate_uploaded_photo(uploaded_file):
    """Renvoie un message d'erreur (str) si le fichier n'est pas valide, sinon None."""
    extension = uploaded_file.name.rsplit('.', 1)[-1].lower() if '.' in uploaded_file.name else ''
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return f"« {uploaded_file.name} » : format non supporté."
    if uploaded_file.size > MAX_PHOTO_SIZE_BYTES:
        return f"« {uploaded_file.name} » dépasse la taille maximale de 20 Mo."
    return None
