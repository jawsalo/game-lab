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
