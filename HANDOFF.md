# HANDOFF — KPS Studio / PhotoShare

## État au 2026-08-24 (v2 — refonte visuelle + logique paiement)

Le MVP fonctionne de bout en bout avec la nouvelle logique métier validée par l'utilisateur
(paiement → activation du lien) et une UI calquée sur la maquette Figma partagée
(`https://www.figma.com/design/eXbqrjf5HYogVrv9yfcx9P/PhotoShare-KPS`).

### Fait (v1 — socle)

- Restructuration `apps/` + `config/`, `CustomUser` (UUID, e-mail, rôles), `Event`/`Photo`/`ShareLink`.
- Authentification par e-mail, isolation stricte par photographe (404, jamais 403).
- CRUD événement, upload multiple (drag & drop + progression), suppression de photos.
- Galerie publique sans compte, téléchargement individuel et ZIP groupé.
- Commande `purge_expired_events --dry-run`.

### Fait (v2 — cette itération)

- **Logique paiement → lien** : `Event.is_paid`/`paid_at`/`expires_at` (nullable), méthodes
  `mark_paid()` / `mark_unpaid()` / `extend_expiration()`. Tant qu'impayé : pas de lien exploitable,
  pas de décompte. `EventForm` de création propose une case à cocher au lieu d'une date libre.
- **L'admin est aussi photographe** : `create_superuser` fixe `is_photographer=True` par défaut ;
  le compte admin existant a été mis à jour en conséquence.
- **Compteurs** : `Event.view_count` / `download_count` (incrémentés via `F()` dans `apps/gallery/views.py`),
  agrégés sur le dashboard admin (`total_photos`, `total_storage` via `humanize_bytes`).
- **Accès client par code** : `gallery:access_by_code` (`POST /access/`) — réutilise le token du
  `ShareLink` comme « code », affiché aussi côté photographe sur la fiche événement.
- **Page d'accueil vitrine** (`templates/home.html`, vue `config/views.py::home`) : présentation
  KPS (photographie / imprimerie / design graphique), CTA connexion, formulaire code d'accès.
- **Refonte visuelle sidebar** : `templates/base.html` (shell connecté, nav conditionnelle par rôle)
  et `templates/public_base.html` (pages publiques centrées) remplacent l'ancienne navbar horizontale.
- **Thème clair/sombre** : tokens CSS dans `static/css/main.css`, bascule via `static/js/theme.js`
  (persistance `localStorage`, respecte `prefers-color-scheme` par défaut).
- **Nouveaux champs `CustomUser`** : `phone`, `public_contact_email`, `website`, `address`, `logo`
  (utilisés en Settings, page « lien expiré », dashboard admin).
- `PURGE_AFTER_EXPIRATION_DAYS` par défaut passé à **15 jours** (au lieu de 30) ; les événements
  jamais payés (`expires_at=None`) ne sont jamais purgés.
- Migrations réinitialisées proprement (0001) après les changements de modèle — aucune donnée de
  prod à préserver à ce stade.

### À faire / connu

- **Comparaison pixel-perfect au Figma non faite** : l'UI reprend la structure (sidebar, cartes,
  badges, thème) et les libellés vus sur les captures partagées, mais n'a pas été calquée précisément
  (espacements, typographies exactes, icônes SVG vs emojis utilisés comme placeholders).
- Le « code d'accès » réutilise le token long du `ShareLink` (pas un code court dédié) — plus simple
  et plus sûr, mais moins agréable à recopier à la main ; à revoir si un vrai besoin de code court apparaît.
- Aucune suite de tests automatisés versionnée (validation manuelle via scripts `test.Client`, non commités).
- Pas de tâche planifiée réellement configurée sur cette machine pour `purge_expired_events`
  (commande `schtasks` documentée dans `README.md`, non exécutée).
- PostgreSQL non branché (SQLite en dev).
- Settings « Preferences » / « Branding » vus sur la maquette (onglets additionnels) non implémentés —
  seuls « Company Info » et « Sécurité » existent actuellement.
- Pas de génération de miniatures (les photos sont servies en taille réelle, redimensionnées en CSS).

### Décisions prises pendant ce chantier (à connaître avant de retoucher le code)

- Isolation : 404 (jamais 403) pour ne pas révéler l'existence d'un événement à un autre photographe.
- `mark_unpaid()` ne réinitialise pas `paid_at`/`expires_at` (historique conservé) ; un nouveau
  `mark_paid()` recalcule toujours `paid_at`/`expires_at` à l'instant présent.
- `download_count` compte des *actions* de téléchargement (1 par clic, y compris pour un ZIP
  contenant plusieurs photos), pas le nombre de fichiers.
- ZIP généré en mémoire (`zipfile` + `BytesIO`) — suffisant pour une galerie événementielle.
