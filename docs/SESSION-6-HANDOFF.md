# Game Lab Session 6 Handoff — Complete Local DBR Export

**Checkpoint:** November 6, 2026  
**Repository:** `jawsalo/game-lab`, `main`  
**Project stage:** Phase 2 — DBR-to-catalog identity crosswalk for future character/stash snapshots  
**Status:** Complete local source export verified: **98,827 DBRs across all seven database layers**, including GDX3. The extraction blocker is closed. Next: build and validate a reproducible local DBR index and candidate crosswalk report.

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

## Next work: first index and candidate-mapping chunk

Estimated time for the first useful chunk: **about 1–2 hours**, depending on the local export format and localization requirements. Broad catalog coverage will need additional sessions; estimate it after seeing the first report.

1. From the Windows checkout of `jawsalo/game-lab`, inspect the DBR text format, layer directory layout, and available English localization inputs. Keep the local export outside Git.
2. Implement a small deterministic local tool that scans all seven layer roots and emits an inventory/index of item-relevant DBRs. Preserve source layer and normalized DBR path. Keep raw DBR bodies and localized personal data out of the repo.
3. Compare the index with the pinned 8,695-row catalog using a composite fingerprint based on source path relationships and item fields (resolved name, class/category, rarity, item/required levels, bitmap, gameplay properties, and where relevant recipe output/reagents or quest text). Do not use display name alone.
4. Produce a review report that separates unique candidates, ambiguous matches, and unmatched records. Validate the known seed mappings (including the four canonical item-card items where applicable, the caster set, crafting/recipe examples, and quest examples) as regression checks.
5. Review the first sample/report before expanding to a full generated crosswalk. Keep source version, catalog version, counts, and hashes/provenance explicit. Do not claim full coverage until counts and unresolved cases are reported.

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
