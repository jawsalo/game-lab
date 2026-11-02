# Grim Dawn catalog ID ↔ DBR crosswalk

**Scope:** Grim Dawn catalog 1.3.1.0; user game build 1.3.1.1 (hotfix).
**Checkpoint:** November 2, 2026. This is an evidence-backed partial crosswalk, not full catalog coverage.

## Result

- The saved gd-edit output contains **418 unique paths** under `records/items/gearweapons/caster/` (978 heading occurrences across eight overlapping output chunks).
- The saved catalog property query contains **77 IDs** across **15 generic caster weapon names**. Every one matched exactly one of the 418 DBR records when `itemNameTag`, `itemLevel`, and the full available `offensive*` property set were compared. Numeric values were normalized between integer and decimal rendering.
- The remaining **341 caster DBR paths are not mapped by this checkpoint**. Other item categories are also not exhaustively mapped. Do not infer that the crosswalk is complete.
- The 24 coarse-fingerprint collision groups found in the 8,695-record catalog scan are not evidence of database poisoning. The groups include real stat variants, multiple recipes, and quest items with shared display names/icons. A coarse fingerprint is not a unique identity key.

## Caster generic-name mappings (77)

Each row is unique within the 418-path caster directory on the evidence described above.

| Catalog ID | Catalog name | Item level | DBR path |
|---|---|---:|---|
| `it2019` | Arcane Dagger | 26 | `records/items/gearweapons/caster/a04_dagger001.dbr` |
| `it2020` | Arcane Dagger | 26 | `records/items/gearweapons/caster/a04_dagger002.dbr` |
| `it2021` | Arcane Dagger | 26 | `records/items/gearweapons/caster/a04_dagger003.dbr` |
| `it2022` | Arcane Wand | 26 | `records/items/gearweapons/caster/a04_scepter001.dbr` |
| `it2023` | Arcane Wand | 26 | `records/items/gearweapons/caster/a04_scepter002.dbr` |
| `it2024` | Arcane Wand | 26 | `records/items/gearweapons/caster/a04_scepter003.dbr` |
| `it2025` | Arcane Wand | 26 | `records/items/gearweapons/caster/a04_scepter004.dbr` |
| `it2054` | Exalted Dagger | 72 | `records/items/gearweapons/caster/a09_dagger001.dbr` |
| `it2055` | Exalted Dagger | 72 | `records/items/gearweapons/caster/a09_dagger002.dbr` |
| `it2056` | Exalted Dagger | 72 | `records/items/gearweapons/caster/a09_dagger003.dbr` |
| `it2057` | Exalted Scepter | 72 | `records/items/gearweapons/caster/a09_scepter001.dbr` |
| `it2058` | Exalted Scepter | 72 | `records/items/gearweapons/caster/a09_scepter002.dbr` |
| `it2059` | Exalted Scepter | 72 | `records/items/gearweapons/caster/a09_scepter003.dbr` |
| `it2060` | Exalted Scepter | 72 | `records/items/gearweapons/caster/a09_scepter004.dbr` |
| `it8451` | Preserver Dagger | 84 | `records/items/gearweapons/caster/a10_dagger001.dbr` |
| `it8452` | Preserver Dagger | 84 | `records/items/gearweapons/caster/a10_dagger002.dbr` |
| `it8453` | Preserver Dagger | 84 | `records/items/gearweapons/caster/a10_dagger003.dbr` |
| `it8454` | Preserver Scepter | 84 | `records/items/gearweapons/caster/a10_scepter001.dbr` |
| `it8455` | Preserver Scepter | 84 | `records/items/gearweapons/caster/a10_scepter002.dbr` |
| `it8456` | Preserver Scepter | 84 | `records/items/gearweapons/caster/a10_scepter003.dbr` |
| `it8457` | Preserver Scepter | 84 | `records/items/gearweapons/caster/a10_scepter004.dbr` |
| `it8458` | Redeemer Dagger | 94 | `records/items/gearweapons/caster/a11_dagger001.dbr` |
| `it8459` | Redeemer Dagger | 94 | `records/items/gearweapons/caster/a11_dagger002.dbr` |
| `it8460` | Redeemer Dagger | 94 | `records/items/gearweapons/caster/a11_dagger003.dbr` |
| `it8461` | Redeemer Scepter | 94 | `records/items/gearweapons/caster/a11_scepter001.dbr` |
| `it8462` | Redeemer Scepter | 94 | `records/items/gearweapons/caster/a11_scepter002.dbr` |
| `it8463` | Redeemer Scepter | 94 | `records/items/gearweapons/caster/a11_scepter003.dbr` |
| `it8464` | Redeemer Scepter | 94 | `records/items/gearweapons/caster/a11_scepter004.dbr` |
| `it2047` | Ritual Blade | 60 | `records/items/gearweapons/caster/a08_dagger001.dbr` |
| `it2048` | Ritual Blade | 60 | `records/items/gearweapons/caster/a08_dagger002.dbr` |
| `it2049` | Ritual Blade | 60 | `records/items/gearweapons/caster/a08_dagger003.dbr` |
| `it2050` | Ritual Blade | 60 | `records/items/gearweapons/caster/a08_dagger004.dbr` |
| `it2051` | Ritual Blade | 60 | `records/items/gearweapons/caster/a08_dagger005.dbr` |
| `it2052` | Ritual Blade | 60 | `records/items/gearweapons/caster/a08_dagger006.dbr` |
| `it2053` | Ritual Blade | 60 | `records/items/gearweapons/caster/a08_dagger007.dbr` |
| `it2040` | Ritual Scepter | 50 | `records/items/gearweapons/caster/a07_scepter001.dbr` |
| `it2041` | Ritual Scepter | 50 | `records/items/gearweapons/caster/a07_scepter002.dbr` |
| `it2042` | Ritual Scepter | 50 | `records/items/gearweapons/caster/a07_scepter003.dbr` |
| `it2043` | Ritual Scepter | 50 | `records/items/gearweapons/caster/a07_scepter004.dbr` |
| `it2044` | Ritual Scepter | 50 | `records/items/gearweapons/caster/a07_scepter005.dbr` |
| `it2045` | Ritual Scepter | 50 | `records/items/gearweapons/caster/a07_scepter006.dbr` |
| `it2046` | Ritual Scepter | 50 | `records/items/gearweapons/caster/a07_scepter007.dbr` |
| `it2033` | Ritual Wand | 40 | `records/items/gearweapons/caster/a06_scepter001.dbr` |
| `it2034` | Ritual Wand | 40 | `records/items/gearweapons/caster/a06_scepter002.dbr` |
| `it2035` | Ritual Wand | 40 | `records/items/gearweapons/caster/a06_scepter003.dbr` |
| `it2036` | Ritual Wand | 40 | `records/items/gearweapons/caster/a06_scepter004.dbr` |
| `it2037` | Ritual Wand | 40 | `records/items/gearweapons/caster/a06_scepter005.dbr` |
| `it2038` | Ritual Wand | 40 | `records/items/gearweapons/caster/a06_scepter006.dbr` |
| `it2039` | Ritual Wand | 40 | `records/items/gearweapons/caster/a06_scepter007.dbr` |
| `it1998` | Sacrificial Knife | 12 | `records/items/gearweapons/caster/a01_dagger001.dbr` |
| `it1999` | Sacrificial Knife | 12 | `records/items/gearweapons/caster/a01_dagger002.dbr` |
| `it2000` | Sacrificial Knife | 12 | `records/items/gearweapons/caster/a01_dagger003.dbr` |
| `it2001` | Sacrificial Knife | 12 | `records/items/gearweapons/caster/a01_dagger004.dbr` |
| `it2002` | Sacrificial Knife | 12 | `records/items/gearweapons/caster/a01_dagger005.dbr` |
| `it2003` | Sacrificial Knife | 12 | `records/items/gearweapons/caster/a01_dagger006.dbr` |
| `it2004` | Sacrificial Knife | 12 | `records/items/gearweapons/caster/a01_dagger007.dbr` |
| `it2012` | Scepter | 21 | `records/items/gearweapons/caster/a03_scepter001.dbr` |
| `it2013` | Scepter | 21 | `records/items/gearweapons/caster/a03_scepter002.dbr` |
| `it2014` | Scepter | 21 | `records/items/gearweapons/caster/a03_scepter003.dbr` |
| `it2015` | Scepter | 21 | `records/items/gearweapons/caster/a03_scepter004.dbr` |
| `it2016` | Scepter | 21 | `records/items/gearweapons/caster/a03_scepter005.dbr` |
| `it2017` | Scepter | 21 | `records/items/gearweapons/caster/a03_scepter006.dbr` |
| `it2018` | Scepter | 21 | `records/items/gearweapons/caster/a03_scepter007.dbr` |
| `it2026` | Spellblade | 31 | `records/items/gearweapons/caster/a05_dagger001.dbr` |
| `it2027` | Spellblade | 31 | `records/items/gearweapons/caster/a05_dagger002.dbr` |
| `it2028` | Spellblade | 31 | `records/items/gearweapons/caster/a05_dagger003.dbr` |
| `it2029` | Spellblade | 31 | `records/items/gearweapons/caster/a05_dagger004.dbr` |
| `it2030` | Spellblade | 31 | `records/items/gearweapons/caster/a05_dagger005.dbr` |
| `it2031` | Spellblade | 31 | `records/items/gearweapons/caster/a05_dagger006.dbr` |
| `it2032` | Spellblade | 31 | `records/items/gearweapons/caster/a05_dagger007.dbr` |
| `it2005` | Wand | 19 | `records/items/gearweapons/caster/a02_scepter001.dbr` |
| `it2006` | Wand | 19 | `records/items/gearweapons/caster/a02_scepter002.dbr` |
| `it2007` | Wand | 19 | `records/items/gearweapons/caster/a02_scepter003.dbr` |
| `it2008` | Wand | 19 | `records/items/gearweapons/caster/a02_scepter004.dbr` |
| `it2009` | Wand | 19 | `records/items/gearweapons/caster/a02_scepter005.dbr` |
| `it2010` | Wand | 19 | `records/items/gearweapons/caster/a02_scepter006.dbr` |
| `it2011` | Wand | 19 | `records/items/gearweapons/caster/a02_scepter007.dbr` |

