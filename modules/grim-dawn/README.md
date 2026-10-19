# Grim Dawn module

The first production feature is a searchable canonical item catalog for Grim Dawn 1.3.1.0.

## Current catalog

- 8,695 records from the freshly captured GrimTools 1.3.1.0 item database and English localization.
- Versioned SQLite artifact packaged read-only inside the API image.
- Provenance pins the source repository commit, source path, byte size, and SHA-256.
- SQLite FTS5 supports item-name and description search.
- Groups distinguish equipment, components, augments, recipes, consumables, lore, quest items, unlocks, and cosmetics.
- Exact names rank ahead of related items such as blueprints.

The authoritative extraction and catalog-building pipeline lives in `jawsalo/grimtools-data`. Game Lab vendors one verified immutable database so builds and runtime startup require no cross-repository credentials or downloads.

## API

- `GET /api/grim-dawn/catalog` — version, record count, groups, and categories.
- `GET /api/grim-dawn/items` — search, filtering, and bounded pagination.
- `GET /api/grim-dawn/items/{id}` — complete record by stable item ID.

Search filters include `q`, `group`, `category`, `slot`, `rarity`, `levelMin`, and `levelMax`.

## Data boundary

The catalog answers “what items exist in the game?” It is not a record of items the user owns.

Personal character and stash snapshots will be introduced as a separate read-only ingestion path with explicit upload metadata, persistence, ownership, and duplicate detection. Canonical game data must remain independently replaceable and reproducible.

Grim Dawn, its names, and third-party source data remain the property of their respective owners.
