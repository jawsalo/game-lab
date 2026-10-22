# Grim Dawn Item Catalog and Item Cards

This note explains how the pinned Grim Dawn catalog is stored, queried, and turned into the display-safe item-card API. It is intended as project context for maintainers and AI assistants.

## What the catalog represents

The catalog is the game's canonical item-record dataset. It is **not** a player's character or stash inventory. Personal stash snapshots, ownership, and duplicate detection are separate future Phase 2 work.

The API packages a read-only SQLite database for Grim Dawn **1.3.1.0**:

- 8,695 item records
- Database: `apps/api/data/grim-dawn/1.3.1.0/items.sqlite`
- Provenance: `apps/api/data/grim-dawn/1.3.1.0/provenance.json`
- Source: `jawsalo/grimtools-data`, commit `b21b33be1c7346a1ca12a3cc83e2b476c9aa220b`
- SHA-256: `ed3edbf2d8dd7ec6333bc777c38eafdc5b9905993755b99c2fec868ebfb16b4b`

The provenance manifest pins the source commit, source path, byte size, hash, game version, and record count. The validator checks those values, SQLite integrity/application/schema identifiers, embedded metadata, and that both the item table and full-text index have the expected row count.

## Request paths

The FastAPI router is `apps/api/app/grim_dawn.py`; SQLite access and search are in `apps/api/app/catalog.py`; the card contract and mapper are in `apps/api/app/item_card.py`.

| Route | Purpose |
| --- | --- |
| `GET /api/grim-dawn/catalog` | Game/schema version, count, and available group/category facets |
| `GET /api/grim-dawn/items` | Full-text search, filters, and bounded pagination |
| `GET /api/grim-dawn/items/{id}` | Full catalog item record, including source fields and decoded raw record |
| `GET /api/grim-dawn/items/{id}/card` | Structured display-safe item card |

Search parameters: `q`, `group`, `category`, `slot`, `rarity`, `levelMin`, `levelMax`, `limit`, and `offset`. The page limit is 1–100 (default 50). Search tokenizes case-insensitively and uses prefix matching for each token; tokens are ANDed. Exact item-name matches rank first, then name-prefix matches, then other matches. Results have stable name/id ordering within those ranks.

Unknown IDs return 404. A missing or invalid packaged catalog makes readiness fail and item routes report the catalog as unavailable.

## Storage model and normalized item fields

The item table has a normalized/search-friendly layer plus the original source record as JSON. These are the SQLite storage column names; `_item_summary()` maps them to camelCase API names (see below):

| Storage column | Meaning |
| --- | --- |
| `id` | Source item ID, such as `it11751`; used for lookup and recipe references |
| `name`, `name_sort` | Resolved display name and normalized case-folded sort/search name |
| `name_tag` | Original localization token for the name, when present |
| `name_source`, `name_source_item_id` | How a resolved name was obtained and source item ID when borrowed/inherited |
| `description` | Resolved display description, nullable |
| `description_tag` | Original localization token for the description, when present |
| `item_group` | Broad catalog grouping, e.g. `equipment` or `recipe` |
| `category`, `category_code` | Human-readable source category and compact source category code |
| `slot` | Derived equipment slot, nullable for records without a slot |
| `rarity` | Rarity, nullable when not provided |
| `level_requirement`, `item_level` | Normalized requirement and source item level; either may be null |
| `bitmap` | Game-relative image path, nullable |
| `mods_json` | JSON array of expansion/mod identifiers |
| `record_json` | Original compact source record, preserved as JSON |

The catalog code maps storage column names to API names in `_item_summary()`. For example, database `item_group` becomes API `group`; `level_requirement` becomes `levelRequirement`; `mods_json` is decoded to `mods`; and `record_json` is decoded to `record`.

The API opens SQLite with `mode=ro&immutable=1` and `PRAGMA query_only = ON`. Application code must not mutate this canonical catalog.

## The compact source-record keys

`record_json` preserves the source's compact record keys and long-form property keys rather than discarding information during ingestion. The compact keys are source-format identifiers, not the card API's field names.

Keys observed in the pinned 1.3.1.0 catalog (counts are out of 8,695 records):

