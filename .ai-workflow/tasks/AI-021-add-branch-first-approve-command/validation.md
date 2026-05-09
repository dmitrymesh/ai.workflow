# Validation: AI-021

- Workflow validate: passed (`python .ai-workflow/scripts/ai_task.py validate`)
- `approve --help`: subcommand registered, output correct
- `approve AI-022 --print-only`: printed correct branch/path/commit commands
- Live `approve AI-023` (clean worktree): committed `ready` status; `show-branch` confirmed `Status: ready`
- Error case — already-ready task: `approve requires task to be draft (current: ready).`
- Error case — dirty staged index: staged a file in AI-023 worktree; `approve AI-023` failed with "has staged changes" listing the staged path and instructions
- Forbidden file check: no forbidden files modified
- Tests: not applicable (no test suite for workflow scripts)
