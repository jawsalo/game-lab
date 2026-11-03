# Game Lab Session 5 Handoff — Parser Smoke Test Complete

**Checkpoint:** November 3, 2026  
**Repository:** jawsalo/game-lab, main  
**Project stage:** Phase 2 — personal character/stash snapshots  
**Status:** The local read-only parser integration and its PowerShell smoke check both passed. Stop here for tonight.

## What was completed

1. Installed Python 3.13.17 and Git 2.55.0.windows.5 on the Windows PC.
2. Cloned jawsalo/game-lab to the Desktop and updated the clean local main checkout.
3. Created a repo-local Python virtual environment at .venv; installed the declared requirements.txt dependency, PyYAML 6.0.3.
4. Confirmed the merged parser files exist: apps/api/app/snapshot_parser.py and apps/parser-worker/src/game_lab/.
5. Ran the Python SnapshotParser.parse_bytes wrapper with the installed Java runtime, gd-edit JAR, and local save files.
6. Ran the merged scripts/smoke-snapshot-parser.ps1 after pulling the latest main. The machine's default PowerShell execution policy blocked direct invocation; running it in a child process with -ExecutionPolicy Bypass worked without changing persistent execution policy.
7. Both routes returned the same result:

| Source | Save format version | Projected item instances |
|---|---:|---:|
| Character | 8 | 153 |
| Shared stash | 11 | 210 |

The local runtime was Temurin Java 25.0.5 and gd-edit standalone JAR 0.2.586. Keep the JAR, save files, and any local file paths outside Git.

## What the result means

- The worker launches on this Windows setup and reads these particular character and transfer-stash files.
- The Python adapter returns the expected minimal, allowlisted projection.
- The PowerShell smoke script is a working repeatable check and reports only source type, format version, and aggregate item count.
- The source save files were read-only; no save was written or changed.
- No character name, item name, individual inventory row, or save-file path was added to the repository.

This is a successful local parser invocation test. It does not prove compatibility with every save, establish the clean Grim Dawn 1.3.1.0 fixture gate, finish the DBR-to-catalog identity crosswalk, or authorize accepting uploads. The user's game build is 1.3.1.1; the catalog is pinned to 1.3.1.0. The earlier version review says this hotfix did not add item data, but preserve that distinction in metadata and tests.

## Merged implementation

- PR #51: read-only gd-edit worker boundary and Python SnapshotParser.
- PR #52: PowerShell smoke script scripts/smoke-snapshot-parser.ps1.
- Both are merged into main; the user's local git pull --ff-only reported “Already up to date.”

## Next session — suggested order

1. Resume the DBR-to-catalog ID crosswalk. See DBR-CATALOG-CROSSWALK.md: 77 verified caster mappings among 418 captured caster paths; 341 caster paths remain unmapped, and broader catalog coverage is incomplete.
2. Solve the export workflow before expanding coverage. We do not want to manually run about 80 batches of 100 catalog rows. Explore a single reproducible export from local database/parser tooling or choose high-value categories based on actual snapshot needs. Preserve evidence and keep unique, ambiguous, and missing matches separate. Do not map by name alone.
3. Keep the fixture gate explicit. The current user-file smoke test is evidence for those files only. Before upload implementation, use clean fixtures with confirmed game-version provenance, expected summaries, and permission to use them; do not copy upstream save binaries without that evidence.
4. Then follow SNAPSHOT-IMPORT-CONTRACT.md: parser compatibility/isolation tests, single-owner authentication, bounded temporary upload, read-only preview, current VPS capacity review, and only then PostgreSQL persistence.
5. Keep Datadog deferred until the app has a useful snapshot workload and repeatable failure scenarios.

## Resume commands

On the Windows PC, in a fresh PowerShell window:

    Set-Location "$env:USERPROFILEDesktopgame-lab"
    git pull --ff-only

Python and Git are already installed; .venv is already created. To rerun the read-only smoke check after parser changes, use:

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File .scriptssmoke-snapshot-parser.ps1 -JavaExecutable "<path to java.exe>" -GdEditJar "<path to gd-edit-standalone.jar>" -CharacterSave "<path to player.gdc>" -SharedStash "<path to transfer.gst>"

Use the user's local paths interactively; do not replace the placeholders with private paths in repository documentation. The script suppresses parser stderr and prints only an aggregate summary.

## Privacy / safety guardrails

- Never commit .gdc, .gst, .gsh, raw parser JSON, full gd-edit exports containing private inventory, or terminal transcripts.
- Keep personal inventory and character data out of the shared catalog and public endpoints.
- Parser invocation remains read-only. Do not include gd-edit's interactive editor or save-writing commands in the worker boundary.
- Treat all future uploads as untrusted; apply size, timeout, memory, authentication, and temporary-file cleanup limits before exposing endpoints.
