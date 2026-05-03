# Validation: AI-007

## CLI commands

- `python .ai-workflow/scripts/ai_task.py roles` — passed (prints role/tool/skill table)
- `python .ai-workflow/scripts/ai_task.py roles --help` — passed
- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `python .ai-workflow/scripts/ai_task.py board` — passed
- `python .ai-workflow/scripts/ai_task.py list` — passed
- `python .ai-workflow/scripts/ai_task.py show AI-007` — passed

## install-plan snippet check

- `python .ai-workflow/scripts/ai_task.py install-plan <tmp>` against target with existing AGENTS.md and CLAUDE.md — passed
  - AGENTS.md snippet includes adapter header and config.yaml role guidance
  - CLAUDE.md snippet includes adapter header, default executor role note, and config.yaml reference

## Manual checks

- Text search for hardcoded role assumptions (`Codex`, `Claude`, `codex`, `claude`): all remaining mentions are examples/defaults or adapter-specific labels — passed
- Forbidden file check: no `.env*`, no Unity files, no unrelated files changed — passed

## Human review

- Status: pending
- Reviewer: null

## Notes

No compile step required (pure documentation and stdlib Python changes).
