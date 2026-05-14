# Validation: AI-032

## Local

- `python .ai-workflow/scripts/ai_task.py --help`: passed — no `move AI-001 ready`; `prepare-worktree` labeled legacy
- `python .ai-workflow/scripts/ai_task.py migrate`: passed — prints "Nothing to migrate — repo is already on the flat task layout."
- `python .ai-workflow/scripts/test_cascade.py`: passed (8 tests)
- `python .ai-workflow/scripts/test_review.py`: passed (14 tests)
- `python .ai-workflow/scripts/test_migrate.py`: passed (2 tests)
- `python .ai-workflow/scripts/ai_task.py validate`: passed
- `rg -n "move AI-001 ready" .ai-workflow/scripts/ai_task.py`: passed — no matches
- `git diff --name-only main...HEAD`: passed — only in-scope files and task folder

## Human review

- Status: pending
- Reviewer: null

## Guardrails

- Forbidden files changed: none
- Package changes: none

## Notes

No Unity code changed; recompile check not applicable.
