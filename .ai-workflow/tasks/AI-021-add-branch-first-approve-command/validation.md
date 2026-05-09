# Validation: AI-021

- Workflow validate: passed (`python .ai-workflow/scripts/ai_task.py validate`)
- `approve --help`: subcommand registered and output is correct
- `approve AI-022 --print-only`: printed correct branch/path/commit commands
- Live `approve AI-023`: committed `ready` status to task branch; `show-branch` confirmed `Status: ready`
- Error case `approve AI-023` (already ready): failed with clear message `approve requires task to be draft (current: ready).`
- Forbidden file check: no forbidden files modified
- Tests: not applicable (no test suite for workflow scripts)
