# PROJECT_PROGRESS — KPS Studio / PhotoShare

Suivi par rapport aux phases du cahier des charges (section 12).

> **v2 (2026-08-24)** : refonte visuelle sidebar + thème clair/sombre calqués sur la maquette Figma
> réelle, logique métier paiement → activation du lien (au-delà du cahier initial, validée avec
> l'utilisateur), compteurs vues/téléchargements, page vitrine KPS, accès client par code. Détails
> complets dans `HANDOFF.md`.

| Phase | Contenu | Statut |
|---|---|---|
| 1 | Socle (Django, apps, migrations, admin) | ✅ Fait |
| 2 | Authentification, rôles, isolation, paramètres | ✅ Fait |
| 3 | Événements (CRUD, expiration, dashboard) | ✅ Fait |
| 4 | Photos (upload multiple, stockage, suppression) | ✅ Fait — miniatures non générées (affichage en taille réelle via CSS) |
| 5 | Galerie client (lien public, vitrine, téléchargements) | ✅ Fait |
| 6 | Administration et statistiques | ✅ Fait (stats simples : compteurs) |
| 7 | Automatisation (expiration, purge) | ✅ Fait — pas de notification e-mail, pas de tâche planifiée en place |
| 8 | Tests et intégration | ⚠️ Partiel — validation manuelle des 10 scénarios (section 13), pas de suite automatisée versionnée |
| 9 | Déploiement | ❌ Non fait — SQLite en dev, PostgreSQL prêt via `DATABASE_URL` mais non testé en réel |

## Scénarios de validation (section 13)

Tous vérifiés manuellement le 2026-08-24 via le test client Django (script non versionné) :

1. Connexion — ✅
2. Isolation (photographe B → événement de A) — ✅ 404
3. Création d'événement — ✅
4. Upload multiple — ✅
5. Partage (lien généré) — ✅
6. Client sans compte — ✅
7. Téléchargement — ✅ (individuel + ZIP)
8. Expiration — ✅ page 410
9. Purge (`--dry-run` puis réel) — ✅
10. Administration (vue globale) — ✅

## Prochaines étapes suggérées

1. Comparaison fine (pixel) des templates à la maquette Figma (espacements, icônes SVG, typographies).
2. Écrire une suite de tests automatisés par app (`apps/*/tests.py`), un par domaine (cf. répartition DEV1/DEV2/DEV3 du cahier).
3. Configurer PostgreSQL et valider la bascule via `DATABASE_URL`.
4. Planifier réellement `purge_expired_events` (Task Scheduler / cron — commandes documentées dans `README.md`).
5. Implémenter les onglets Settings restants vus sur la maquette (Preferences, Branding).
6. `git add` + premier commit, puis mettre en place les branches `main`/`develop` (section 11 du cahier).
