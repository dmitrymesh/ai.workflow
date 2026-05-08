# Validation: AI-017

## Local

- `python .ai-workflow/scripts/ai_task.py validate` → **passed**
- `python -m unittest test_show test_cascade -v` (from `scripts/`) → **11/11 passed**
  - test_show: 3 tests (status from metadata, each status value, no mutation)
  - test_cascade: 8 tests (all prior cascade scenarios)
- `show AI-016` → `status: done` ✓ (was `status: tasks`)
- `show AI-011` → `status: done` ✓ (was `status: tasks`)
- `list` → AI-017 under `in_progress`, all other tasks in correct buckets ✓
- Integration/PlayMode tests: not applicable (Python CLI project)

## Human review

- Status: pending
- Reviewer: null

## Guardrails

- Forbidden files changed: none — only `_relationships.py` and new `test_show.py`
- Package changes: none

## Notes

Fix is one line in `show_task`. All pre-existing tests continue to pass.
