# Game Lab Feature Backlog

This backlog captures feature requests as the user provides their requirements. Each entry states whether it can be advanced from a phone or needs a PC. Keep requirements and acceptance criteria tied to what the user actually asked for; clarify only when a missing detail affects implementation.

## Device labels

- **Mobile-friendly** — can be scoped, documented, reviewed, or verified from a phone without a local development environment.
- **PC-required** — needs a desktop development setup, terminal, game files, local tools, or substantial browser/QA work.
- **Mixed** — planning can happen on mobile, but implementation or verification requires a PC.

## Feature requests

### 1. Add independent Equipment and Slot filters

- **Device:** Mobile-friendly
- **Status:** Proposed
- **Problem and desired behavior:** The catalog already has a **Rarity** filter. The **Equipment** option currently lives in the **Groups** dropdown; make Equipment its own filter and add a **Slot** filter. Keep the existing Rarity filter.
- **Acceptance criteria:** Users can combine Equipment, Rarity, and Slot filters. For example, selecting **Equipment**, **Rare**, and **1H Ranged** shows only equipment matching all three selections.
- **Dependencies or notes:** Keep non-equipment groups available through the Groups filter. Map the user's wording “1h range” to the catalog's actual slot/category value during implementation.

### 2. Add creator attribution and non-affiliation notice to the site footer

- **Device:** Mobile-friendly
- **Status:** Proposed
- **Problem and desired behavior:** Add a concise signature at the bottom of the site so it is clear the project is the user's work when shared with potential employers, and clarify that the project is independent of the game's publisher.
- **Acceptance criteria:** The footer identifies the creator as **John Salo**, includes a copyright mark and automatically current year, states that the site is **not affiliated with Crate Entertainment**, and remains readable on mobile.
- **Dependencies or notes:** Suggested wording: “Built by John Salo · © [current year] · Not affiliated with Crate Entertainment.” Keep it factual and professional; no contact details are requested.

### 3. Filter equipment by item stat

- **Device:** PC-required (tentative; reassess when scoped)
- **Status:** Proposed; deferred for later
- **Problem and desired behavior:** Add a filter based on an item's stat, so a user can search for a slot or type of item and a stat together—for example, gloves with Vitality Damage—and see only applicable items.
- **Acceptance criteria:** A user can combine an item type or slot (such as **Gloves**) with a stat (such as **Vitality Damage**) and get only matching catalog items.
- **Dependencies or notes:** Build on the separate Equipment and Slot filters. Determine how stat names and values are indexed across item details before implementation; reassess whether the work truly needs a PC when planned.

### 4. Show all item damage conversions on cards

- **Device:** Mobile-friendly
- **Status:** Proposed
- **Problem and desired behavior:** Dauntless shield (`it14449`) shows only `45% Chaos to Physical` under Conversions in Game Lab, whereas the GrimTools 1.3.1.0 reference shows two variable-roll conversions: `36/54% Chaos Damage converted to Physical Damage` and `36/54% Acid Damage converted to Physical Damage`.
- **Acceptance criteria:** Both conversion types appear in the Dauntless item details with correct damage directions and source-backed min/max values; other item conversions remain correct.
- **Dependencies or notes:** Diagnose whether the missing Acid conversion originates in catalog extraction, structured card API, or frontend rendering. Do not infer a conversion from the screenshot alone; validate against the pinned source data. User supplied side-by-side mobile screenshots.

### 5. Render crafting recipes with readable ingredient names and alternatives

- **Device:** Mobile-friendly
- **Status:** Proposed
- **Problem and desired behavior:** Blueprint: Dauntless (`it14332`) currently shows raw catalog IDs for the crafted output and ingredient entries, including a long `or` chain. The GrimTools reference displays named ingredients and quantities.
- **Acceptance criteria:** Show `Dauntless` as the crafted output and readable ingredient names with quantities; group mutually exclusive alternatives clearly and retain the crafting cost. For the Dauntless example, compare against Bloodbound Guardian, Juggernaut, Fervor, and Chains of Oleron as displayed by GrimTools.
- **Dependencies or notes:** Resolve references through canonical catalog data, distinguish ingredient alternatives from simultaneous requirements, and preserve an explicit fallback for unresolved IDs. Verify exact recipe structure before changing presentation. User supplied side-by-side mobile screenshots.

### 6. Rename Retaliation Physical Min to Physical Retaliation

- **Device:** Mobile-friendly
- **Status:** Proposed
- **Problem and desired behavior:** Dauntless shield (`it14449`) shows `Retaliation Physical Min` on its item card, while the player-facing name should be `Physical Retaliation`.
- **Acceptance criteria:** Display `Physical Retaliation` with the existing `1,200/1,800` values; leave `Retaliation Physical Modifier` as a separate percentage-based stat, and do not change calculations or source values.
- **Dependencies or notes:** Apply the label through the shared item-property translation layer where appropriate. User supplied mobile screenshot.

### Request template

- **Title:**
- **Device:** Mobile-friendly / PC-required / Mixed
- **Status:** Proposed / Ready / In progress / Done
- **Problem and desired behavior:**
- **Acceptance criteria:**
- **Dependencies or notes:**

## Carry-over technical work

These are existing investigation tasks, not new feature requests.

### Finish the targeted DBR-path-to-catalog-ID crosswalk

- **Device:** PC-required
- **Status:** In progress; paused between sessions
- **Goal:** Resolve remaining flagged catalog fingerprint collisions by comparing their source DBR records. Keep the work targeted to ambiguous groups; do not export or hand-review all 8,695 catalog rows.
- **Progress:** The caster directory export covered 418 DBR records. Their source fields resolved 77 catalog entries across 15 repeated caster-weapon display names. Remaining collision groups include recipes/formulas and quest items; compare only those groups against their source DBRs.
- **Next step:** Resume with the remaining collision groups and identify the source record for each catalog ID. Preserve the catalog as-is unless a source-backed identity correction is justified.
- **Why PC:** Requires gd-edit, local Grim Dawn database files, batch exports, and catalog comparison tools.

## Intake notes

When adding a request, preserve the user's wording where practical, record assumptions separately, and mark device effort based on the work needed to complete and verify it—not merely the first planning step.
