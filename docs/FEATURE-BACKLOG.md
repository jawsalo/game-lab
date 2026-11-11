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

## Resolved P1 — Web/API deployment mismatch and rollout failures

- **Priority:** P1 incident resolved; no longer blocks feature work.
- **Device:** Mixed.
- **Status:** Resolved operationally — November 10, 2026 (user confirmed the VPS pull-deploy service reports success after PR #98). Historical incident retained for traceability.
- **Original symptom:** Dauntless (`it14449`) returned both 36/54% conversions from the API, while the stale web deployment showed 45% values. Production web and API were not reliably on the same release.
- **Root causes and fixes:** PR #78 restored numeric non-root nginx UID 101 so Kubernetes could start the web pod; the user verified both deployments running `sha-6a0ae1a` with ready pods and zero restarts. PR #97 isolated VPS deployment validation in a temporary Python virtual environment, avoiding missing host-level dependencies. PR #98 corrected over-escaped asset-URL patterns that caused post-deployment smoke-test failures even after successful Helm and pod rollouts.
- **Verification:** The user previously confirmed both Dauntless conversions rendered 36/54% in normal mobile Chrome, and verified web/API image-tag parity on the VPS. After merging PR #98, the user reported `game-lab-pull-deploy.service` succeeded. This supports closing the operational P1 blocker; it does not independently establish a permanent commit-parity assertion.
- **Remaining hardening (non-blocking):** The production smoke test verifies the expected API version, versioned frontend asset URLs, HTML cache revalidation, and JS/CSS content hashes. It does **not** currently prove that the web image was built from the same commit as the API. Add a web build commit marker and assert web/API expected-commit parity in deployment verification as a separate follow-up; do not mark that original acceptance criterion complete without implementation and validation.
- **Notes:** Do not reopen this resolved incident for unrelated item-card issues. Investigate any future rollout failure on its own evidence.

## Approved feature priorities — November 10, 2026

Priorities below apply to **open numbered feature requests**, not completed items, the resolved deployment incident, or separate snapshot/backend carry-over work. P0 means highest **feature** priority, not a new production incident. Preserve each request's own status and acceptance criteria. Implement in focused PRs, investigate shared extraction/formatting layers where useful, and verify source semantics before changing values.

| Priority | Backlog items | Rationale |
| --- | --- | --- |
| **P0 — Missing gameplay information** | **#28** mastery-wide skill bonuses; **#7** item-granted modifiers to existing skills; **#26** missing granted-skill effects; **#8** shield block/recovery data | Missing mechanics can materially mislead build choices. |
| **P1 — Incorrect/incomplete stat interpretation** | **#9** property labels/base damage; **#27** damage-over-time field family; **#25** granted-skill effect formatting; **#16** specialty retaliation; **#22** crowd-control/leech resistances; **#23** movement speed; **#24** Offensive Life Modifier investigation | Displayed data needs accurate player-facing semantics and units. |
| **P2 — Catalog enhancements** | **#18** equipment sets; **#3** stat filtering; **#5** readable recipes; **#10** acquisition/vendor information | Valuable discovery and crafting features, but not prerequisites for correcting missing mechanics. |
| **P3 — Presentation and maintenance** | **#20** shield stats positioning; **#11** stale branch audit | Polish and repository hygiene. |

**Suggested first five implementation tasks (subject to source findings):** #28 → #7 → #26 → #8 → #9. Keep separate, reviewable PRs even when shared underlying code is involved. The resolved deployment incident's remaining **web/API build-commit parity assertion** is non-blocking infrastructure hardening, tracked in its incident section rather than renumbered as a feature request.

**Completed items:** #21 is complete after PR #94 merged and the user verified both Dauntless conversion labels and line wrapping in normal mobile Chrome on November 10, 2026. Other completed entries retain their existing status.

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
- **Status:** Complete — implemented and reverified by user on mobile (2026-11-10)
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
- **Status:** Complete — implemented and reverified by user on mobile (2026-11-10)
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
- **Status:** Complete — implemented and reverified by user on mobile (2026-11-10)
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
- **Status:** Done — PR #66 merged; user confirmed pagination looks and works great on mobile November 8, 2026
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
- **Status:** Implemented in PR #103; pending CI, merge, and mobile verification.
- **Problem and desired behavior:** Shield cards currently bury their defining block mechanics among general properties. On Dauntless (`it14449`), `Blocked Damage` and `Block Chance` appear below offensive bonuses and Defensive Ability. Display block chance and blocked damage together at the top of expanded shield details, ideally under a dedicated `Shield Stats` heading, before general properties.
- **Acceptance criteria:** Apply to all shield item cards, not just Dauntless; preserve the original chance and amount values/ranges and their units; avoid duplicate rows in the general Properties section; do not move similarly named non-shield properties; keep the ordering responsive and readable on mobile; add representative shield and non-shield regression tests.
- **Dependencies or notes:** Use Dauntless (`it14449`) and Mythical Bramblevine (`it12725`) as visual regression cases. The Dauntless GrimTools reference is [03-1000115465.jpg](reference/grimtools-item-cards/03-1000115465.jpg). Keep this presentation-only task distinct from backlog #8's deeper block recovery and source-data audit.

### 21. Polish damage conversion display names

- **Device:** Mobile-friendly
- **Status:** Complete — PR #94 merged; user verified both Dauntless conversion labels in normal mobile Chrome on November 10, 2026.
- **Problem and desired behavior:** Item cards previously showed abbreviated conversion labels such as `36/54% Chaos to Physical`. Use complete, player-facing damage type names, e.g. `36/54% Chaos Damage converted to Physical Damage`, consistent with the Dauntless GrimTools reference.
- **Acceptance criteria:** Render both Dauntless (`it14449`) conversions as `36/54% Chaos Damage converted to Physical Damage` and `36/54% Acid Damage converted to Physical Damage`; apply the shared formatting consistently to all item damage conversion types; preserve percentages, min/max rolls, conversion directions, and API values; ensure text wraps cleanly on narrow mobile screens; add representative conversion-format regression tests.
- **Dependencies or notes:** Presentation-only. Do not conflate item-wide conversions with skill-specific conversions tracked in #7. Dauntless's two conversions were confirmed visible with full damage-type labels and correct 36/54% ranges in normal mobile Chrome on November 10, 2026. Screenshot also confirmed mobile line wrapping.

### 22. Audit crowd-control and leech resistance property labels

- **Device:** Mobile-friendly
- **Status:** Proposed
- **Problem and desired behavior:** Mythical Bloodmist Boots (`it14640`) display `Defensive Trap +24/+36%` and `Defensive Stun +24/+36%`; Mythical Boneshatter Treads (`it9093`) display `Defensive Slow Life Leach +40/+60%` and `Defensive Total Speed +24/+36%`. These are internal-looking names rather than recognizable resistance labels. Investigate Entrapment Resistance, Stun Resistance, Life Leech Resistance, and Slow Resistance respectively, confirming actual source semantics before relabeling.
- **Acceptance criteria:** Inventory related crowd-control, speed-reduction, and leech resistance fields across the catalog; use accurate player-facing resistance labels with correct percentages; distinguish resistance from effect duration, application chance, and offensive slow/leech effects; preserve original values and rolls; test the two boot cards and representative sibling/exception records.
- **Additional mobile evidence (November 11, 2026):** User screenshots of Mythical Boneshatter Treads (`it9093`) confirm the exact rendered strings `Defensive Slow Life Leach +40/+60%` and `Defensive Total Speed Resistance +24/+36%` (the latter wraps onto two lines). Investigate source-backed player-facing `Life Leech Resistance` and `Slow Resistance`; preserve the ranges and avoid assuming the existing internal labels are accurate.
- **Dependencies or notes:** Family-wide label/semantics investigation, not two item-specific replacements. Check whether these overlap the specialty retaliation task #16 before implementing.

### 23. Audit movement speed and maximum movement speed labels

- **Device:** Mobile-friendly
- **Status:** Implemented in PR #104; pending CI, merge, and mobile verification.
- **Problem and desired behavior:** Mythical Bloodmist Boots (`it14640`) display `Character Run Speed Modifier +8/+12%`; Mythical Boneshatter Treads (`it9093`) display both `Character Run Speed Modifier +7/+9%` and `Character Run Speed Max Modifier +2/+4%`. Replace internal-looking terms with clear player-facing movement speed labels after confirming the distinction between ordinary speed bonuses and increased maximum speed.
- **Acceptance criteria:** Verify field semantics and naming across related movement-speed properties; clearly distinguish `Movement Speed` from `Maximum Movement Speed` (or source-accurate equivalent); preserve percent values, min/max rolls, and separate lines for separate effects; test both boots and other movement-speed item categories; check narrow-screen wrapping.
- **Dependencies or notes:** Do not merge distinct speed mechanics or assume `Run Speed Max` is a standard movement-speed bonus.

### 24. Investigate Offensive Life Modifier damage label

- **Device:** Mobile-friendly
- **Status:** Implemented in PR #105; pending CI, merge, and mobile verification.
- **Problem and desired behavior:** Mythical Boneshatter Treads (`it9093`) show `Offensive Life Modifier +67/+100%`, an internal-looking property name among Physical, Vitality Decay, and Internal Trauma damage bonuses. Determine whether this represents Vitality Damage or another game mechanic before choosing a player-facing label.
- **Acceptance criteria:** Trace the exact source field and meaning; inspect sibling offensive damage types and other items; display the verified label without changing numeric values or confusing damage, life leech, or health modifiers; add regression cases for the affected family and non-matching life-related fields.
- **Dependencies or notes:** May overlap existing backlog #9 (player-facing item-property labels); keep the investigation separately trackable and consolidate implementation if the same translation family is involved. User-provided GrimTools reference for Mythical Boneshatter Treads confirms `+67/+100% Vitality Damage` at the corresponding position. The frontend's existing offensive damage-family formatter now maps source `Life` to `Vitality` while leaving life leech, health, and resistances untouched.

### 25. Render granted-skill effects as readable game mechanics

- **Device:** Mixed — source/field mapping and API tests may need deeper development work; mobile screenshots and card verification are straightforward.
- **Status:** Proposed
- **Problem and desired behavior:** Mythical Boneshatter Treads (`it9093`) grant `Shattering Force (30% Chance when Hit)`. Its trigger, description, and 2.5-second recharge are readable, but the effects list exposes raw internal properties: `Offensive Life Max +155`, `Offensive Life Min +115`, `Physical Damage (minimum) +240`, `Offensive Slow Defensive Ability Duration Min +3`, `Offensive Slow Defensive Ability Min +70`, `Offensive Stun Min +1`, `Skill Target Radius +3.5`, and `Skill Ultimate Level +1`.
- **Acceptance criteria:** Trace granted-skill source fields and their actual units; compose matching minimum/maximum damage fields into one correctly labeled range (likely 115–155 Vitality Damage); render flat physical damage accurately; express Defensive Ability reduction together with its duration when supported; label stun duration and area radius in player-facing terms; determine whether `Skill Ultimate Level` is displayable gameplay information or internal metadata; retain trigger chance, recharge, and description; add regression cases across multiple granted skills, including non-matching or incomplete field pairs.
- **Dependencies or notes:** Do not infer units or mechanics solely from internal field names. Implement shared, source-verified granted-skill formatting rather than a Boneshatter-specific override. Distinct from #7, which concerns item modifiers to existing skills. Screenshot supplied November 8, 2026.

### 26. Restore missing granted-skill effects on item cards

- **Device:** Mixed — mobile reproduction and verification; source/API investigation may require deeper development work.
- **Status:** Proposed
- **Problem and desired behavior:** Mythical Fiendflesh Greaves (`it8015`) show the granted skill `Fiend's Flesh (50% Chance when Hit)` and its description (`The flesh of the fiend protects you from harm.`), but no effect/stat lines appear beneath it. Determine whether the skill effects are absent from the pinned catalog, lost during card API extraction, or omitted by frontend rendering.
- **Acceptance criteria:** Trace the granted-skill reference and effects from the pinned 1.3.1.0 source through API payload to frontend; display all verified player-facing effects for Fiend's Flesh without inventing values; distinguish genuinely effect-less skills from incomplete extraction; test additional granted defensive/buff skills and at least one offensive granted skill; preserve trigger chance, skill name, description, and other existing details; provide explicit fallback only when source effects cannot be resolved.
- **Dependencies or notes:** Separate from #25 (effects present but raw/unreadable). Coordinate shared granted-skill parsing/formatting fixes without treating this item as an isolated exception. Mobile screenshot supplied November 8, 2026.

### 27. Complete damage-over-time field-family rendering (Chillgore regression)

- **Device:** Mixed — source/API mapping and tests; mobile visual verification.
- **Status:** Proposed — regression follow-up to #17 / PR #64
- **Problem and desired behavior:** Chillgore (`it15817`) still exposes raw `Offensive Slow Bleeding Duration Min`, `Offensive Slow Bleeding Duration Modifier`, `Offensive Slow Bleeding Min`, and corresponding `Offensive Slow Cold ...` fields even though the Bleeding Damage and Frostburn Damage percentage modifier labels are already corrected. The earlier fix did not fully cover flat damage-over-time, duration, and duration-modifier siblings.
- **Acceptance criteria:** Trace and inventory the full DoT field families (Bleeding, Frostburn, Burn, Electrocute, Poison, Vitality Decay, Internal Trauma and verified variants); combine damage, duration, and duration-modifier fields into source-accurate player-facing effects where appropriate; preserve separate percentage damage modifiers and original values/rolls; handle missing or non-matching fields safely; add Chillgore and representative sibling/exception tests and mobile verification.
- **Dependencies or notes:** Explicitly cross-reference existing #17 rather than treating the prior implementation as family-complete. The same screenshot also exposes `Character Offensive Ability Modifier` (percentage OA) and split physical minimum/maximum damage fields; assess these under #9 or separately if implementation scope differs. Do not invent a final damage range from unverified field semantics.

### 28. Display mastery-wide skill bonuses on item cards

- **Device:** Mixed — pinned source/lookup and API investigation may require PC development; mobile card verification is straightforward.
- **Status:** Implemented and mobile-verified November 11, 2026 — upstream grimtools-data PR #4 and Game Lab PR #102 merged; Dauntless shows all six bonuses in production. Broader frontend/other-item regression coverage from the original acceptance criteria remains unverified.
- **Problem and desired behavior:** Dauntless shield (`it14449`) grants `+1 to All Skills in Occultist` and `+1 to All Skills in Soldier` according to the user's GrimTools reference, but neither mastery-wide bonus appears in Game Lab's Skill Bonuses section. The four individual skill bonuses are visible. Missing mastery-wide bonuses can materially misrepresent equipment benefits.
- **Acceptance criteria:** Trace mastery-wide bonuses from the pinned Grim Dawn 1.3.1.0 source through the versioned skill lookup, item-card API contract, and frontend; render both Dauntless bonuses with accurate mastery names and rank values; support all recognized masteries and other items using the same field family; preserve existing individual skill bonuses and avoid duplicates; handle absent/unknown source fields conservatively; add API/lookup and frontend regression tests for Dauntless, another mastery-bonus item, and an item with no mastery bonus; verify the deployed Dauntless card on mobile.
- **Dependencies or notes:** Do not hardcode Dauntless or invent bonuses from class associations. Inspect the pinned lookup extraction before selecting the fix layer. Distinct from #7 (modifiers to specific skills) and #26 (missing granted-skill effects). Reported November 10, 2026.

### 29. Promote base armor to the top of equipment item details

- **Device:** Mobile-friendly
- **Status:** Implemented in PR #106; pending CI, merge, and mobile verification.
- **Problem and desired behavior:** Armor is a base equipment stat, not a general bonus. Boots such as Mythical Boneshatter Treads (`it9093`), Mythical Bilethread Greaves (`it14641`), and Mythical Bloodmist Boots (`it14640`) currently bury `Armor` among damage and resistance properties. Give base armor its own `Base Stats` section above `Properties`, analogous to shield-specific block mechanics.
- **Acceptance criteria:** Apply to equipment with the `defensiveProtection` property, preserve the existing armor value and flat-number formatting, avoid duplication in general Properties, leave non-equipment records and items without armor unchanged, and retain `Shield Stats` before `Base Stats` on shields when both exist. Verify on mobile and with shield/non-shield regression tests.
- **Dependencies or notes:** Presentation-only; do not reinterpret the source armor value or conflate base armor with percentage armor modifiers. Keep shield block recovery/source audit (#8) separate.

### 30. Group item properties into six readable sections without nested disclosures

- **Device:** Mixed — frontend architecture, catalog-wide classification audit, and automated tests benefit from development/CI; mobile visual verification is essential.
- **Status:** Implemented in PR #107; pending CI, merge, mobile verification, and full catalog-key coverage audit.
- **Problem and desired behavior:** A single long Properties list makes equipment difficult to scan on mobile. Preserve the existing single Show/Hide Item Details control, but display properties under six ordered headings: **Base Stats**, **Attributes & Combat**, **Damage & Retaliation**, **Resistances & Defense**, **Utility**, and **Other Properties**. Do not add dropdowns within the expanded item card.
- **Acceptance criteria:** Use verified source-key families rather than guessing from display labels; keep shield block chance, blocked damage, and armor together in Base Stats with shield block mechanics prioritized; preserve every property value, percentage, min/max roll, and formatting; keep original order within each group except explicitly prioritized base stats; render each property exactly once; suppress empty headings; and send every unrecognized or ambiguous property to a visible Other Properties section. Retain existing Skill Bonuses, Granted Skills, skill-specific effects, and Conversions sections without regrouping them.
- **Regression coverage:** Test shield, boots, non-equipment records, all six groups, fallback for unknown and potentially misleading keys, no duplicates, no omissions, empty groups, and stable ordering. Mobile-verify long names and narrow-screen rows.
- **Follow-up audit:** Inventory actual source property keys across the pinned 1.3.1.0 catalog and report the frequency of keys landing in Other Properties before expanding the classification allowlists. Do not hide unclassified keys or classify unfamiliar keys just to make the fallback bucket smaller.
- **Dependencies or notes:** This is a presentation-only grouping pass, not a source-data or damage-semantics rewrite. Follow-on label audits (#16, #17, #22, #24) may improve readability of Other Properties. No nested accordions.

### 33. Label percentage Spirit modifiers and classify attribute modifiers

- **Device:** Mobile-friendly
- **Status:** Proposed — source-key verification and focused frontend regression tests required.
- **Problem and desired behavior:** Mythical Arcanum Sigillis currently shows `Character Intelligence Modifier +3/+5%` under **Other Properties**. Investigate the pinned source property `characterIntelligenceModifier`; if confirmed as the player-facing Spirit percentage bonus, label it **Spirit** (with percentage range retained) and group it under **Attributes & Combat**.
- **Acceptance criteria:** Verify the source key and expected label against the item and GrimTools; handle the full corresponding attribute-modifier family (Physique, Cunning, Spirit) consistently, not a one-off item replacement; preserve values and formatting; prevent duplicate rows; ensure genuinely unknown keys still appear in **Other Properties**. Add regression coverage for Mythical Arcanum Sigillis and sibling attribute modifiers, and verify on mobile.
- **Dependencies or notes:** Follow the existing six-group layout (#30). Backlog numbers #31 and #32 are reserved in the separate documentation PR #108; this entry is #33 to avoid collisions.

### 34. Correct Electrocute duration modifier label and grouping

- **Device:** Mobile-friendly
- **Status:** Proposed — verify source semantics before changing application code.
- **Regression item:** Mythical Barrelsmith's Crossfire (`it9383`), one-handed ranged pistol.
- **Problem and desired behavior:** Pistol QA screenshot shows `Offensive Slow Lightning Duration Modifier +56/+84%` under **Other Properties**. Investigate the source key and confirm whether this represents **Electrocute Duration +56/+84%** (the lightning damage-over-time duration modifier). If confirmed, use the player-facing label and classify it under **Damage & Retaliation** rather than Other Properties.
- **Acceptance criteria:** Check pinned 1.3.1.0 source fields and GrimTools display; preserve percentage values and ranges; cover sibling damage-over-time duration modifiers as a family (e.g. Burn, Frostburn, Poison, Vitality Decay, Internal Trauma, Bleeding) without assuming every source token maps identically; preserve unknown modifiers in Other Properties; add tests and verify on mobile.
- **Dependencies or notes:** This is the first pistol-QA finding tracked in the same backlog PR as #33. Do not change Granted Skills or unrelated damage properties.

### 35. Audit Bloodborer bleeding damage, duration, and pierce ratio properties

- **Device:** Mobile-friendly for presentation and regression QA; source-key investigation and automated tests required.
- **Status:** Proposed — investigate source semantics before changing any labels or values.
- **Regression item:** Bloodborer (`it11695`), legendary one-handed ranged weapon, reported during pistol QA.
- **Observed issues:** `Offensive Slow Bleeding Min +22/+33` currently appears under **Damage & Retaliation** with an internal field label; investigate its flat Bleeding Damage meaning and distinguish it from the separate `Bleeding Damage +224/+336%` modifier. **Other Properties** contains `Offensive Pierce Ratio Min +112/+168`, `Offensive Slow Bleeding Duration Min +3`, and `Offensive Slow Bleeding Duration Modifier +112/+168%`.
- **Desired behavior:** Verify the pinned 1.3.1.0 DBR keys, units, game mechanics, and GrimTools equivalents. Display source-backed player-facing labels for flat bleeding damage, bleeding duration, duration percentage modifiers, and the pierce-ratio field. Group confidently identified damage/duration properties under **Damage & Retaliation**; keep genuinely ambiguous properties visible in **Other Properties** until verified.
- **Acceptance criteria:** Preserve all values and min/max ranges, distinguish flat and percentage bleeding damage and duration units, avoid duplicate entries, add source-family regression tests (including the related Electrocute duration modifier from #34), and mobile-verify Bloodborer. Investigate the minimum/maximum physical weapon damage entries alongside #31 without assuming their labels are already correct.
- **Dependencies or notes:** Second pistol-QA finding in PR #110; no Granted Skills or unrelated item changes. Do not infer that `Offensive Pierce Ratio Min` is a percentage without confirming the source semantics.

### Request template

- **Title:**
- **Device:** Mobile-friendly / PC-required / Mixed
- **Status:** Proposed / Ready / In progress / Done
- **Problem and desired behavior:**
- **Acceptance criteria:**
- **Dependencies or notes:**

## Carry-over technical work

These are existing investigation tasks, not new feature requests.

### Investigate a standalone lookup for known non-catalog inventory items

- **Device:** PC-required
- **Status:** Backlogged; informational only, not blocking snapshot parsing or catalog matching
- **Problem and desired behavior:** The latest local snapshot check found five stash instances across four valid game DBR paths that are absent from the catalog candidate set. Treat them as known game items without catalog cards for now. Investigate whether a reusable standalone lookup is worthwhile; the four examples may be only a small part of the roughly 90k-record DBR corpus.
- **Known paths and source classes:**
  - `records/items/misc/potions/potion_attributereset.dbr` — `ItemAttributeReset`
  - `records/items/misc/difficultyunlock_ultimate.dbr` — `ItemDifficultyUnlock` (two stash instances)
  - `records/items/misc/potions/potion_devotionreset.dbr` — `ItemDevotionReset`
  - `records/items/faction/booster/boosthostile_wendigo_c01.dbr` — `ItemFactionWarrant`
- **Acceptance criteria:** Inventory-scan the exported DBR corpus to estimate how many inventory-bearing records are not represented by the public catalog; classify their likely use and localization coverage; recommend whether to keep them as unresolved-but-known metadata, build a general local lookup for private snapshots, or leave them unsupported. Do not create one-off catalog IDs/cards or expand the public catalog without a separate product decision.
- **Why PC:** Requires the local DBR exports/index, candidate report, and analysis scripts.

### Finish the targeted DBR-path-to-catalog-ID crosswalk

- **Device:** PC-required
- **Status:** In progress; paused between sessions
- **Goal:** Resolve remaining flagged catalog fingerprint collisions by comparing their source DBR records. Keep the work targeted to ambiguous groups; do not export or hand-review all 8,695 catalog rows.
- **Progress:** The caster directory export covered 418 DBR records. Their source fields resolved 77 catalog entries across 15 repeated caster-weapon display names. Remaining collision groups include recipes/formulas and quest items; compare only those groups against their source DBRs.
- **Next step:** Resume with the remaining collision groups and identify the source record for each catalog ID. Preserve the catalog as-is unless a source-backed identity correction is justified.
- **Why PC:** Requires gd-edit, local Grim Dawn database files, batch exports, and catalog comparison tools.

## Intake notes

When adding a request, preserve the user's wording where practical, record assumptions separately, and mark device effort based on the work needed to complete and verify it—not merely the first planning step.
