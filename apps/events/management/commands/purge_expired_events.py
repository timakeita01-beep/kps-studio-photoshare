from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.events.models import Event


class Command(BaseCommand):
    help = (
        "Supprime les événements expirés depuis plus de N jours (photos et fichiers média inclus). "
        "Utiliser --dry-run pour lister sans rien supprimer."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Liste les événements à purger sans les supprimer.',
        )
        parser.add_argument(
            '--after-days', type=int,
            default=getattr(settings, 'PURGE_AFTER_EXPIRATION_DAYS', 15),
            help="Nombre de jours après l'expiration avant purge (défaut : réglage du projet).",
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        after_days = options['after_days']
        threshold = timezone.now() - timezone.timedelta(days=after_days)

        # Les événements jamais payés n'ont pas de date d'expiration : ils ne sont
        # jamais purgés par cette règle (ils restent en attente indéfiniment).
        candidates = [
            event for event in Event.objects.all()
            if event.expires_at and event.expires_at <= threshold
        ]

        if not candidates:
            self.stdout.write(self.style.SUCCESS('Aucun événement à purger.'))
            return

        for event in candidates:
            self.stdout.write(
                f'- {event.title} (photographe: {event.photographer.email}, '
                f'expiré le {event.expires_at:%d/%m/%Y}, {event.photo_count} photo(s))'
            )

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'\n[dry-run] {len(candidates)} événement(s) seraient purgés.'
            ))
            return

        deleted_count = 0
        with transaction.atomic():
            for event in candidates:
                for photo in event.photos.all():
                    photo.image.delete(save=False)
                event.delete()
                deleted_count += 1

        self.stdout.write(self.style.SUCCESS(f'\n{deleted_count} événement(s) purgé(s).'))
