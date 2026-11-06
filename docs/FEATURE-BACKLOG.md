# Game Lab Feature Backlog

This backlog captures feature requests as the user provides their requirements. Each entry states whether it can be advanced from a phone or needs a PC. Keep requirements and acceptance criteria tied to what the user actually asked for; clarify only when a missing detail affects implementation.

## Implementation policy: fix families, not screenshots

When a screenshot or single item exposes a naming, unit, formatting, or data-display problem, treat it as a **symptom of a potentially broader property family** rather than patching only that one item.

1. **Trace the source and semantics.** Identify the source field(s), catalog/API keys, frontend transformation, and actual player-facing meaning before changing labels or units. Distinguish flat values, percentages, ranges, durations, chances, and skill-specific effects.
2. **Inventory the family.** Search for related keys and damage types (including damage-over-time and retaliation variants), analogous item categories, and source-supplied labels. Document which are in scope and which are deliberately excluded.
3. **Prefer shared, constrained rules.** Fix the common translation or formatting layer when appropriate. Use explicit recognized types or well-defined schemas; avoid broad string replacements that would accidentally affect specialty effects, e.g. crowd-control retaliation.
4. **Test representative siblings and exceptions.** Cover multiple damage types, both flat and percentage forms, source-label overrides, and at least one non-matching specialty property. Preserve raw values and mechanics unless a separately verified defect requires changing them.
5. **Verify beyond the reported screenshot.** Review the initial example *and* other items or properties from the same family, ideally on mobile when the task is mobile-friendly. Record unverified edge cases honestly.
6. **Keep changes reviewable.** State the family scope, exceptions, regression cases, and remaining unknowns in the PR. If a related issue is materially different, track it separately rather than silently expanding the fix.

This policy applies to all future catalog and item-card changes, not just retaliation or damage labels. A single screenshot is a reproduction case, **not** the boundary of the solution.

## Device labels

- **Mobile-friendly** — can be scoped, documented, reviewed, or verified from a phone without a local development environment.
- **PC-required** — needs a desktop development setup, terminal, game files, local tools, or substantial browser/QA work.
- **Mixed** — planning can happen on mobile, but implementation or verification requires a PC.

## Priority 1 — Verify web and API deployments are on the same release

- **Priority:** P1 — next infrastructure task, ahead of feature backlog items.
- **Device:** Mixed — GitHub workflow and smoke-test changes are mobile-friendly; inspecting running VPS images and deployment reconciliation may require terminal access.
- **Status:** Ready to investigate.
- **Problem:** Dauntless (`it14449`) returns both conversions with `minValue: 36`, `maxValue: 54` from the live API, yet regular and Incognito Chrome display 45% for each. The deployed `/app.js` appears to lack the `conversionValue` function already present on main. The existing production workflow checks the API commit and asset integrity but does not prove that web and API images originate from the same commit.
- **Acceptance criteria:** Inspect the actual running web and API image tags/digests on the VPS and compare with published images; diagnose and correct any stale web rollout; expose an unambiguous web build commit/version marker; update production verification to assert the web build matches the expected commit as well as the API version; retain existing HTML/asset hash checks; test a new deployment and ensure both Dauntless conversions render 36/54% in normal Chrome without clearing cache.
- **Notes:** Do not assume a stale image until the VPS image state is checked. Keep the fix deployment-wide, not Dauntless-specific. Do not silently alter production infrastructure without reviewing the deployment procedure.

## Feature requests

### 1. Add independent Equipment and Slot filters

- **Device:** Mobile-friendly
- **Status:** Done — merged and mobile-verified November 2, 2026
- **Problem and desired behavior:** The catalog already has a **Rarity** filter. The **Equipment** option currently lives in the **Groups** dropdown; make Equipment its own filter and add a **Slot** filter. Keep the existing Rarity filter.
- **Acceptance criteria:** Users can combine Equipment, Rarity, and Slot filters. For example, selecting **Equipment**, **Rare**, and **1H Ranged** shows only equipment matching all three selections.
- **Dependencies or notes:** Keep non-equipment groups available through the Groups filter. Map the user's wording “1h range” to the catalog's actual slot/category value during implementation.

### 2. Add creator attribution and non-affiliation notice to the site footer

- **Device:** Mobile-friendly
- **Status:** Done — merged and mobile-verified November 2, 2026
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
- **Status:** Done — merged and mobile-verified November 2, 2026
- **Problem and desired behavior:** Some item names display a literal `^k` prefix in Game Lab, including `^kSymbol of Solael` (`it2904`) and `^kTitan Plating` (`it8916`), both components in the supplied mobile screenshot. Show the clean localized names without leaking game text-control codes.
- **Acceptance criteria:** Display `Symbol of Solael` and `Titan Plating` without the `^k` prefix in search results and item details where applicable; audit other names and item groups for verified formatting tokens; preserve actual name text, search behavior, and intentional formatting; add regression tests for affected records.
- **Dependencies or notes:** Inspect the pinned catalog name fields, API display-name handling, and frontend formatting before choosing the correction layer. Do not blindly remove arbitrary caret sequences or assume only components are affected.

