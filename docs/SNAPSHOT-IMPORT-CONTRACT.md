# Grim Dawn Character and Stash Snapshot Import Contract

**Status:** Direction selected October 27, 2026; parser and security gates remain before implementation  
**Product goal:** Let the owner search personal character and stash snapshots against the shared Grim Dawn catalog, identify owned copies, and compare snapshots over time.

## Input decision

The first importer is intended to accept **Grim Dawn's own character and stash save files**. The user selected these over a GrimTools build link or a third-party stash export.

Target file types:

- `player.gdc`: a character save, including that character's own state and personal stash.
- `transfer.gst`: the softcore shared stash.
- `transfer.gsh`: the hardcore shared stash.

A character's personal stash and the shared stash are separate sources; a snapshot may include one or more character files and a shared stash file. The first upload flow must let the user explicitly choose the files that make up one snapshot. Do not silently merge files from different uploads.

The canonical save-folder guide on the Crate forum describes the character folders and shared stash files separately: [Moving saves from Steam Cloud to Grim Dawn's default location](https://forums.crateentertainment.com/t/how-to-move-your-saves-from-steam-cloud-to-grim-dawns-default-location/28921/1).

## Compatibility gate

Do not assume that a parser handles the user's game version just because it can open an older save.

- The public save-decryption implementation linked from the Crate forum says it was tested for Grim Dawn 1.1.9.1 and warns that it may contain bugs: [Save File Decryption Tools](https://forums.crateentertainment.com/t/tool-save-file-decryption-tools/110765).
- The Crate forum's GD Stash thread reports support for the 1.3.0.0 save format in its version history, but that alone does not establish compatibility with this project's pinned 1.3.1.0 catalog: [GD Stash](https://forums.crateentertainment.com/t/tool-gd-stash/29036/).

Before accepting real uploads, select a parser with a clear license and verify it against unmodified 1.3.1.0 character and stash fixtures. If a compatible parser is not available, stop at file identification and report the limitation rather than storing a misleading or partial inventory.

## Privacy and access contract

- Snapshots are personal data and private to one owner. The current app has no user authentication; do not add a public upload or read endpoint until an owner-authentication boundary is in place.
- Begin with one owner for this single-user deployment. Do not introduce public signup, shared inventories, or multi-user collaboration in the MVP.
- Never modify, repair, or write back a game save file. Upload and import are read-only with respect to the source files.
- Treat uploaded binaries as untrusted input. Enforce request size, per-file size, file-count, and parser resource limits; validate signatures and detected file type rather than trusting filenames.
- Process original files in temporary storage only. Delete them after parsing or failure; do not persist raw save binaries by default. Persist the normalized snapshot and a content hash for idempotency and auditability.
- Do not log file contents, item-instance payloads, account secrets, or uploaded filenames containing personal paths.
- Keep private snapshot records out of the shared catalog and its readiness/search endpoints.

## Parser spike findings (October 27, 2026)

A read-only inspection of the owner's Grim Dawn 1.3.1.1 character and shared-stash files with gd-edit confirmed that the parser can open these files and expose item instances, locations, stack counts, item names, and source DBR paths. Item instances also expose separate affix, component, augment, and seed fields when present. The source files were not modified or added to this repository.

The inspected game build is 1.3.1.1. Crate's [official 1.3.1.0 + Hotfixes notes](https://forums.crateentertainment.com/t/grim-dawn-version-1-3-1-0-hotfixes/160806) describe 1.3.1.1 as a crash fix for players without Fangs of Asterkarn. The pinned catalog is 1.3.1.0 and contains the 1.3.1 item data; use it for this hotfix build, while retaining the exact game build reported by the parser in snapshot metadata.

The parser's item basename is a game DBR path (for example, records/items/.../*.dbr). The catalog identifies records with GrimTools IDs such as it11751 and preserves the compact item record, but its current schema does not expose the DBR path. Therefore parsing is demonstrated, while reliable catalog identity resolution is not. Do not use a name-only match as a confirmed identity. The next mapping gate is a versioned, generated DBR-path-to-catalog-ID crosswalk with uniqueness checks and fixtures from the parser; ambiguous or absent paths remain unresolved. Never commit the owner's save files or item inventory output as fixtures.

## Snapshot and identity semantics

- One user-confirmed import represents a point-in-time snapshot of the selected character and/or stash files.
- Store snapshots as immutable history. A later upload creates a new snapshot; it does not merge into or overwrite an earlier snapshot.
- Re-uploading identical file content is idempotent: report the existing import rather than creating duplicate item records.
- Preserve the source category and location for each item: equipped, carried, character personal stash, or shared stash when the parser exposes that distinction.
- Preserve per-instance rolls, affixes, bindings, and item-level data when available. Two copies of the same catalog item are separate owned instances; they must not collapse into one row.
- Resolve known item records to stable catalog IDs. Keep unresolved records visibly flagged with parser/source metadata; never discard them or guess a match.
- Keep character identity and difficulty mode distinct. Do not assume character names alone are globally unique.
- A parsed snapshot is not automatically current or authoritative. The UI should show its import time and source so the owner can select which snapshot to browse.

## First usable slice

Implement in small gates:

1. **Parser spike and fixtures:** identify a maintained, licensed parser and test 1.3.1.0 `player.gdc`, `transfer.gst`, and `transfer.gsh` fixtures without changing the files. Document parser/version support and expected counts.
2. **Owner access and upload limits:** add a single-owner authentication boundary and bounded temporary upload handling. The app is currently public and unauthenticated, so this precedes any private snapshot endpoint.
3. **Read-only parse preview:** show detected character/stash type, game/parser version when available, counts, and unresolved records. Nothing is saved until the owner confirms import.
4. **PostgreSQL persistence:** after checking live VPS capacity, introduce migrations and separate snapshot tables. Keep the pinned catalog in immutable SQLite; do not migrate or mutate it.
5. **Owned-item lookup:** search one selected snapshot, distinguish duplicate item instances, and compare snapshots. Add cleanup/deletion and backup/restore behavior before relying on retained personal data.

## MVP acceptance criteria

- A valid 1.3.1.0 character or stash file is identified and parsed by a tested, licensed parser.
- Invalid, unsupported, oversized, and malformed inputs fail with a useful message and leave no raw upload behind.
- Preview explicitly distinguishes character personal stash from softcore/hardcore shared stash.
- Import confirmation persists a private, immutable snapshot under the authenticated owner; repeated identical uploads do not create duplicates.
- Owned item instances preserve their catalog identity, location, rolls/affixes where available, and unresolved status.
- The shared catalog search and public endpoints cannot expose personal snapshot data.
- The source save files remain byte-for-byte unchanged.

## Out of scope for the first slice

- Writing items or character changes back into the game.
- Steam Cloud access, automatic folder scanning, or background synchronization.
- Reading GD Stash's private database or custom export format.
- GrimTools build links as inventory evidence.
- Public accounts, sharing, trading, recommendations, or an autonomous remediation/MCP action.
- Starting the Datadog trial before a useful snapshot workload and repeatable failure scenarios exist.
