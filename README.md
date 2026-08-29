# KPS Studio / PhotoShare

Application web de partage de photographies pour photographes professionnels — voir
[`Cahier_des_charges_KPS_Studio_PhotoShare.md`](../Cahier_des_charges_KPS_Studio_PhotoShare.md) à la racine du dépôt.

## Stack

- Python 3.13 / Django 5.1
- SQLite en développement, PostgreSQL en production (via `DATABASE_URL`)
- 3 apps : `apps.accounts`, `apps.events`, `apps.gallery`

## Installation

```bash
# Depuis c:\Users\HP\Desktop\photoShare (racine contenant env/ et photoShare/)
./env/Scripts/pip install -r photoShare/requirements.txt

cd photoShare
cp .env.example .env   # ajuster si besoin (PostgreSQL, SECRET_KEY, etc.)
python manage.py migrate
python manage.py createsuperuser
```

## Lancement

```bash
python manage.py runserver
```

- `/` — page vitrine KPS Studio (publique) + accès galerie par code
- `/login/` — connexion (admin ou photographe)
- `/dashboard/` — espace photographe (« My Events »)
- `/admin-dashboard/` — espace administrateur (« Overview »), accessible à un admin qui est aussi photographe
- `/admin/` — administration Django (super-utilisateur)

## Thème clair / sombre

Bouton de bascule dans la sidebar (espaces connectés) et en haut à droite (pages publiques).
Préférence mémorisée en `localStorage`, respecte `prefers-color-scheme` par défaut.

## Basculer vers PostgreSQL

Renseigner dans `.env` :

```
DATABASE_URL=postgres://user:password@localhost:5432/kps_studio
```

Aucune modification de code nécessaire (`dj-database-url` dans `config/settings.py`).

## Logique paiement → lien de partage

Un événement est créé avec un statut **payé/impayé** (case à cocher au moment de la création,
ou bouton dédié sur la fiche événement ensuite). Tant qu'il est impayé :
- le lien de partage n'est pas exploitable (page « en attente » côté client) ;
- le délai d'expiration de 15 jours ne démarre pas (`expires_at` reste `null`).

Dès que le photographe le marque **payé**, `paid_at` est fixé à cet instant et
`expires_at = paid_at + 15 jours` — c'est ce qui active le lien. Aucune passerelle de paiement
réelle n'est intégrée (conforme au cahier des charges, section 16) : c'est un simple indicateur manuel.

## Accès client par code

En plus du lien direct (`/g/<token>/`), le client peut saisir le token comme un « code d'accès »
sur la page d'accueil (`/`), via `POST /access/`, pour être redirigé vers sa galerie.

## Purge des événements expirés

```bash
python manage.py purge_expired_events --dry-run   # simulation
python manage.py purge_expired_events              # suppression réelle
```

Le délai par défaut (**15 jours** après expiration) se configure via `PURGE_AFTER_EXPIRATION_DAYS` dans `.env`.
Les événements jamais payés (`expires_at` non défini) ne sont jamais purgés par cette règle.

### Planifier la purge

**Windows (dev), via le Planificateur de tâches :**

```powershell
schtasks /create /tn "KPS Studio - Purge" /sc daily /st 03:00 ^
  /tr "C:\Users\HP\Desktop\photoShare\env\Scripts\python.exe C:\Users\HP\Desktop\photoShare\photoShare\manage.py purge_expired_events"
```

**Linux (prod), via cron :**

```cron
0 3 * * * /path/to/env/bin/python /path/to/photoShare/manage.py purge_expired_events >> /var/log/kps-purge.log 2>&1
```

## Tests

Aucune suite de tests automatisés (`pytest`/`unittest`) n'est encore écrite — voir `PROJECT_PROGRESS.md`.
Les 10 scénarios de validation du cahier des charges (section 13) ont été vérifiés manuellement via le test client Django lors du développement.

## Structure

```
apps/accounts/   # CustomUser, auth, profil, gestion des utilisateurs, dashboard admin
apps/events/     # Event, Photo, ShareLink, dashboard photographe, upload, purge
apps/gallery/    # vues publiques : galerie client, téléchargement, page expirée
config/          # settings, urls, wsgi/asgi
templates/, static/
```