### 13. Add pagination controls to catalog search results

- **Device:** Mobile-friendly
- **Status:** Proposed
- **Problem and desired behavior:** Catalog search currently displays only the first 30 matching items with no visible way to reach the rest. A mobile screenshot shows `Showing 30 of 270 matching records` for Equipment-only + Head + highest-level version, but no next-page control.
- **Acceptance criteria:** Provide accessible, mobile-friendly Next and Previous controls (or equivalent) to browse all matches in stable pages; display the current range and total count; disable navigation at the beginning and end; preserve all active search terms, Equipment/Group, Slot, Rarity, and highest-level settings between pages; reset to page one when a new search or Clear occurs; avoid duplicate/skipped records.
- **Dependencies or notes:** Inspect the existing API `limit`/`offset` pagination before implementation. Test the screenshot's 270-result case as well as fewer than 30 results and an exact multiple of 30.

### 14. Restore desktop GitHub pull request merging

- **Device:** PC-required
- **Status:** Proposed; deferred by the user
- **Problem and desired behavior:** On PC, the pull request page's **Merge status** control remains unavailable instead of becoming the merge action when the PR is ready. The same PR was successfully merged from mobile. The cause is unknown; do not assume the repository rules or checks are the problem.
- **Acceptance criteria:** Reproduce this on a ready PR from the PC; identify why the desktop merge action is unavailable; restore normal PC merging without weakening required PR checks or main-branch protections; verify a ready test PR can be merged from PC.
- **Dependencies or notes:** The user reported on November 3, 2026 that PR #46 was merged via mobile while PC-based merging remained broken. Explicitly deferred; no troubleshooting or settings changes requested tonight.

### 15. Polish catalog pagination button appearance

- **Device:** Mobile-friendly
- **Status:** Proposed
- **Problem and desired behavior:** After PR #54, Previous and Next pagination controls work on mobile but look like browser-default gray buttons rather than the site's dark-themed controls. Make pagination navigation visually consistent with the rest of Game Lab without changing its working behavior.
- **Acceptance criteria:** Style Previous/Next with the existing site's colors, typography, border radius, spacing, and touch-target sizing; distinguish enabled, disabled, focused, and pressed states accessibly; ensure the page indicator and controls fit narrow mobile screens without overflow; keep both top and bottom pagination controls visually consistent; preserve pagination, result ranges, and all filters.
- **Dependencies or notes:** Screenshot from mobile verification of PR #54 showed `Previous  Page 2 of 290  Next` in default-looking gray buttons. Inspect existing CSS specificity and button styles before implementation. Do not combine with pagination logic changes.

### 16. Correct specialty retaliation labels and presentation

- **Device:** Mobile-friendly
- **Status:** Proposed
- **Problem and desired behavior:** Specialty retaliation effects such as Terrifying, Slow, and Freeze Retaliation need accurate, readable player-facing names and values. They should not be treated as ordinary flat damage retaliation or displayed with raw internal property labels.
- **Acceptance criteria:** Audit the catalog/API keys and rendered labels for terrifying/fear, slow, freeze, and other non-damage retaliation effects; show accurate effect names, durations, chances, and units where supported by source data; distinguish crowd-control retaliation from flat damage and percentage damage modifiers; add representative regression cases; preserve underlying values and mechanics.
- **Dependencies or notes:** Follow-up to global flat damage retaliation label PR #56. Inspect source fields and actual examples before deciding mappings; do not blindly apply the `retaliation<Type>Min` → `<Type> Retaliation` damage naming rule to specialty effects. Keep PR #55 as documentation-only backlog intake.

### 17. Audit damage-over-time property labels and block chance naming

- **Device:** Mobile-friendly
- **Status:** Proposed
- **Problem and desired behavior:** Mobile verification after PR #57 revealed `Offensive Slow Bleeding Modifier` on Mythical Bramblevine (`it12725`) and `Defensive Block Chance` on shields. Present these as readable `Bleeding Damage` and `Block Chance`, respectively, without overlooking other related property keys.
- **Acceptance criteria:** Inventory the full offensive damage-over-time family (Bleeding, Burn, Frostburn, Electrocute, Poison, Vitality Decay, Internal Trauma, and any source-backed variants) and standardize labels across modifier and flat/duration forms where semantically correct; distinguish damage-over-time from ordinary flat damage; normalize block-chance labeling wherever the same property occurs while keeping `Blocked Damage` as a separate flat amount; add representative regression tests for siblings and exceptions; preserve values, percentages, durations, and mechanics.
- **Dependencies or notes:** Follow the family-wide implementation policy introduced in PR #58. Verify Mythical Bramblevine (`it12725`) and additional damage types on mobile. Keep this separate from specialty retaliation backlog #16 and block recovery/source audit #8.

### 18. Display equipment set membership, pieces, and set bonuses

