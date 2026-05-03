# Validation: AI-005

## Local

- `python .ai-workflow/scripts/ai_task.py install-plan --help`: **passed**
- `python .ai-workflow/scripts/ai_task.py validate`: **passed**
- `python .ai-workflow/scripts/ai_task.py board`: **passed**
- `python .ai-workflow/scripts/ai_task.py list`: **passed**
- `python .ai-workflow/scripts/ai_task.py show AI-005`: **passed**

**Dry-run smoke test (temp dir `/tmp/ai_install_test`, fully deleted before review):**

- Target pre-loaded with: `AGENTS.md`, `CLAUDE.md`, `README.md`,
  `.claude/commands/ai-execute-task.md`
- `install-plan <target>` (dry-run):
  - 25 CREATE, 3 MERGE-REQUIRED (`AGENTS.md`, `CLAUDE.md`,
    `.claude/commands/ai-execute-task.md`), 1 SKIP — **PASS**
  - Merge snippets printed for all 3 merge-required files — **PASS**
- `install-plan <target> --apply`:
  - Applied 25 files — **PASS**
  - `AGENTS.md` content unchanged (`# My Project`) — **PASS**
  - `CLAUDE.md` content unchanged — **PASS**
  - `README.md` not created (SKIP) — **PASS**
- Re-run `install-plan <target>` after apply:
  - 23 UNCHANGED, 5 MERGE-REQUIRED (commands now exist), 1 SKIP, 0 CREATE — **PASS**
- Temp directory deleted: **PASS**

- Unit/EditMode tests: not applicable
- Integration/PlayMode tests: not applicable

## Human review

- Status: pending
- Reviewer: null

## Guardrails

- Forbidden files changed: none (`.gitignore` is not in the forbidden list and
  the change is necessary to exclude the untracked local settings file)
- Package changes: none
- `git status --short` after fix: `.claude/settings.local.json` no longer
  appears as untracked — **PASS**

## Notes

Unicode box-drawing chars caused cp1252 encoding error on Windows — replaced
with plain ASCII in merge snippet output. Re-tested after fix: passed.
