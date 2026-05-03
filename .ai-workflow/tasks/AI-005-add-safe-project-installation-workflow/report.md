# Execution Report: AI-005

## Summary

Added a safe installation / upgrade workflow for the Portable AI Task Protocol.
The solution replaces the blind-copy instruction in `README.md` with an
ownership model, a `install-plan` CLI command that classifies every file before
touching it, and merge snippets for integration points.

## Changed files

- `.ai-workflow/scripts/_install.py` — new module: `install_plan`, file
  classification logic, merge snippet printers, `--apply` path
- `.ai-workflow/scripts/ai_task.py` — added `install-plan` subcommand; updated
  module layout comment
- `README.md` — replaced blind-copy installation section with safe install
  docs, ownership table, upgrade path, and collision handling summary
- `.ai-workflow/README.md` — prepended ownership model table, safe
  installation / upgrade steps, merge snippets for `AGENTS.md` and `CLAUDE.md`,
  and upgrade instructions
- `.gitignore` — added `.claude/settings.local.json` pattern; this is a
  user-local Claude Code permissions file, not project configuration, and
  should never be committed

## Collision behaviour

| File category | Action on `--apply` |
|---|---|
| `.ai-workflow/**` (excl. `tasks/`, `board.md`) | CREATE / UPDATE |
| `AGENTS.md`, `CLAUDE.md` | CREATE if absent; MERGE-REQUIRED if exists (never overwritten) |
| `.claude/commands/*` | CREATE if absent; MERGE-REQUIRED if exists (never overwritten) |
| `README.md` | SKIP always |
| `.ai-workflow/tasks/` | Never touched |
| `.ai-workflow/board.md` | Never touched |

## Validation performed

- `python .ai-workflow/scripts/ai_task.py install-plan --help` — passed
- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `python .ai-workflow/scripts/ai_task.py board` — passed
- `python .ai-workflow/scripts/ai_task.py list` — passed
- `python .ai-workflow/scripts/ai_task.py show AI-005` — passed
- **Dry-run smoke test** against `/tmp/ai_install_test` with pre-existing
  `AGENTS.md`, `CLAUDE.md`, `README.md`, `.claude/commands/ai-execute-task.md`:
  - Plan printed correctly: 25 CREATE, 3 MERGE-REQUIRED, 1 SKIP
  - `--apply` created 25 protocol files, skipped 3 merge-required
  - AGENTS.md content confirmed unchanged after apply (`# My Project`)
  - Re-run after apply: 23 UNCHANGED, 5 MERGE-REQUIRED, 1 SKIP, 0 CREATE
  - Temp directory fully deleted before review
- Forbidden file check: no `.env*`, no out-of-scope files changed

## Assumptions

- Source for `install-plan` is always `repo_root()` (the repo where ai_task.py
  lives). The command is intended to be run from a cloned protocol repo
  pointing at a target project.
- `__pycache__/` directories are excluded from the install (only .py source
  files and non-Python assets are installed).
- Merge-snippet output uses plain ASCII (not Unicode box-drawing) for Windows
  compatibility.

## Known risks

- `install-plan` does not detect `.ai-workflow/tasks/` in the target and warn
  if it is non-empty (upgrade scenario). The tasks are preserved regardless, but
  no explicit "N existing tasks preserved" message is shown. This is a minor UX
  gap, not a data-loss risk.
