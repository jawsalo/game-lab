# Game Lab — Mobile Session Handoff (November 2, 2026)

## Production checkpoint
- Repo: `jawsalo/game-lab`; production: https://games.phobosandeimos.com
- User-reviewed GitHub PRs merge to protected `main`; VPS pull-deploy timer checks roughly every five minutes.
- Last screenshot-confirmed production API identifier: `efd56da`.
- This was a phone-only development and verification session; no manual VPS intervention was required.

## Completed, merged, and mobile-verified
1. **Equipment and Slot filters** — PR #39, repaired in PRs #40 and #41. Initial issues: empty Slot options and Equipment-only returning all 8,695 items including lore. Live catalog API metadata showed 6,762 equipment records and populated slots. PR #41 addressed frontend asset caching and ensured the equipment group filter is submitted, with regression tests. User verified Equipment-only + One-handed ranged + Rare + highest-level gave **19 of 19** appropriate records (Bloodsworn Repeater, Viper Hemorrhager, Viper Sandspitter); also verified Clear resets all filters and the highest-level checkbox.
2. **Creator footer** — PR #43. User verified `Built by John Salo · © 2026`, `Not affiliated with Crate Entertainment.`, and the API commit indicator on mobile. Year updates automatically; observed API identifier `50a3f98`.
3. **Remove leading Grim Dawn name formatting codes** — PR #44. Shared API display-name handling strips leading `^<letter>` tokens while retaining names and tier prefixes. Regression cases: Symbol of Solael (`it2904`) and Titan Plating (`it8916`). User screenshot verified **Symbol of Solael** clean at API `efd56da`; Titan Plating not separately screenshot-verified.

## Backlog and unfinished tasks
- PR #42 **merged** with backlog #11 safe audit/cleanup of stale Git branches, #12 `^k` display-name issue (now done), and #13 catalog search pagination.
- **#13 Pagination:** Search only displays 30 items without next/previous controls; screenshot showed 30 of 270 Head equipment results with highest-level enabled. Backend supports limit/offset. Preserve all filters and show current result range.
- **#11 Branch cleanup:** Audit branch and PR merge status read-only first. Do not delete any branches without explicit approval.
- **#6 Physical Retaliation label:** Dauntless (`it14449`) displays `Retaliation Physical Min`; change player-facing label to `Physical Retaliation`, preserving separate percent modifier. Good next mobile-friendly task.
- Other pending Dauntless work: #4 damage conversions, #5 readable blueprint ingredients, #7 skill modifiers, #8 shield block/recovery, #9 property labels/base damage, #10 acquisition/vendor details.
- #3 stat filtering deferred; targeted DBR-path-to-catalog crosswalk remains PC-required and paused. See `docs/SESSION-4-HANDOFF.md` and `docs/SNAPSHOT-IMPORT-CONTRACT.md`.

## Restart instructions
Read this file, `docs/FEATURE-BACKLOG.md`, and `docs/ROADMAP-V9.md`. Verify current `main`, open PRs, and deployment before new work. Pick one focused backlog item; inspect code, create PR, wait for CI, request user merge approval, then verify on phone after deployment. Do not merge PRs, delete branches, or modify production without explicit authorization.
