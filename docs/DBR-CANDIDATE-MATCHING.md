# Local DBR-to-catalog candidate report

This second local step compares the item-directory DBR index with the pinned Grim Dawn 1.3.1.0 SQLite catalog. It creates a review report only; it does not update or publish the canonical crosswalk.

## Match evidence

- A DBR and catalog row must have the same category (`Class` ↔ catalog `category`).
- When present, the DBR `itemNameTag` is compared with catalog `name_tag` as an exact source-tag match.
- Shared item level, required level, rarity, and bitmap values are checked. `.tex` and `.png` bitmap extensions are normalized for comparison.
- Numeric offensive, defensive, character, conversion, and armor stats are compared when the field is present in both the DBR and the catalog's raw `record_json`. This distinguishes variants that share a name tag, category, level, rarity, and bitmap, such as elemental versions of generic weapons. Explicit zero values are compared when present on both sides; fields omitted by either source are treated as unavailable evidence, not a mismatch.
- If the source name tag cannot identify a catalog row, an exact normalized localized display name may produce a candidate only when at least one independent discriminator also matches. Display-name-only matches stay unmatched.
- Multiple candidates remain `ambiguous`. Unmatched rows are retained in the report.

Every output record retains the DBR source layer and record path. Unique here means unique under the recorded evidence in this local report; manually review samples before promoting any row to the project crosswalk.

## Run on the Windows checkout

From PowerShell in `C:\Users\15073\Desktop\game-lab`, run this one-liner:

```powershell
.\.venv\Scripts\python.exe scripts\match_grim_dawn_dbr_candidates.py --index 'C:\GD-Data-Export\item-dbr-index.jsonl' --catalog-sqlite 'C:\Users\15073\Desktop\game-lab\apps\api\data\grim-dawn\1.3.1.0\items.sqlite' --output 'C:\GD-Data-Export\dbr-catalog-candidates.jsonl'
```

The command checks that the SQLite catalog reports game version `1.3.1.0`. It prints candidate totals and counts by source layer and category. The full JSONL candidate report is written outside the repository at `C:\GD-Data-Export\dbr-catalog-candidates.jsonl`. If the file already exists, choose another output name or pass `--overwrite` after deciding it is disposable.

The report output and DBR index contain derived game data. Keep both local; do not commit them or the raw extracted DBRs, text archives, save files, or inventory data.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest scripts.tests.test_grim_dawn_dbr_candidates -v
```

Tests cover exact tag matching, stat-based disambiguation, discriminator conflicts, ambiguity retention, composite display-name fallback, rejection of name-only matches, category mismatches, and the catalog-version check.
