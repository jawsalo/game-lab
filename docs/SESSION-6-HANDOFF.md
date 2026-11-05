# Game Lab Session 6 Handoff — GDX3 Extraction Blocked

**Checkpoint:** November 5, 2026  
**Repository:** `jawsalo/game-lab`, `main`  
**Project stage:** Phase 2 — DBR-to-catalog identity crosswalk for future character/stash snapshots  
**Status:** The broad local database export succeeded for 74,052 DBRs. GDX3 extraction is not complete. Stop here and resume from the isolated extraction investigation below.

## Where this fits

The local snapshot parser smoke test is complete for the user's own files (see [Session 5 handoff](SESSION-5-HANDOFF.md)). The remaining identity work is to map parsed DBR record paths to stable catalog IDs. The current evidence-backed seed is documented in [DBR-CATALOG-CROSSWALK.md](DBR-CATALOG-CROSSWALK.md): 77 unique generic caster mappings among 418 captured paths, plus targeted recipe, quest, and positive-control mappings. It is not full catalog coverage.

## Successful local export

The user ran Asset Manager extraction to a local output folder outside the game installation. DBR counts reported:

| Layer/folder | DBRs |
|---|---:|
| Base database | 34,180 |
| GDX1 | 18,455 |
| GDX2 | 16,453 |
| survivalmode | 3,148 |
| survivalmode1 | 1,005 |
| survivalmode2 | 811 |
| **Total extracted** | **74,052** |

The sum reconciles exactly. The top-level output was `database` and `mods`; base was under `database`, with expansion/survival layers under `mods`. Preserve this export. There is no reason to repeat it.

## GDX3 investigation

- The installed archive exists at `<Grim Dawn install>\gdx3\database\GDX3.arz` and is 48,508,393 bytes.
- No GDX3 folder/count appeared in the Asset Manager export.
- ArchiveTool was run against that archive with a new destination outside the game install. It listed entries through **24,775/24,775**, then printed `Operation completed in 00:18`; PowerShell reported `Exit=0`.
- Despite that progress, the requested destination was never created, and the DBR count there was 0. A recursive search for the final listed record, `prodromus_chaosblastn.dbr`, across the export tree, user profile, and Grim Dawn install returned no result.
- The previous top-level `gdx3-direct-1` folder contains a child folder named `3`, but contains 0 DBRs. Do not assume that folder is a valid extraction.
- The command and output locations were checked against PowerShell history; the target path in the command was the intended one. The exact reason the CLI completed without writing files is still unknown.
- Crate's forum has a report of Asset Manager failing to extract GDX3 ([forum report](https://forums.crateentertainment.com/t/v1-3-0-0-foa-assetmanager-not-extracting-gdx3/156037)). This is evidence of a reported issue, not proof of a universal failure or a confirmed fix.

## Resume plan

1. Keep the 74,052-file export untouched. Never point extraction output at the live Grim Dawn install or overwrite an existing export.
2. Next try the community ArchiveTool GUI helper referenced in this [Crate forum troubleshooting thread](https://forums.crateentertainment.com/t/cant-get-archivetool-exe-to-work/160297). It is a community utility, not a Crate-made tool. Review its source/archive and path fields before extracting.
3. Extract only `GDX3.arz` into a fresh isolated output folder, such as `C:\GD-Data-Export\GDX3-GUI`.
4. Verify actual files were written: count `.dbr` files recursively, inspect at least one known GDX3 item record such as `records/items/gearhead/d309_head.dbr`, and compare the observed count with the archive's listed 24,775 entries. Do not treat a progress count or exit code alone as extraction success.
5. If the GUI also produces no files, stop and investigate the tool/version or use a verified extraction method before expanding crosswalk coverage. Do not fall back to many manual gd-edit pages.
6. Once GDX3 is present, decide whether to generate mappings from local DBR/catalog data or prioritize item categories represented in actual snapshots. Keep unique, ambiguous, and missing matches separately reported; never map on display name alone.

## Data handling

The DBR export is local source material. Do not commit raw game DBRs, extracted localization archives, personal save files, gd-edit transcripts, or individual inventory data to Git. Commit only project-authored scripts, reviewed derived mapping results, provenance, and tests as appropriate. The user's game build is 1.3.1.1; the catalog is pinned to 1.3.1.0. Keep those version labels distinct.

## Related documents

- [DBR-to-catalog crosswalk](DBR-CATALOG-CROSSWALK.md)
- [Snapshot import contract](SNAPSHOT-IMPORT-CONTRACT.md)
- [Session 5 parser handoff](SESSION-5-HANDOFF.md)
- [Roadmap v9](ROADMAP-V9.md)
