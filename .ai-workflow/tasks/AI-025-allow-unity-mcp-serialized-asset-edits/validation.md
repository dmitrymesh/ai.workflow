# Validation: AI-025

## Automated checks

- `python .ai-workflow/scripts/ai_task.py validate` — **passed** (0 errors)

## Diff check

- `git diff --name-only main...HEAD` — only skill files, AGENTS.md, and task folder in diff.
- No `.unity`, `.prefab`, `.asset`, `.meta`, package, or project settings files modified.

## Manual review

- All five target documents updated consistently with the same three-condition rule.
- `config.yaml` forbidden file patterns untouched — verified by reading the file.
- No code changes; documentation-only diff.

## Tests

not run — documentation-only change; no test suite covers skill file content.