| Source key | Safe interpretation |
| --- | --- |
| `a` | Name/localization token, mostly on equipment (6,671 records; always equals `name_tag` when present) |
| `d` | Name/localization token, mostly on non-equipment groups such as recipes, augments, lore and quest items (1,903 records; equals `name_tag` in 1,895). 8 records carry both `a` and `d`; 129 carry neither |
| `b` | Description/localization token when present (2,348 records; always equals `description_tag`) |
| `f` | Rarity, e.g. `Legendary` or `Epic` |
| `l` | Compact category code, e.g. `c43` or `c48` |
| `n` | Bitmap path |
| `k` | Level requirement in the equipment examples |
| `itemLevel` | Item level |
| `mods` | Expansion/mod identifiers, e.g. `["gdx2"]` |
| `artifactName` | Output item ID for a crafting formula |
| `reagent…BaseName`, `reagent…Quantity` | Recipe ingredient IDs and quantities |
| `artifactCreateQuantity`, `artifactCreationCost` | Recipe output quantity and crafting cost |

Do not assume `a` or `d` alone identifies the name token; inspect both. `name_tag` is the normalized column for the source localization token; `name` is the resolved display text. A resolved description can also exist when the raw record has no `b`, so `b` is not a complete test for whether `description` is populated.

These counts describe this exact catalog artifact, whose SHA-256 is recorded above; they are measured data findings, not guarantees of the source format or future game versions. Recheck them when the pinned artifact changes. Do not infer undocumented meanings for other short keys from their names or frequency. Preserve unknown source keys. Long-form keys such as `characterLife`, `defensiveAether`, `offensivePhysicalModifier`, and `skillCooldownReduction` are source property identifiers; the card retains these exact identifiers as property keys.


### Rechecking the data-derived findings

The counts above were obtained by inspecting the pinned SQLite artifact, not by a runtime guarantee in the API. To reproduce or update them after changing the artifact, run a read-only script against the exact file and record its SHA-256 alongside the results. At minimum, count source keys in `record_json` and compare candidate localization keys with `name_tag` / `description_tag`; do not treat a key count as proof of meaning. The API's `/api/grim-dawn/items/{id}` endpoint is useful for spot-checking individual records, while the card endpoint shows exactly which fields the UI projection omits.

## Localization and missing descriptions

Names/descriptions are not guaranteed to be ordinary prose in the source record. They can be localization tokens that need resolution against game text data. The normalized `name` and `description` are the resolved display values; `name_tag` and `description_tag` retain the original tokens for diagnosis and traceability.

A null description is valid catalog data. Example: `Blueprint: Myrmidon Visor` (`it10`) has a resolved name and name tag `tagBlueprint_ArmorC010`, but no description or description tag. Its source record has `d` for the name token and no `b` description token. The card therefore omits the `description` property instead of fabricating text. A missing description does not mean the item itself is missing.

Descriptions can contain game markup tokens such as `^n`, `^w`, and `^o`. The card mapper converts those markers into semantic text segments:

- `^n` → default style
- `^w` → white style
- `^o` → accent style

The marker changes the style of following text; the marker itself is removed. Unknown markup tokens are not currently interpreted by this mapper.

### Unresolved references inside source records (known gap)

Only item names and descriptions have a resolved display form in the current API. Other references in `record_json` remain raw identifiers. In the pinned catalog inspection, there was no lookup table for the skill/controller identifiers described below; recheck the SQLite schema if the catalog artifact or source pipeline changes:

- **Granted-skill localization tags.** `augmentSkillName1`…`augmentSkillName4` hold skill-name tags such as `tagClass04SkillName05E` or `tagGDX2Class09SkillName02A`, with levels in `augmentSkillLevelN`. The class number in the tag identifies the mastery, but the skill's display text requires the game's localization data.
- **Compact skill/controller IDs.** `itemSkillName` (e.g. `sk468`), `itemSkillAutoController` (e.g. `ct11`) and similar values are source-export IDs, not game localization tags. They need a skill/controller table from the same export that produced `items.sqlite`; game text files alone cannot resolve them.

An earlier scan found roughly 6,000 records with at least one granted-skill field. Treat that as an approximate, version-specific measurement until it is reproduced against the pinned artifact. Until resolution data exists, consumers should present those values as unresolved (or name only the mastery) rather than guess skill names.

