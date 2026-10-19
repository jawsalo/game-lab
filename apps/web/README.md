# Web app

The mobile-first static web application is served by an unprivileged NGINX container. Browser requests use same-origin `/api` routes so the application does not own deployment hostnames.

The current interface provides:

- Platform and API readiness state.
- Grim Dawn catalog version and record count.
- Full-text item search.
- Dynamic group and rarity filters.
- Responsive result cards with category, slot, rarity, description, and level information.

The catalog represents every known game item. Personal inventory uploads and ownership views are a later, separate feature.