## Additional verified mappings and collision findings

These examples resolve several of the flagged non-caster collisions. They are targeted mappings, not a complete crosswalk for every game item.

| Catalog ID | Display name / role | DBR path | Evidence note |
|---|---|---|---|
| `it14668` | Apoclypton’s Gaze | `records/items/gearhead/d309_head.dbr` | Positive control; name, class, item level, bitmap, and properties align. |
| `it310` | Bloodfang Oil | `records/items/crafting/consumables/oil_bleed01.dbr` | Positive control; consumable distinguished from similarly named recipe. |
| `it7393` | Aetherial Missive formula (10,000 iron) | `records/items/crafting/blueprints/other/craft_material_aetherialmissive.dbr` | Reagent: Aetherial Mutagen ×1. |
| `it11293` | Aetherial Missive formula (35,000 iron) | `records/items/crafting/blueprints/other/craft_material_aetherialmissive_02.dbr` | Polished Emerald ×1 + Tainted Brain Matter ×6. |
| `it7463` | Aetherial Missive item | `records/items/crafting/materials/craft_aetherialmissive.dbr` | Crafted item; distinct from its formula records. |
| `it7394` | Aetherial Mutagen formula (10,000 iron) | `records/items/crafting/blueprints/other/craft_material_aetherialmutagen.dbr` | Reagent: Wendigo Spirit ×1. |
| `it11294` | Aetherial Mutagen formula (35,000 iron) | `records/items/crafting/blueprints/other/craft_material_aetherialmutagen_02.dbr` | Polished Emerald ×1 + Tainted Brain Matter ×6. |
| `it7464` | Aetherial Mutagen item | `records/items/crafting/materials/craft_aetherialmutagen.dbr` | Crafted item; distinct from its formula records. |
| `it7395` | Wendigo Spirit formula (10,000 iron) | `records/items/crafting/blueprints/other/craft_material_wendigospirit.dbr` | Reagent: Aetherial Missive ×1. |
| `it11295` | Wendigo Spirit formula (35,000 iron) | `records/items/crafting/blueprints/other/craft_material_wendigospirit_02.dbr` | Polished Emerald ×1 + Ancient Heart ×6. |
| `it15883` | Beronath’s Celestial Horn formula | `records/items/crafting/blueprints/weapon/craft_weapond303.dbr` | Produces `it15959`; Permafrost ingredient. |
| `it15884` | Beronath’s Celestial Horn formula | `records/items/crafting/blueprints/weapon/craft_weapond304.dbr` | Produces `it15960`; Desolation ingredient. |
| `it15885` | Beronath’s Celestial Horn formula | `records/items/crafting/blueprints/weapon/craft_weapond305.dbr` | Produces `it15961`; Conflagration ingredient. |
| `it15377` | Formula: Bolstered Flask | `records/items/crafting/blueprints/potions/potions_container_a301.dbr` | Real gdx3 formula record; skill level 2. |
| `it15380` | Formula: Bolstered Tincture | `records/items/crafting/blueprints/potions/potions_container_b301.dbr` | Real gdx3 formula record; skill level 2. |
| `it15383` | Formula: Bolstered Vial | `records/items/crafting/blueprints/potions/potions_container_c301.dbr` | Real gdx3 formula record; skill level 2. |
| `it15478` | Legendary Ranged Weapon formula for Dagallon’s Destroyer | `records/items/crafting/blueprints/weapon/craft_weapondagallond110.dbr` | Produces `it15485`; Arcane Lens + Dagallon’s Destroyer recipe variant. |
| `it15479` | Legendary Ranged Weapon formula for Dagallon’s Annihilator | `records/items/crafting/blueprints/weapon/craft_weapondagallond111.dbr` | Produces `it15486`; Arcane Lens + Dagallon’s Annihilator recipe variant. |
| `it15485` | Dagallon’s Destroyer (crafted output) | `records/items/gearweapons/guns1h/d110b_gun1h.dbr` | Polarized variant; item record has the matching displayed name and stats. |
| `it15486` | Dagallon’s Annihilator (crafted output) | `records/items/gearweapons/guns1h/d111b_gun1h.dbr` | Polarized variant; item record has the matching displayed name and stats. |
| `it16001` | Wayfinder Report (Agakai) | `records/items/questitems/quest_areah_kurnscoutreport_01.dbr` | Dropped by matching Wayfinder corpse 01. |
| `it16002` | Wayfinder Report (Purska) | `records/items/questitems/quest_areah_kurnscoutreport_02.dbr` | Dropped by matching Wayfinder corpse 02. |
| `it16003` | Wayfinder Report (Ulfear) | `records/items/questitems/quest_areah_kurnscoutreport_03.dbr` | Dropped by matching Wayfinder corpse 03. |

