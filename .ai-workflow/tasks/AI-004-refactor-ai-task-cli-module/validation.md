# Validation: AI-004

## Local

- `python .ai-workflow/scripts/ai_task.py validate`: **passed**
- `python .ai-workflow/scripts/ai_task.py board`: **passed**
- `python .ai-workflow/scripts/ai_task.py list`: **passed**
- `python .ai-workflow/scripts/ai_task.py show AI-004`: **passed**
- `python .ai-workflow/scripts/ai_task.py path AI-004`: **passed**
- `python .ai-workflow/scripts/ai_task.py prepare-worktree --help`: **passed**

**Smoke tests (temp tasks AI-005, AI-006 — fully deleted before review):**

- `create` (AI-005, AI-006): **passed**
- `link AI-005 related AI-006` (bidirectional): **passed**, validate confirmed reciprocity
- `link AI-005 parent AI-006`: **passed**, validate confirmed reciprocity
- `link AI-005 blocked-by AI-006`: **passed**, validate confirmed reciprocity
- `unlink AI-005 parent`: **passed**
- `unlink AI-005 blocked-by AI-006`: **passed**
- `move AI-005 ready --force` → `move AI-005 rejected`: **passed**
- `move AI-006 rejected --force`: **passed**
- Temp task folders deleted from `rejected/`: **confirmed**
- `validate` after cleanup: **passed**

- Unit/EditMode tests: not applicable (no test framework)
- Integration/PlayMode tests: not applicable

## Human review

- Status: pending
- Reviewer: null

## Guardrails

- Forbidden files changed: none — only `.ai-workflow/scripts/` files modified
- Package changes: none
- No external dependencies added

## Notes

All commands tested end-to-end after refactor. Relationship validation
(reciprocity for parent/children, blocks/blocked_by) confirmed working via
`validate` after each link operation.
