# Validation: AI-022

- Workflow validate: passed (`python .ai-workflow/scripts/ai_task.py validate`)
- Docs review: passed — README Basic commands section reordered; `list` now labelled as checkout-only
- `list` smoke check: passed — warning appears on stderr in branch_first mode; stdout unchanged
- `list-branches` smoke check: passed — output unchanged
- Forbidden file check: passed — no forbidden files modified
