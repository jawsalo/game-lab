# Local Grim Dawn DBR index

This tool creates a local JSONL index from the user's extracted Grim Dawn database. It reads the extracted `.dbr` files and English localization text, but never modifies them. Keep the index output and all source exports outside the Git checkout; the index contains derived copies of item-record fields and is not intended for commit.

## Inputs

- Combined DBR tree: `C:\GD-Data-Export\AssetManager-Work`
- Base English text: `C:\GD-Data-Export\Text-EN-base-test\text_en`
- Expansion text: `C:\GD-Data-Export\Text-EN-expansions\<layer>\text_en`
- Local Python environment: `C:\Users\15073\Desktop\game-lab\.venv`

The combined tree is expected to have `database\records` for Base and `mods\<layer>\database\records` for each installed layer. Each JSONL record has a normalized source layer and DBR-relative path, the parsed field/value pairs, and localization results for `FileDescription`, `itemNameTag`, `description`, and `itemText`. Repeated DBR fields are preserved. Localization keys are loaded per layer; expansion layers fall back to earlier game layers. Conflicting translations are marked ambiguous and missing tag keys remain unresolved. Literal English values are retained as literals.

## Run on the Windows checkout

From PowerShell:

```powershell
cd C:\Users\15073\Desktop\game-lab
```

Run the following as one PowerShell line. The output is under `C:\GD-Data-Export`, outside the checkout, and will fail safely if it already exists:

```powershell
.\.venv\Scripts\python.exe scripts\index_grim_dawn_dbrs.py --database-root 'C:\GD-Data-Export\AssetManager-Work' --text-layer 'base=C:\GD-Data-Export\Text-EN-base-test\text_en' --text-layer 'gdx1=C:\GD-Data-Export\Text-EN-expansions\gdx1\text_en' --text-layer 'gdx2=C:\GD-Data-Export\Text-EN-expansions\gdx2\text_en' --text-layer 'gdx3=C:\GD-Data-Export\Text-EN-expansions\gdx3\text_en' --text-layer 'survivalmode1=C:\GD-Data-Export\Text-EN-expansions\survivalmode1\text_en' --text-layer 'survivalmode2=C:\GD-Data-Export\Text-EN-expansions\survivalmode2\text_en' --output 'C:\GD-Data-Export\item-dbr-index.jsonl'
```

The summary reports DBR totals by layer, item-directory record totals by layer, localization entry totals, unresolved/ambiguous/literal localization counts, and common DBR classes. The corpus scan should count 98,827 DBRs. The index includes only DBRs under `records/items/`; it retains item, formula, component, quest, and other item-directory records for later classification against the pinned catalog.

If the output already exists, choose a new filename or explicitly pass `--overwrite` after deciding the old generated index is disposable. The source DBR and text exports are read-only inputs.

## Validation

The repo test suite includes focused synthetic tests for ArchiveTool CSV rows, duplicate fields, localization precedence and conflicts, and Windows-1252 text decoding:

```powershell
.\.venv\Scripts\python.exe -m unittest scripts.tests.test_grim_dawn_dbr_index -v
```

This index is a source inventory, **not** a completed DBR-to-catalog crosswalk. The next step is to compare the local index with catalog records and report unique, ambiguous, and unmatched candidates separately.
