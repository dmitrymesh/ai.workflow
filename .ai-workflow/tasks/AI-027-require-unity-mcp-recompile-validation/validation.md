# Validation: AI-027

## Automated checks

- `python .ai-workflow/scripts/ai_task.py validate` — **passed** (0 errors)

## Diff check

- `git diff --name-only main...HEAD` — only skill files, profile README, and
  task folder in diff. No `.unity`, `.prefab`, `.asset`, `.meta`, package, or
  project settings files modified.

## Manual review

- All five target documents updated consistently.
- `config.yaml`, `AGENTS.md`, `CLAUDE.md`, and `templates/task.md` untouched.
- Documentation-only change.

## Unity recompilation

not run — this task modifies only workflow documentation; no Unity code was changed.

## Tests

not run — documentation-only change; no test suite covers skill file content.