### Distinctions that must remain explicit

- The two Dagallon blueprints have distinct source DBRs and distinct outputs: `it15478` → `craft_weapondagallond110.dbr` → `it15485`; `it15479` → `craft_weapondagallond111.dbr` → `it15486`. Their short display descriptions overlap, so retain the output and reagent relationships.
- `it17148`–`it17150` are default-item representations sharing names/icons with the gdx3 Bolstered Flask/Tincture/Vial formulas (`it15377`, `it15380`, `it15383`). They have no distinct source DBR established in this investigation; do not fabricate one.
- Wayfinder Reports share a display name and icon, but each has different report text and a distinct DBR path.
- The Beronath’s Celestial Horn formulas share a display name, but produce different output variants and consume different relics. Their IDs and paths remain separate.

## Method and limits

- Catalog source: read-only SQLite `items` rows from the pinned 1.3.1.0 catalog; API `record_json` preserved the gameplay properties and stable `it...` IDs.
- DBR source: gd-edit database-record output. The item name was compared through `itemNameTag`, not a guessed filename; item level and all catalog-exported `offensive*` properties were also compared for the caster mapping.
- Caster mapping uniqueness is scoped to the captured caster directory. A match there does not prove global uniqueness across every category/mod or later game/catalog version.
- Recipe and quest mappings use the item’s complete source record, output/reagent links, and distinguishing content. Repeated names/icons alone are insufficient.
- Record the exact catalog/game build with any future generated crosswalk. If a source path has zero or multiple candidates, keep it unresolved until additional evidence distinguishes it.
- The attachments also contained private character/stash files and unrelated output. None of those files, raw exports, or inventory contents are included in this document or should be committed.

## Next mapping work

1. Keep these 77 mappings as a verified seed set and regression fixture.
2. Build mappings for the remaining 341 caster DBR paths and selected non-caster categories, using a reproducible export format that does not contain save/inventory data.
3. Report unique, ambiguous, and missing mappings separately before using the crosswalk in snapshot imports.
4. Resume parser/license/version compatibility, owner authentication, bounded upload and preview gates in [the snapshot import contract](SNAPSHOT-IMPORT-CONTRACT.md).
