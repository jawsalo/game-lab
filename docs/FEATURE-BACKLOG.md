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

### 7. Render item-granted skill modifiers on cards

- **Device:** Mixed
- **Status:** Proposed
- **Problem and desired behavior:** The supplied Dauntless shield (`it14449`) GrimTools screenshot shows skill-specific modifiers that are not visible in the provided Game Lab card screenshots. These may be omitted from the card rather than merely mislabeled.
- **Acceptance criteria:** Verify and display source-backed modifiers under their affected skills, including Counter Strike (8% retaliation damage added to attack), Vindictive Flame (recharge reduction, retaliation damage added to attack, flat physical damage, Fire-to-Physical conversion), and Curse of Frailty (attack speed and physical resistance modifiers). Avoid duplicating ordinary skill bonuses.
- **Dependencies or notes:** First check the complete card payload and source data; screenshots do not prove the entire card lacks these sections. May require source extraction and API work. Preserve actual signed values and semantics.

### 8. Audit shield block values and recovery display

- **Device:** Mixed
- **Status:** Proposed
- **Problem and desired behavior:** GrimTools shows Dauntless blocking 930 damage with 34% block chance and 0.6-second block recovery. Game Lab shows `Defensive Block +744/+1,116%` and `Defensive Block Chance +34%`, but the provided screenshots do not show block recovery.
- **Acceptance criteria:** Verify whether `744/1,116` is a flat blocked-damage roll range rather than a percentage, render it with the correct unit and readable label, preserve 34% block chance, and show the 0.6-second recovery if available in the canonical source.
- **Dependencies or notes:** Do not equate the GrimTools 930 representative value with the range endpoints; inspect source semantics and card API before changing values. May require catalog/API fixes.

### 9. Audit player-facing item-property labels and base damage

- **Device:** Mixed
- **Status:** Proposed
- **Problem and desired behavior:** Dauntless shows `Offensive Slow Fire Modifier +100/+151%` in Game Lab where GrimTools presents `+100/+151% Burn Damage`. Game Lab also shows `Physical Damage (minimum) +190/+285`, while GrimTools separately shows `170 Physical Damage` as shield base damage.
- **Acceptance criteria:** Confirm source-property identities, replace internal labels with accurate player-facing terms (including Burn Damage when validated), and display base shield damage separately from unrelated item modifiers where appropriate. Maintain correct roll formatting and do not conflate different stats.
- **Dependencies or notes:** Use the pinned 1.3.1.0 data and Dauntless `it14449` as a regression case; inspect other items for shared translation issues. Treat the 170 versus 190/285 discrepancy as an investigation, not a confirmed numeric defect.

### 10. Add item acquisition and blueprint vendor information

- **Device:** Mixed
- **Status:** Proposed
- **Problem and desired behavior:** GrimTools shows Dauntless as crafted from Blueprint: Dauntless, and identifies Kurn faction and Atka of the Iron Clan (Kurnhold) as the blueprint vendor. The visible Game Lab card only shows `Expansion data: gdx3`.
- **Acceptance criteria:** Where verified source data exists, show crafting origin, faction/reputation requirement, and named vendor/location on the relevant item and/or blueprint cards; handle missing acquisition metadata explicitly without invented sources.
- **Dependencies or notes:** Determine whether vendor/faction acquisition data exists in the current catalog or needs a separate source-backed mapping. Screenshot reference is GrimTools 1.3.1.0; mobile-readable presentation required.

### 11. Audit and clean up stale Git branches

- **Device:** Mobile-friendly
- **Status:** Proposed
- **Problem and desired behavior:** The repository has accumulated feature and fix branches from merged pull requests. Identify branches that are no longer needed and remove them safely to keep GitHub navigation manageable.
- **Acceptance criteria:** List remote branches and associated PR/merge status; identify merged branches eligible for deletion; preserve `main`, protected branches, and all unmerged or active work; delete only confirmed-safe stale branches after review; verify the remaining branch list. Where appropriate, evaluate GitHub's automatic deletion of head branches after merge.
- **Dependencies or notes:** Start with a read-only audit. Never bulk-delete by age or name alone. Branch deletion is a separate explicitly approved action, not authorized by adding this backlog item.

### 12. Remove raw Grim Dawn formatting tokens from displayed item names

- **Device:** Mobile-friendly
- **Status:** Proposed
- **Problem and desired behavior:** Some item names display a literal `^k` prefix in Game Lab, including `^kSymbol of Solael` (`it2904`) and `^kTitan Plating` (`it8916`), both components in the supplied mobile screenshot. Show the clean localized names without leaking game text-control codes.
- **Acceptance criteria:** Display `Symbol of Solael` and `Titan Plating` without the `^k` prefix in search results and item details where applicable; audit other names and item groups for verified formatting tokens; preserve actual name text, search behavior, and intentional formatting; add regression tests for affected records.
- **Dependencies or notes:** Inspect the pinned catalog name fields, API display-name handling, and frontend formatting before choosing the correction layer. Do not blindly remove arbitrary caret sequences or assume only components are affected.

### 13. Add pagination controls to catalog search results

- **Device:** Mobile-friendly
- **Status:** Proposed
- **Problem and desired behavior:** Catalog search currently displays only the first 30 matching items with no visible way to reach the rest. A mobile screenshot shows `Showing 30 of 270 matching records` for Equipment-only + Head + highest-level version, but no next-page control.
- **Acceptance criteria:** Provide accessible, mobile-friendly Next and Previous controls (or equivalent) to browse all matches in stable pages; display the current range and total count; disable navigation at the beginning and end; preserve all active search terms, Equipment/Group, Slot, Rarity, and highest-level settings between pages; reset to page one when a new search or Clear occurs; avoid duplicate/skipped records.
- **Dependencies or notes:** Inspect the existing API `limit`/`offset` pagination before implementation. Test the screenshot's 270-result case as well as fewer than 30 results and an exact multiple of 30.

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
