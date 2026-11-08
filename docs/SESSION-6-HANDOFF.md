# Game Lab Session 6 Handoff — Complete Local DBR Export

**Checkpoint:** November 6, 2026  
**Repository:** `jawsalo/game-lab`, `main`  
**Project stage:** Phase 2 — DBR-to-catalog identity crosswalk for future character/stash snapshots  
**Status:** Complete local source export verified: **98,827 DBRs across all seven database layers**, including GDX3. The extraction blocker, local index, and candidate-report implementation are complete. Resume with parser fixture compatibility and preview runtime verification; see [Roadmap V9](ROADMAP-V9.md) and [Snapshot Import Contract](SNAPSHOT-IMPORT-CONTRACT.md).

## Where this fits

The read-only snapshot parser smoke test is complete for the user's own files (see [Session 5 handoff](SESSION-5-HANDOFF.md)). The remaining identity work is mapping parsed DBR paths to stable catalog IDs. The evidence-backed seed is in [DBR-CATALOG-CROSSWALK.md](DBR-CATALOG-CROSSWALK.md): 77 unique generic caster mappings among 418 captured paths, plus targeted recipe, quest, and positive-control mappings. The crosswalk is still partial.

The Grim Dawn catalog is pinned to **1.3.1.0**. The user's installed game reports **1.3.1.1**, which was identified in prior work as a hotfix without item additions. Keep the game build and catalog version separately labeled.

## Successful complete local export

The first Asset Manager export, outside the live game installation, provided 74,052 DBRs. Asset Manager omitted GDX3. The installed archive was present at:

`C:\Program Files (x86)\Steam\steamapps\common\Grim Dawn\gdx3\database\GDX3.arz`

The direct ArchiveTool CLI reported all 24,775 entries processed and exit code 0, but wrote no files to the requested destination. Do not treat that attempt as a successful extraction.

The user then extracted the GDX3 archive through the community ArchiveToolGUI utility. The GUI package was kept outside the game installation at `C:\GD-Data-Export\ArchiveToolGUI`; its INI points to the installed `ArchiveTool.exe`. GDX3 was extracted to a separate source folder and then copied into the combined Asset Manager tree.

Verified local paths:

- GDX3 standalone extraction source: `C:\GD-Data-Export\GDX3-GUI\records`
- Combined local database tree: `C:\GD-Data-Export\AssetManager-Work`
- Combined GDX3 location: `C:\GD-Data-Export\AssetManager-Work\mods\gdx3\database\records`

The standalone GDX3 source contains 24,775 `.dbr` files. The combined tree was counted by layer:

| Layer | Relative location in combined tree | DBRs |
|---|---|---:|
| Base | `database` | 34,180 |
| GDX1 | `mods\gdx1` | 18,455 |
| GDX2 | `mods\gdx2` | 16,453 |
| GDX3 | `mods\gdx3` | 24,775 |
| Survival mode | `mods\survivalmode` | 3,148 |
| Survival mode 1 | `mods\survivalmode1` | 1,005 |
| Survival mode 2 | `mods\survivalmode2` | 811 |
| **Total** |  | **98,827** |

The seven layer counts sum exactly to the recursive total. The GDX3 count matches the 24,775 records reported by ArchiveToolGUI, and actual files were verified with sample paths under `records/controllers/enemy/`. This establishes that files were written and the complete extracted DBR corpus is assembled locally.

## Index and candidate matching: complete

- `scripts/index_grim_dawn_dbrs.py` indexes item-directory records from the seven local database layers, preserving source layer, DBR path, fields, and localization evidence. Run instructions and boundaries are in [DBR-LOCAL-INDEX.md](DBR-LOCAL-INDEX.md).
- `scripts/match_grim_dawn_dbr_candidates.py` compares that index with the pinned Grim Dawn 1.3.1.0 catalog. It uses category, source tags or localized names plus independent evidence, gameplay stats, recipe references, and known discriminators. Ambiguous, rejected, and unmatched cases stay explicit. See [DBR-CANDIDATE-MATCHING.md](DBR-CANDIDATE-MATCHING.md).
- The latest generated report compared 12,070 catalog category rows to 31,205 item-directory DBRs: 10,588 unique, 1 ambiguous, and 1,481 unmatched. This report is local derived data, not the canonical database and not a claim of full source-record coverage.
- A supplied character summary resolved all 181 item instances uniquely across 146 source paths. The shared-stash summary resolved 109 of 114 instances uniquely; 5 instances across four DBR paths remain outside the current catalog matcher, though the records exist in the extracted corpus. Keep those unresolved rather than guessing.
- All raw DBR and localization exports, generated index/report files, and save/inventory data stay outside Git.

## Next work: parser fixture and packaged runtime gate

1. Obtain or create save fixtures with confirmed Grim Dawn version, expected aggregate parse results, and permission for local test use. The user's own 1.3.1.1 files remain local smoke-test evidence, not clean compatibility fixtures.
2. Verify the merged API image contains the checksum-pinned gd-edit 0.2.586 archive, preserved license notices, Java 21, and read-only worker. Keep the production preview flag off during this check.
3. Run authenticated preview acceptance checks against approved fixtures, checking character/stash mode, counts, bounded failures, temporary-file cleanup, and that no data persists.
4. Only after the fixture and runtime gates pass, decide whether to enable preview. Check live VPS capacity and design PostgreSQL persistence as a later step.

The current checkout is on the user's PC at `C:\Users\15073\Desktop\game-lab`; Python 3.13.17, a repository-local `.venv`, and Temurin Java 25.0.5 are installed. The parser smoke test already returned character format 8 / 153 items and shared stash format 11 / 210 items. The full DBR corpus is in `C:\GD-Data-Export`, not in that checkout.

## Data handling and safety

- Keep both raw exports local. Do not commit the 98,827 raw game DBRs, extracted localization archives, save files, gd-edit transcripts, or personal inventory data.
- Commit only project-authored tooling, reviewed derived mapping data, provenance, and tests where appropriate.
- Keep the known 74,052-file Asset Manager export and the standalone `GDX3-GUI` source intact. No need to repeat either extraction.
- The failed direct CLI output folders are not valid sources; they contained no DBRs. Do not overwrite or mistake them for the successful export.
- Keep the snapshot parser read-only with respect to original saves. The parser smoke test did not write to the character or stash files.
- A candidate match is not a confirmed identity. Unique, ambiguous, and missing mappings must remain distinct until supported by evidence.

## Related documents

- [DBR-to-catalog crosswalk](DBR-CATALOG-CROSSWALK.md)
- [Snapshot import contract](SNAPSHOT-IMPORT-CONTRACT.md)
- [Session 5 parser handoff](SESSION-5-HANDOFF.md)
- [Roadmap v9](ROADMAP-V9.md)
