# Game Lab Session 4 Handoff — Snapshot Crosswalk

**Checkpoint date:** November 2, 2026  
**Project stage:** Phase 2, Grim Dawn snapshot identity mapping.

## Current state

The app, pinned Grim Dawn 1.3.1.0 catalog (8,695 records), and open-source observability stack remain in place. PR #31 fixed SQLite temporary sort storage; a direct read-only integrity check returned `ok`. The user's game build is 1.3.1.1, a hotfix without item-data changes.

The parser opens the user's game files and exposes item instances and DBR paths. Stable catalog identity mapping is now proven for a seed set, but the complete crosswalk is not done. Full evidence and the mappings are in [DBR-CATALOG-CROSSWALK.md](DBR-CATALOG-CROSSWALK.md).

## Crosswalk progress

- The saved gd-edit exports contain 978 overlapping path headings across eight output chunks. They deduplicate to 418 unique records in `records/items/gearweapons/caster/`.
- The saved catalog query contains 77 IDs across 15 repeated generic caster names. All 77 matched exactly one caster DBR when resolved `itemNameTag`, `itemLevel`, and the full exported `offensive*` property set were compared.
- The other 341 caster DBR paths remain unmapped. Other item categories are not exhaustively covered.
- Targeted non-caster cases were checked, including the Aetherial Missive/Mutagen/Wendigo Spirit recipes, three Beronath’s Celestial Horn formulas, Bolstered potion formulas, Dagallon recipes, and Wayfinder Reports. The crosswalk labels default-item rows without a distinct DBR as unresolved instead of inventing a path.
- The earlier 24 coarse-fingerprint collision groups are meaningful variants or shared-name/icon cases, not proof that the catalog data is poisoned. The coarse fingerprint is not a unique identity key.
- Positive controls remain: Apoclypton's Gaze `d309_head.dbr` → `it14668`; Bloodfang Oil `oil_bleed01.dbr` → `it310`.

## Next work

1. Extend the mapping beyond the 77-entry seed, using reproducible source exports that contain no character or stash inventory data.
2. Track unique, ambiguous, and missing matches separately; do not infer an identity from name alone.
3. Finish parser license/version compatibility and validate against 1.3.1.0 fixtures.
4. Before accepting uploads, implement owner authentication, bounded temporary upload, and a read-only parse preview as specified in [the snapshot import contract](SNAPSHOT-IMPORT-CONTRACT.md).
5. Check live VPS capacity before selecting persistence/storage details.

## Privacy and workflow

Do not repeat the failed launcher/transcription attempts. Do not commit save files, raw private inventory exports, or unrelated terminal output. No save was modified and no application or pipeline code changed in this investigation.

See [ROADMAP-V9.md](ROADMAP-V9.md) for the wider priority order. Datadog remains deferred until the app has a useful snapshot workload and repeatable failure scenarios.
