# Execution Report: AI-007

## Summary

Made the Portable AI Task Protocol role/tool agnostic. Key changes:
- Documented `.ai-workflow/config.yaml` as the source of truth for role assignments (added comment block)
- Added a "Protocol entrypoints" section to `.ai-workflow/README.md` distinguishing universal vs adapter-specific entrypoints, and added onboarding steps
- Updated merge snippets in `.ai-workflow/README.md` with adapter framing
- Framed `AGENTS.md` as a Codex-compatible/generic adapter entrypoint, not universal source of truth
- Framed `CLAUDE.md` as a Claude Code adapter (default: executor role)
- Added adapter notes to `.claude/commands/ai-execute-task.md` and `ai-fix-review.md`
- Updated `README.md` root: example role split now labelled as default, example prompts rewritten to use role-based language with config.yaml references, workflow steps updated
- Added `roles` CLI subcommand that reads config.yaml and prints role → default_tool → skill
- **Fix (review round 2):** Updated `_merge_snippet_agents` and `_merge_snippet_claude` in `_install.py` to match new adapter/config-driven wording — snippets now include adapter header and direct agents to config.yaml for role determination

## Changed files

- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `.claude/commands/ai-execute-task.md`
- `.claude/commands/ai-fix-review.md`
- `.ai-workflow/README.md`
- `.ai-workflow/config.yaml`
- `.ai-workflow/scripts/ai_task.py`
- `.ai-workflow/scripts/_install.py`

## Validation performed

- `python .ai-workflow/scripts/ai_task.py roles` — passed, prints role table
- `python .ai-workflow/scripts/ai_task.py roles --help` — passed
- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `python .ai-workflow/scripts/ai_task.py board` — passed
- `python .ai-workflow/scripts/ai_task.py list` — passed
- `python .ai-workflow/scripts/ai_task.py show AI-007` — passed
- `python .ai-workflow/scripts/ai_task.py install-plan <tmp>` with existing AGENTS.md and CLAUDE.md — merge snippets confirmed to include adapter header and config.yaml role guidance
- Manual text search for hardcoded role assumptions (`Codex`/`Claude`/`codex`/`claude`) — all remaining mentions are examples, defaults, or adapter-specific references
- Forbidden file check: no `.env*` or unrelated files changed

## Assumptions

- No worktree was prepared (`metadata.yaml.branch` was null — `prepare-worktree` was not run before handoff). Edited directly in the main checkout per executor.md exception clause.
- `_parse_agents_from_config` uses a simple indent-aware loop rather than extending `parse_simple_yaml`, to avoid modifying shared core infrastructure for a single command.

## Known risks

- `_parse_agents_from_config` assumes 2-space indent for role keys and 4-space for attributes. Non-standard indentation in config.yaml would silently produce an empty output. Low likelihood since the protocol controls config.yaml format.
