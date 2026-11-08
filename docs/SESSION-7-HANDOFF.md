# Game Lab Session 7 Handoff — Snapshot Compatibility Checkpoint

**Checkpoint:** November 8, 2026  
**Repository:** `jawsalo/game-lab`, `main` (PRs #87–#91 are merged)  
**Roadmap position:** Phase 2 — snapshot parsing and inventory identity; parser packaging and local identity smoke checks are implemented, while the upload compatibility gate remains open.  
**Privacy:** No save binaries, inventory exports, names, local file paths, or item-instance payloads were committed.

## What was completed this session

### Parser runtime packaging and build checks

- **PR #87 — Package pinned gd-edit runtime with preview disabled by default.** The API image includes the pinned gd-edit 0.2.586 runtime, Java 21, the read-only worker, and upstream license notices. The Helm default for `modules.api.snapshotPreview.enabled` remains `false`.
- **PR #88 — Update snapshot parser roadmap and handoff.** It recorded the runtime and parser status and set out the restart point.
- **PR #89 — Smoke-load parser worker during API image build.** The Docker build starts Java 21 and requires the `game-lab.snapshot-worker` namespace. Validate and Build application images passed. This catches missing runtime/worker packaging during image build; it is not a known-version save compatibility test and does not exercise a live preview request.

### Local snapshot-to-catalog smoke check

- **PR #90 — Add local snapshot catalog smoke report.** The local utility invokes `SnapshotParser` against the user's local files and joins each item DBR path against the local candidate report. It reports format version, instance count, unique DBR-path count, status counts, and unresolved DBR paths only. It does not print item names or instance payloads. The candidate report and save files remain outside Git.
- Default source-layer precedence is `gdx3,gdx2,gdx1,base`; the utility also accepts `--layer-priority`. This follows the expansion override order for the normal game, but should be treated as a configurable matching assumption.
- Latest run used the user's 1.3.1.1 game saves after playing and syncing Steam Cloud. Results:

| Source | Save format | Instances | Unique DBR paths | Unique matches | Known non-catalog items |
|---|---:|---:|---:|---:|---:|
| Character | 8 | 173 | 139 | 173 | 0 |
| Shared stash | 11 | 137 | 129 | 132 | 5 |

- The five stash instances cover four valid game DBR paths. They are known inventory items without public catalog cards or assigned catalog IDs:
  - `records/items/misc/potions/potion_attributereset.dbr` — `ItemAttributeReset`
  - `records/items/misc/difficultyunlock_ultimate.dbr` — `ItemDifficultyUnlock` (two instances)
  - `records/items/misc/potions/potion_devotionreset.dbr` — `ItemDevotionReset`
  - `records/items/faction/booster/boosthostile_wendigo_c01.dbr` — `ItemFactionWarrant`
- The source records were previously located in the local DBR export. The matcher’s `missing` result means no catalog candidate row exists; it does not mean the game DBR path is invalid or the parser failed.
- **PR #91 — Document known non-catalog snapshot items.** The four records are marked known game items without cards. The backlog task is to assess a general standalone lookup against the full local DBR corpus (98,827 DBRs), not to add four one-off mappings or public catalog entries. This lookup is informational and does not block parser work.

### DBR candidate report state

The most recent report compared **12,070 catalog category rows** against **31,205 item-directory DBRs**. It found 10,588 unique, 1 ambiguous, and 1,481 unmatched catalog-row candidates. These are evidence-coverage counts; they do not mean 1,481 catalog items are broken or that all 98,827 game DBRs belong in the public catalog. The candidate report is local analysis output and was not committed.

### Upstream fixture eligibility audit

The source tests at the pinned [gd-edit v0.2.586](https://github.com/GrimDawn-max/gd-edit/tree/v0.2.586) were inspected as the first compatibility-gate task. **No reviewed fixture qualifies as a clean, known-game-version fixture for Game Lab.**

- `counterstrike.gdc` and `z20.gdc` in [item_skills_test.clj](https://github.com/GrimDawn-max/gd-edit/blob/v0.2.586/test/gd_edit/item_skills_test.clj) have expected item-skill counts of 1 and 2. The test comments say a forum contributor sent them for this regression. They are Block 8 format version 5 saves; the comments do not state the Grim Dawn release that created them or grant Game Lab fixture reuse/redistribution permission. Their expected counts cover item skills, not complete inventory summaries.
- `NamedTabs.gdc` and `NamedTabs-transfer.gst` in [stash_tabs_test.clj](https://github.com/GrimDawn-max/gd-edit/blob/v0.2.586/test/gd_edit/stash_tabs_test.clj) cover named tabs, icons/colors, and byte-for-byte round trips. They do not give expected inventory counts or the creating game release. The character fixture's Block 8 version 8 is a save-format version, not a game version.
- gd-edit is EPL-1.0 licensed. That does not, by itself, establish the provenance or license of contributed save binaries. No upstream binaries were copied into Game Lab or run as Game Lab fixtures.
- This audit is limited to the fixture tests reviewed above. It did not establish that every test resource in the upstream repository has been audited; the inspected fixtures do not satisfy the gate regardless.

## Validation evidence

- The user's Windows run of the local snapshot smoke utility successfully parsed the synced character and stash. It was read-only and printed only aggregate counts/statuses and unresolved paths.
- In the development checkout, `PATH="$PWD/.venv/bin:$PATH" make validate` passed, including 38 script tests and 49 API tests. An initial run using system Python failed because that interpreter lacked OpenTelemetry; rerunning with the repository virtualenv passed.
- `git diff --check` passed for the documentation and utility changes.
- PR #89's Validate and API image-build checks passed before merge.

## Current roadmap position

**Phase 2 remains in progress.** The local data extraction, DBR index, conservative candidate matcher, parser integration, packaged worker, and local snapshot-to-candidate smoke check are complete for the tested files. The character resolves fully; the five stash items are categorized as valid non-catalog game inventory. Snapshot persistence implementation has not started; the contract outlines the later design gate.

The upload gate is still open. The user's 1.3.1.1 files are useful private smoke evidence, and the shared item catalog is 1.3.1.0; the hotfix did not add item data. They are not an independently sourced, authorized fixture set. The upstream fixtures reviewed tonight lack confirmed game-release provenance and fixture-specific reuse permission. **Keep preview disabled.**

Open gates, in order:

1. Find an authorized fixture with confirmed game version and expected aggregate parse results, or document that no suitable fixture is available. Do not treat internal save Block 8 versions as game versions.
2. Verify the packaged parser runtime in the target environment while the preview flag remains off. The image-build worker smoke is already complete; live runtime verification is still distinct.
3. With an approved fixture, exercise the protected preview path, authentication/CSRF behavior, request/file/resource limits, temporary-file cleanup, and source-file preservation. Keep preview disabled for general use until these pass.
4. Only after the compatibility and preview gates pass, review current VPS capacity and design private PostgreSQL snapshot persistence. Keep snapshots separate from the immutable shared catalog.
5. Later, assess the standalone lookup backlog by scanning/classifying inventory-bearing DBR records absent from catalog coverage. It is not a blocker for the current parser gate.

Datadog remains deferred until the app has a useful workload and repeatable failure scenarios. Open-source observability and the mobile item-card baseline remain complete for their current checkpoints.

## Restart point

Resume at **fixture availability and provenance**, not by repeating local DBR extraction, index generation, candidate matching, parser installation, or the synced-save smoke check. The detailed contract and roadmap are [SNAPSHOT-IMPORT-CONTRACT.md](SNAPSHOT-IMPORT-CONTRACT.md) and [ROADMAP-V9.md](ROADMAP-V9.md); the deferred non-catalog lookup is in [FEATURE-BACKLOG.md](FEATURE-BACKLOG.md).