Proposed resolution (not yet implemented): build the tables in the source pipeline (`jawsalo/grimtools-data`), not in the API. Add a `tags` table (localization tag → English text, extracted from the game's `Text_EN.arc`, with base text loaded before expansion text so later definitions win) and a `skills` table (compact `sk`/`ct` ID → tag and resolved name) from the same export as the items. Pin both to the same game version with the same provenance and hash checks, ship them in the packaged SQLite file, and have the card mapper join against them.

## Item-card contract

The card is deliberately a **projection** of the full record. It provides useful, typed display fields without returning the entire raw source record.

Top-level fields:

- Identity/classification: `id`, `name`, `group`, `category`, `slot`, `rarity`
- Levels/art: `levelRequirement`, `itemLevel`, `bitmap`
- `description`: nullable array of `{text, style}` segments
- `expansions`: expansion IDs copied from source `mods`
- `properties`: array of `{key, value}` numeric gameplay properties
- `conversions`: array of `{from, to, percentage}`
- `recipe`: nullable crafting recipe object

### Properties

The mapper includes numeric fields whose source key begins with `character`, `defensive`, `offensive`, or `skill`. It sorts them by key for deterministic responses. Booleans are excluded even though Python treats booleans as integers. The three conversion fields are excluded from properties because they are represented separately. Other source fields (levels, affix limits, rarity, bitmap, recipe fields, etc.) are not numeric gameplay properties and do not appear here.

**Known omission:** the prefix rule also drops real gameplay stats that use other prefixes. Notably, `retaliation…` keys (e.g. `retaliationPoisonMin`) and granted skills (`augmentSkill…`, `itemSkill…`) are absent from cards. A catalog scan reported `retaliationPoisonMin` on 408 equipment records; rerun that count against the pinned artifact before treating it as current. A card is therefore not a complete stat list; use the full item endpoint (`record`) when completeness matters. Example: Ring of the Black Matriarch (`it9040`) was observed with poison retaliation and four +2 skill bonuses in its record that do not appear on its card; verify the current record before relying on the exact values.

Example:

```json
"properties": [
  {"key": "characterLife", "value": 300},
  {"key": "defensiveAether", "value": 25}
]
```

These keys are intentionally not renamed to presentation labels. A future UI label/dictionary layer can translate them without losing the source key.

### Conversions

A conversion is emitted only when all three source values exist with expected types:

- `conversionInType` → card `from`
- `conversionOutType` → card `to`
- `conversionPercentage` → card `percentage`

Example: `{"from":"physical","to":"vitality","percentage":100}`.

### Recipes

A recipe is emitted when source `artifactName` contains an output item ID. The card includes:

- `outputItemId`
- `outputQuantity` (defaults to 1)
- `craftingCost` (nullable)
- `ingredients`: `{itemIds, quantity}` entries

Source `reagent1BaseName`, `reagent2BaseName`, etc. can hold one item ID. `reagentBaseBaseName` can hold one ID or a list of alternatives; alternatives are represented together in one `itemIds` array. The matching quantity comes from `reagentNQuantity` or `reagentBaseQuantity`, defaulting to 1. Ingredient IDs point back to catalog item IDs and can be resolved with the item endpoint. The card exposes IDs, not nested ingredient cards.

## Example: full item versus card

A full `GET /api/grim-dawn/items/it11751` response includes normalized fields, traceability fields such as `nameTag` and `descriptionTag`, and `record` with its raw source keys.

The `GET /api/grim-dawn/items/it11751/card` response instead includes a compact presentation contract. For Serenity, it includes the Relic slot, Legendary rarity, level 90, the `gdx2` expansion, and its numeric properties. It does not expose `record` or `mods` as raw fields.

## Source-of-truth code

- `apps/api/app/catalog.py` — read-only SQLite connection, catalog metadata, normalized summaries, search and item lookup
- `apps/api/app/grim_dawn.py` — HTTP routes and query validation
- `apps/api/app/item_card.py` — card schema and mapping rules
- `apps/api/tests/test_catalog.py` — catalog search/lookup/readiness regression tests
- `apps/api/tests/test_item_card.py` — description markup, omission of null description, properties/conversions, and recipes
- `scripts/validate-grim-dawn-catalog.py` — artifact/provenance/schema/integrity checks

When changing these behaviors, update the tests and this note together. Treat the pinned source data and implementation as authoritative if this prose ever drifts. For data-derived counts or item examples, include the catalog version/hash and a reproducible query or script.
