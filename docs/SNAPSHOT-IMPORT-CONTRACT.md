# Grim Dawn Character and Stash Snapshot Import Contract

**Status:** Authenticated, bounded, temporary-only preview route and pinned parser runtime are merged (PRs #86–87). Preview is disabled by default pending approved, version-known compatibility fixtures and production runtime verification. No snapshot persistence exists yet.
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

The selected parser is gd-edit 0.2.586 under EPL-1.0. PR #87 packages the pinned upstream Linux release, its LICENSE and THIRD-PARTY notices, the read-only worker, and Java 21 in the API image. The parser was locally smoke-tested against the user's unmodified 1.3.1.1 character and stash files, but that does not close the compatibility gate. Before enabling preview for real uploads, verify the packaged runtime against fixtures with confirmed Grim Dawn version, expected aggregate parse results, and permission for local test use. Keep the feature flag off until that verification passes. If suitable fixtures are unavailable, document that limit and do not claim broad compatibility.

## Privacy and access contract

- Snapshots are personal data and private to one owner. The API has a single-owner authentication boundary, and the preview route requires owner authentication and CSRF protection. Snapshot storage and lookup are not implemented.
- Begin with one owner for this single-user deployment. Do not introduce public signup, shared inventories, or multi-user collaboration in the MVP.
- Never modify, repair, or write back a game save file. Upload and import are read-only with respect to the source files.
- Treat uploaded binaries as untrusted input. Enforce request size, per-file size, file-count, and parser resource limits; validate signatures and detected file type rather than trusting filenames.
- Process original files in temporary storage only. Delete them after parsing or failure; do not persist raw save binaries by default. Persist the normalized snapshot and a content hash for idempotency and auditability.
- Do not log file contents, item-instance payloads, account secrets, or uploaded filenames containing personal paths.
- Keep private snapshot records out of the shared catalog and its readiness/search endpoints.

## Parser spike findings (October 27, 2026)

A read-only inspection of the owner's Grim Dawn 1.3.1.1 character and shared-stash files with gd-edit confirmed that the parser can open these files and expose item instances, locations, stack counts, item names, and source DBR paths. Item instances also expose separate affix, component, augment, and seed fields when present. The source files were not modified or added to this repository.

The inspected game build is 1.3.1.1. Crate's [official 1.3.1.0 + Hotfixes notes](https://forums.crateentertainment.com/t/grim-dawn-version-1-3-1-0-hotfixes/160806) describe 1.3.1.1 as a crash fix for players without Fangs of Asterkarn. The pinned catalog is 1.3.1.0 and contains the 1.3.1 item data; use it for this hotfix build, while retaining the exact game build reported by the parser in snapshot metadata.

A follow-up gd-edit database-record inspection confirmed that the game DBR record exposes fields usable for a candidate fingerprint: class/category, localized item name, bitmap path, item level, level requirement, rarity, and gameplay properties. The displayed item-name fields are already resolved to English text, so they do not provide the catalog's original localization tag. Two real save items were compared with the public catalog: an equipment item and a consumable. In both cases, the DBR record and catalog result agreed on exact display name, category, rarity, item level, level requirement where applicable, and bitmap path after normalizing the .tex/.png extension difference. The consumable search also returned a similarly named recipe, which the category and other fingerprint fields distinguished. These are two positive samples, not proof of coverage across all item types or variants. Use the composite fields as candidate fingerprint inputs, require exactly one matching catalog ID, and preserve ambiguous or missing matches as unresolved.

The parser's item basename is a game DBR path (for example, records/items/.../*.dbr). The catalog identifies records with GrimTools IDs such as it11751 and preserves the compact item record, but its current schema does not expose the DBR path. Therefore parsing is demonstrated, while reliable catalog identity resolution is not. Do not use a name-only match as a confirmed identity. The next mapping gate is a versioned, generated DBR-path-to-catalog-ID crosswalk with uniqueness checks and fixtures from the parser; ambiguous or absent paths remain unresolved. Never commit the owner's save files or item inventory output as fixtures.

### Crosswalk investigation checkpoint (November 2, 2026)

The catalog/API sorting issue was fixed in PR #31; read-only SQLite integrity is `ok`, and the 8,695-row catalog remains pinned to Grim Dawn 1.3.1.0. The user's game build is 1.3.1.1, a hotfix build that did not add item data.

A coarse scan of all 8,695 catalog rows found 24 fingerprint collision groups. Investigation of the repeated-name cases showed meaningful variants: caster weapons differ in damage properties; formula records can share a name/icon while differing in ingredients, outputs, or unlock data; quest reports can share a name/icon while containing different text. The coarse fingerprint is useful for finding candidates, never as a unique identity key.

The saved gd-edit exports contain 978 overlapping heading occurrences across eight output chunks, which deduplicate to 418 unique records in `records/items/gearweapons/caster/`. Comparing the saved catalog-side output for 77 IDs across 15 generic caster weapon names against those DBRs yielded 77 unique mappings using resolved `itemNameTag`, `itemLevel`, and the complete exported set of `offensive*` properties. The remaining 341 caster paths are not mapped, and the overall catalog crosswalk is incomplete.

The new [versioned crosswalk seed](DBR-CATALOG-CROSSWALK.md) records those 77 mappings, additional targeted recipe/quest mappings, evidence, and limits. It also preserves the positive checks:

- `records/items/gearhead/d309_head.dbr` — Apoclypton's Gaze — `it14668`.
- `records/items/crafting/consumables/oil_bleed01.dbr` — Bloodfang Oil — `it310`.

Do not commit save files, raw private inventory exports, or unrelated terminal output. The crosswalk document contains only the verified mapping data needed for the next stage.

**Next:** retain the verified 77-entry seed and expand mappings only where a concrete parser fixture or product need requires it. Full catalog coverage is not a precondition for the MVP: known IDs can resolve through the crosswalk while ambiguous or missing IDs remain explicitly unresolved. Proceed with parser compatibility and isolation, then owner authentication, bounded upload, and read-only preview gates before persistence.


## Upstream fixture provenance review (November 2, 2026)

A source-only review of the gd-edit 0.2.586 test suite found useful parser regression cases, but not fixtures that can yet serve as Game Lab's clean 1.3.1.0 compatibility gate:

- `counterstrike.gdc` and `z20.gdc` are described in [item_skills_test.clj](https://github.com/GrimDawn-max/gd-edit/blob/v0.2.586/test/gd_edit/item_skills_test.clj) as saves sent by a forum contributor. The tests expect one and two item-skill entries respectively and state that their character Block 8 version is 5. They do not state the game release that produced the files.
- `NamedTabs.gdc` and `NamedTabs-transfer.gst` are described in [stash_tabs_test.clj](https://github.com/GrimDawn-max/gd-edit/blob/v0.2.586/test/gd_edit/stash_tabs_test.clj) as named-tab regression cases. The tests assert selected tab names, icons/colors, and byte-identical round trips. The same suite identifies `NamedTabs.gdc` as the one save with character Block 8 version 8, but does not identify its game release or provide expected inventory item counts.
- The upstream repository is licensed under EPL-1.0, but no fixture-specific provenance or license note was found alongside these files. Do not copy or redistribute the binaries based solely on the source-code license.

The upstream tests provide evidence that gd-edit's own regression suite covers format edge cases; they do not independently verify parser correctness, expected item counts, or the exact 1.3.1.0 game build. They were inspected but not run in Game Lab, and no upstream binary fixtures were copied.

**Next:** use only fixtures whose provider confirms the game version, expected read-only parse summary, and permission to use them. If none are available, keep the user's files as local smoke-test evidence and use synthetic adapter tests without claiming a clean compatibility result. Do not weaken the real-save compatibility gate for uploads.

## Local parser integration validation (November 2, 2026)

The read-only parser integration is now implemented and its local invocation has been exercised from the user's Windows PC. PR #51 added the Java/Clojure worker boundary and Python wrapper; PR #52 added the PowerShell smoke script. Both are merged to main.

Environment and execution:

- Python 3.13.17 was installed and a repository-local .venv was created. The repository's requirements.txt installed PyYAML 6.0.3.
- Git 2.55.0.windows.5 is installed. The local checkout is on the Desktop; keep personal paths out of committed output.
- The runtime is Temurin Java 25.0.5 with gd-edit standalone JAR 0.2.586. Keep both installed locally; neither is committed to Game Lab.
- The user ran both the Python SnapshotParser.parse_bytes wrapper and scripts/smoke-snapshot-parser.ps1. Results agreed:
  - character: format version 8, 153 item instances in the allowlisted projection.
  - sharedStash: format version 11, 210 item instances in the allowlisted projection.
- PowerShell's default execution policy blocked direct script invocation. The smoke script ran successfully through a child process using powershell.exe -NoProfile -ExecutionPolicy Bypass -File ...; this is process-scoped and did not persistently alter the user's execution policy.

Only aggregate count summaries are recorded. No raw save data, character or item names, local file paths, or individual inventory records were committed. The parser was read-only; neither source save changed. The script's output is an aggregate summary only.

What this establishes: the Java worker can be launched locally, the Python adapter can invoke it and return its minimal projection, and the PowerShell smoke script produces matching format/item-count summaries for these specific user files.

What remains unproven: clean fixtures with confirmed game-version provenance and redistribution permission; broad compatibility beyond these files; exhaustive DBR-to-catalog ID resolution; and upload security/ownership. The game build reported for this user is 1.3.1.1, while the shared catalog is 1.3.1.0. The prior Crate hotfix notes say 1.3.1.1 did not add item data, but do not treat this user-save smoke test as the required clean 1.3.1.0 fixture gate.

The DBR extraction, index, and candidate matching steps are complete; see [Session 6 handoff](SESSION-6-HANDOFF.md). The immediate restart point is the clean parser-fixture and packaged-runtime gate described below, not broad manual mapping work. Keep unresolved item identities explicit. Do not enable preview or plan persistence until the compatibility check is done.

## Preview endpoint and packaged runtime checkpoint (November 8, 2026)

- The DBR index and candidate matcher are implemented; see [DBR-LOCAL-INDEX.md](DBR-LOCAL-INDEX.md) and [DBR-CANDIDATE-MATCHING.md](DBR-CANDIDATE-MATCHING.md). The latest report compared 12,070 catalog category rows against 31,205 item-directory DBRs: 10,588 unique, 1 ambiguous, and 1,481 unmatched. Treat this as evidence coverage, not complete game-item coverage.
- The latest local snapshot check resolved all 173 character item instances across 139 DBR paths. Of 137 shared-stash instances, 132 resolved uniquely; five instances across four paths are known game items outside the catalog, with no catalog IDs or cards assigned. The four paths and their DBR classes are recorded below. Earlier local counts are superseded by this synced-save run.
- PR #86 added `/api/snapshots/preview`, protected by the owner authentication/CSRF boundary, with request and file limits, parser concurrency limits, temporary processing, and an allowlisted response. It does not persist snapshots.
- PR #87 packages gd-edit 0.2.586 from its release archive after checking the pinned byte size and SHA-256, preserves upstream license notices, and includes Java 21 and the worker source. Both CI validation and image-build checks passed. Helm defaults `modules.api.snapshotPreview.enabled` to `false`; keep it disabled until compatibility is verified.
- PR #90 added a local-only snapshot-to-candidate smoke tool. The five missing stash instances are valid inventory records but remain outside the public item catalog and have no catalog IDs/cards assigned: `records/items/misc/potions/potion_attributereset.dbr` (`ItemAttributeReset`), `records/items/misc/difficultyunlock_ultimate.dbr` (`ItemDifficultyUnlock`, two instances), `records/items/misc/potions/potion_devotionreset.dbr` (`ItemDevotionReset`), and `records/items/faction/booster/boosthostile_wendigo_c01.dbr` (`ItemFactionWarrant`). A standalone lookup for these paths is a backlog investigation, not a requirement to block snapshot parsing.
- **Next:** validate the packaged runtime against authorized, version-known fixtures, then test the protected preview route and cleanup behavior. Only then consider enabling preview. Review live VPS capacity before planning PostgreSQL snapshot persistence.

## Backlog — standalone lookup for known non-catalog inventory items

- **Status:** Investigate; not blocking the parser or catalog-match smoke check.
- **Known examples:** the four utility-item DBR paths listed above, covering attribute reset, Ultimate difficulty unlock, devotion reset, and Wendigo faction warrant.
- **Question:** determine whether these and other inventory-bearing DBR records outside the public item catalog merit a general standalone lookup using the local DBR index and layer-aware localization, rather than one-off path mappings or catalog cards.
- **Scope:** begin with a read-only count and classification of inventory item paths absent from catalog coverage across the seven DBR layers (about 98,827 exported DBRs). Estimate likely user value, data volume, maintenance cost, and whether this belongs only in private snapshot metadata or in a separate lookup surface. Do not promote these records into the public catalog by default.

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

1. **Parser compatibility:** gd-edit 0.2.586 is selected and packaged, but test approved fixtures with known Grim Dawn version and expected aggregate parse results before enabling uploads.
2. **Owner access and upload limits — implemented:** the single-owner authentication/CSRF boundary and bounded temporary request handling protect the preview route (PR #86).
3. **Read-only parse preview — implemented but disabled:** preview returns allowlisted parse summaries without persistence. Keep the deployment feature flag off until the fixture and production runtime gates pass.
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


## gd-edit parser source review (November 2, 2026)

The installed editor version reported in the prior PC session was **gd-edit 0.2.586**. The upstream [GrimDawn-max/gd-edit project](https://github.com/GrimDawn-max/gd-edit) identifies its license as **Eclipse Public License 1.0 (EPL-1.0)**, and its README describes this as a community fork updated for Fangs of Asterkarn. Record the license before deciding whether and how to distribute parser code or a bundled worker; this review is not a legal compatibility determination.

Source inspection found these read entry points:

- `gd-edit.io.gdc/load-character-file*` accepts either a path or byte array and validates character data versions 6, 7, or 8.
- `gd-edit.io.stash/load-stash-file` reads a stash path and distinguishes supported block types. The transfer stash uses block 18; block 19 is a different account-data structure.
- The character item layout and stash item layout gate the Fangs-era item fields on format version 11.

These entry points parse encrypted save structures into maps. They do not resolve item DBR paths to Game Lab catalog IDs; that remains a separate, versioned crosswalk operation. Their returned structures also include metadata such as source paths, so a service must construct an explicit allowlisted preview object rather than serialize or log the parser's full map.

A direct runtime smoke test on November 2, 2026 invoked the standalone gd-edit 0.2.586 JAR through `clojure.main` and called only these read functions against the user's unmodified local files. The character reader returned data-format version 8 and a non-empty inventory; the transfer-stash reader returned format version 11 and non-empty stash data. The local command printed only format versions and aggregate counts. Only aggregate format and item counts are recorded; no save files, local paths, character names, item names, or individual records were added to this repository. This confirms the invocation path and parser output shape for these particular files; it does not replace clean, reproducible fixture coverage.

This establishes source-level feasibility for an isolated JVM parser boundary, but **does not yet prove** a production-ready integration. Game Lab's API is Python/FastAPI, so the next implementation spike should invoke only the read-only parser functions through a narrowly scoped worker or sidecar and return a minimal JSON projection. Do not include gd-edit's interactive editor, save-writing commands, or Grim Dawn's full game database in that boundary. Apply upload size, time, memory, and temporary-file limits; delete temporary inputs after parsing; never log raw bytes, instance payloads, or local paths.

The user previously confirmed that gd-edit 0.2.586 could read their own 1.3.1.1 character and transfer-stash files, without modifying them. That is useful smoke-test evidence for those files, not a clean fixture-based compatibility result. The upstream repository contains parser tests and save-file fixtures, but this review did not establish their exact game versions or expected item counts; do not copy them into Game Lab until their provenance, privacy, and license are checked. The required clean 1.3.1.0 fixture tests, expected-count assertions, malformed/unsupported-file rejection, and byte-for-byte source-preservation test remain open.