- **Device:** Mixed
- **Status:** Proposed
- **Problem and desired behavior:** Set items currently appear as standalone equipment with no indication of their set membership. Mythical Invoker's Shocking Touch (`it9047`) belongs to a four-piece set, but its Game Lab card does not identify the set or show related pieces and bonuses.
- **Acceptance criteria:** Audit source DBR/catalog representation of set identity, piece counts, related items, and set bonuses; display the set name and all member pieces on applicable item cards; show bonuses at their correct piece-count thresholds with readable names and values; link to catalog entries for pieces when reliably identifiable; distinguish base, empowered, mythical, and other similarly named sets without combining unrelated tiers; keep non-set items unchanged; add representative regression cases across different set sizes and item slots.
- **Dependencies or notes:** Follow the family-wide implementation policy. Source-backed set metadata may require PC access to game database files, so investigate remotely first and mark implementation PC-required if necessary. The UI should not imply which pieces a player owns or which bonuses are currently active without character/equipment data. Mobile screenshot example: `it9047`.

- **Permanent visual references (committed to this repo):** [GrimTools item-card reference folder](reference/grimtools-item-cards/). The six `gd_baseline*.PNG` files were retrieved and visually inspected through the GitHub connector on 2026-11-04. Use these for the set-member UI and bonus-threshold regression tests; do not move or rename them without updating this entry.
  - **Markovian's Bastion — five pieces, mixed slots:** [gd_baseline1.PNG](reference/grimtools-item-cards/gd_baseline1.PNG) (set list, 2–5-piece bonuses, Blitz/Overguard and granted skill), [gd_baseline2.PNG](reference/grimtools-item-cards/gd_baseline2.PNG) (shield, amulet, chest), [gd_baseline3.PNG](reference/grimtools-item-cards/gd_baseline3.PNG) (shoulders, helm). Members: Mythical Markovian's Visor (helm), Platemail (chest), Vanguard (shoulders), Bulwark (shield), Distinction (amulet). Tests mixed equipment slots, five-piece progression and skill modifiers.
  - **Invoker's Will — four pieces, accessories/off-hand:** [gd_baseline4.PNG](reference/grimtools-item-cards/gd_baseline4.PNG) (off-hand, ring, amulet), [gd_baseline5.PNG](reference/grimtools-item-cards/gd_baseline5.PNG) (Shocking Touch ring, complete piece list and 2–4-piece bonuses), [gd_baseline6.PNG](reference/grimtools-item-cards/gd_baseline6.PNG) (set bonus skill details and Invoker's Fury). Members: Mythical Invoker's Shard (amulet), Burning Hand (ring), Shocking Touch (ring), Blaze (off-hand). Tests two distinct rings, four-piece progression, granted skills and Panetti's Replicating Missile modifiers.

### 19. Invalidate cached frontend assets after deployment

- **Device:** Mobile-friendly (implementation and verification from phone via GitHub; PC optional for deeper browser debugging)
- **Status:** Proposed
- **Problem and desired behavior:** After PR #64 was merged and production deployment verification succeeded, Samsung Internet still displayed the old `Offensive Slow Bleeding Modifier` and `Defensive Block Chance` labels on Mythical Bramblevine (`it12725`). Chrome Incognito displayed the corrected labels, indicating stale browser-cached frontend assets. Users should receive the latest deployed UI without clearing site data or using Incognito.
- **Acceptance criteria:** Give `app.js` and `styles.css` release-specific URLs (for example, a build/commit-based query string or content-hashed filename) that change whenever their contents change; ensure the served HTML is revalidated so an existing browser session discovers the new asset URLs; preserve efficient caching of unchanged versioned assets; verify behavior after two successive deployments using the same regular mobile browser session; confirm a normal reload loads the latest code without manual cache clearing; document any service worker or proxy cache behavior if present.
- **Dependencies or notes:** Prefer the existing build/deploy commit metadata rather than manually updating version numbers. Inspect `apps/web/index.html`, web server cache headers, container build, and deployment path before choosing implementation. Avoid disabling all caching globally. Verify in Samsung Internet and Chrome where practical. No local Grim Dawn DBR exports required.

### 20. Prioritize shield block chance and blocked damage at top of item details

- **Device:** Mobile-friendly
- **Status:** Proposed
- **Problem and desired behavior:** Shield cards currently bury their defining block mechanics among general properties. On Dauntless (`it14449`), `Blocked Damage` and `Block Chance` appear below offensive bonuses and Defensive Ability. Display block chance and blocked damage together at the top of expanded shield details, ideally under a dedicated `Shield Stats` heading, before general properties.
- **Acceptance criteria:** Apply to all shield item cards, not just Dauntless; preserve the original chance and amount values/ranges and their units; avoid duplicate rows in the general Properties section; do not move similarly named non-shield properties; keep the ordering responsive and readable on mobile; add representative shield and non-shield regression tests.
- **Dependencies or notes:** Use Dauntless (`it14449`) and Mythical Bramblevine (`it12725`) as visual regression cases. The Dauntless GrimTools reference is [03-1000115465.jpg](reference/grimtools-item-cards/03-1000115465.jpg). Keep this presentation-only task distinct from backlog #8's deeper block recovery and source-data audit.

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
