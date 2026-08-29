import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Utilisateur interne : administrateur ou photographe. Le client n'a pas de compte."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField('adresse e-mail', unique=True)

    company_name = models.CharField('nom de l\'entreprise', max_length=150, blank=True)
    phone = models.CharField('téléphone', max_length=30, blank=True)
    public_contact_email = models.EmailField(
        'e-mail de contact public', blank=True,
        help_text="Affiché au client (ex : page de lien expiré). Laisser vide pour utiliser l'e-mail de connexion.",
    )
    website = models.URLField('site web', blank=True)
    address = models.TextField('adresse', blank=True)
    logo = models.ImageField('logo du studio', upload_to='studio_logos/', blank=True, null=True)

    is_admin = models.BooleanField('administrateur', default=False)
    is_photographer = models.BooleanField('photographe', default=False)

    is_active = models.BooleanField('compte actif', default=True)
    is_staff = models.BooleanField('accès admin Django', default=False)

    date_joined = models.DateTimeField('date d\'inscription', auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'utilisateur'
        verbose_name_plural = 'utilisateurs'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.company_name or self.email

    def get_short_name(self):
        return self.email.split('@')[0]

    @property
    def contact_email(self):
        return self.public_contact_email or self.email

    @property
    def role_label(self):
        if self.is_admin:
            return 'Administrateur'
        if self.is_photographer:
            return 'Photographe'
        return 'Utilisateur'
