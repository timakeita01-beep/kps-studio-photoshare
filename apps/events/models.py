import secrets
import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


def generate_token():
    return secrets.token_urlsafe(24)


def event_photo_upload_path(instance, filename):
    return f'events/{instance.event_id}/{filename}'


class Event(models.Model):
    class EventType(models.TextChoices):
        MARIAGE = 'mariage', 'Mariage'
        PORTRAIT = 'portrait', 'Portrait'
        CORPORATE = 'corporate', 'Corporate'
        FAMILLE = 'famille', 'Famille'
        AUTRE = 'autre', 'Autre'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    photographer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events',
    )
    title = models.CharField('titre', max_length=200)
    event_type = models.CharField('type', max_length=20, choices=EventType.choices, default=EventType.AUTRE)
    description = models.TextField('description', blank=True)

    created_at = models.DateTimeField('date de création', auto_now_add=True)

    # Le lien de partage n'est utilisable, et le décompte de 15 jours ne démarre,
    # qu'à partir du moment où l'événement est marqué payé (voir mark_paid()).
    is_paid = models.BooleanField('payé', default=False)
    paid_at = models.DateTimeField('date de paiement', null=True, blank=True)
    expires_at = models.DateTimeField('date d\'expiration', null=True, blank=True)

    is_disabled = models.BooleanField('désactivé manuellement', default=False)

    view_count = models.PositiveIntegerField('nombre de vues', default=0)
    download_count = models.PositiveIntegerField('nombre de téléchargements', default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        return self.is_disabled or timezone.now() >= self.expires_at

    @property
    def status(self):
        if not self.is_paid:
            return 'pending'
        if self.is_expired:
            return 'expired'
        return 'active'

    @property
    def photo_count(self):
        return self.photos.count()

    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'pk': self.pk})

    def mark_paid(self):
        days = getattr(settings, 'EVENT_DEFAULT_EXPIRATION_DAYS', 15)
        self.is_paid = True
        self.paid_at = timezone.now()
        self.expires_at = self.paid_at + timezone.timedelta(days=days)
        self.save(update_fields=['is_paid', 'paid_at', 'expires_at'])

    def mark_unpaid(self):
        self.is_paid = False
        self.save(update_fields=['is_paid'])

    def extend_expiration(self, days=15):
        base = self.expires_at or timezone.now()
        self.expires_at = base + timezone.timedelta(days=days)
        self.save(update_fields=['expires_at'])


class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField('image', upload_to=event_photo_upload_path)
    original_filename = models.CharField('nom de fichier original', max_length=255, blank=True)
    file_size = models.PositiveIntegerField('taille (octets)', default=0)
    uploaded_at = models.DateTimeField('date d\'import', auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']

    def __str__(self):
        return self.original_filename or self.image.name

    def save(self, *args, **kwargs):
        if self.image and not self.file_size:
            try:
                self.file_size = self.image.size
            except (OSError, ValueError):
                pass
        if self.image and not self.original_filename:
            self.original_filename = self.image.name
        super().save(*args, **kwargs)


class ShareLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='share_link')
    token = models.CharField('token', max_length=64, unique=True, default=generate_token)
    is_active = models.BooleanField('actif', default=True)
    created_at = models.DateTimeField('date de création', auto_now_add=True)

    def __str__(self):
        return f'Lien de {self.event.title}'

    def get_public_url(self):
        return reverse('gallery:public_gallery', kwargs={'token': self.token})

    def regenerate(self):
        self.token = generate_token()
        self.is_active = True
        self.save(update_fields=['token', 'is_active'])
