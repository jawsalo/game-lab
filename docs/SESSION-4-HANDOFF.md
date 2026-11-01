# Game Lab Session 4 Handoff — Snapshot Crosswalk

**Checkpoint date:** October 28, 2026  
**Project stage:** Phase 2, snapshot parser and catalog identity mapping.

## Current state

The app, Grim Dawn 1.3.1.0 catalog (8,695 records), and open-source observability stack remain in place. PR #31 fixed SQLite temporary sort storage. The public API successfully returned a 100-record page at offset 1100; SQLite integrity was confirmed as `ok`.

The current blocker is resolving an item instance's game DBR path to its stable GrimTools catalog ID. The catalog pipeline preserves `it...` IDs and item properties, but not the DBR path, so name-only or coarse fingerprint matching cannot establish identity.

## Findings from this session

- Full scan covered all 8,695 catalog records.
- A coarse fingerprint produced 24 collision groups. These were meaningful variants, not catalog poisoning: Arcane Wand records vary in elemental base damage; Aetherial Missive recipes vary in crafting cost and reagents.
- Confirmed positive mapping checks:
  - Apoclypton's Gaze: `records/items/gearhead/d309_head.dbr` → `it14668`.
  - Bloodfang Oil: `records/items/crafting/consumables/oil_bleed01.dbr` → `it310`.
- gd-edit's caster directory query returned 418 records, and a 42-line batch (query plus 41 `qshow` commands) completed inside the already-loaded interactive program.
- The query output was later preserved in the user's Library as `gd-edit-caster-part-04-output.txt` through `gd-edit-caster-part-09-output.txt`. I checked the headings across all six files: they contain 898 occurrences with overlap, which deduplicate to exactly 418 unique caster DBR paths. Parts 04–06 are cumulative captures; parts 07–09 contain later/overlapping captures.
- The separate `Pasted text(20261031-013530).txt` contains catalog-side property output for 77 entries across 15 repeated caster-weapon names. No generated crosswalk file is in the repo yet.
- The original launcher and transcription failures are still relevant: do not repeat those attempts. No save files were changed; no private save or inventory output should be committed.

## First task next session

1. Use the six saved Library output files; do not rerun the 418-record export.
2. Parse and deduplicate the 418 source records by DBR path, then compare them with the saved catalog-side output. Build a versioned DBR path → catalog ID crosswalk and report unique, missing, and ambiguous mappings separately. Validate with the two positive examples above.
3. Continue with only the still-flagged non-caster collision groups (recipes/formulas and quest items); do not scan or hand-review all 8,695 catalog records again.
4. Once the identity mapping gate passes, continue parser compatibility, owner authentication, upload limits, read-only preview, and persistence in the order documented in [the snapshot import contract](SNAPSHOT-IMPORT-CONTRACT.md).

## Roadmap

See [ROADMAP-V9.md](ROADMAP-V9.md) for the broader project sequence. Datadog remains deferred until the app has a useful snapshot workload and repeatable failure scenarios.
