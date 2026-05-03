# AI-007: Make agent role mapping model agnostic

## Goal

Make the Portable AI Task Protocol model/tool agnostic so projects can choose which agent/tool acts as manager, executor, and reviewer from `.ai-workflow/config.yaml`.

The protocol should be role-based first. Mentions of Codex, Claude, or other tools should be examples or adapter-specific entrypoints, not hard requirements baked into general workflow instructions.

## Context

The current config already has:

```yaml
agents:
  manager:
    default_tool: codex
    skill: .ai-workflow/skills/manager.md
  executor:
    default_tool: claude
    skill: .ai-workflow/skills/executor.md
  reviewer:
    default_tool: codex
    skill: .ai-workflow/skills/reviewer.md
```

But the surrounding documentation and command files still imply a fixed role split such as "Codex manager/reviewer" and "Claude executor". That makes the protocol less portable. A project should be able to decide that any compatible LLM/tool is manager, executor, or reviewer by editing config and using the appropriate role skill.

There is also a naming/source-of-truth issue: `AGENTS.md` is useful for Codex-compatible tools, but it should not be treated as the universal entrypoint for every possible agent. Claude has `CLAUDE.md`; other tools may have their own adapter files, or may use `.ai-workflow/README.md` directly.

## Scope

Allowed changes:

- `.ai-workflow/config.yaml`
- `.ai-workflow/README.md`
- root `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `.claude/commands/*`
- `.ai-workflow/skills/*.md`
- `.ai-workflow/scripts/*` if adding config inspection/help commands
- `.ai-workflow/templates/*` only if role metadata needs template support
- `.ai-workflow/board.md` if regenerated
- `.ai-workflow/tasks/draft/AI-007-make-agent-role-mapping-model-agnostic/*`

Forbidden changes:

- Do not remove existing role skills (`manager.md`, `executor.md`, `reviewer.md`).
- Do not remove Claude command files if they remain useful as Claude-specific adapters.
- Do not require any specific vendor/model/tool to use the protocol.
- Do not add network calls, package managers, or non-stdlib dependencies.
- Do not change status names or lifecycle transitions.
- Do not mark any task as `done`.

## Requirements

- Define `.ai-workflow/config.yaml` as the source of truth for role assignments.
- Define the universal protocol entrypoints:
  - `.ai-workflow/README.md`
  - `.ai-workflow/config.yaml`
  - `.ai-workflow/skills/<role>.md`
- Define adapter-specific entrypoints:
  - `AGENTS.md` for Codex-compatible / generic agent environments
  - `CLAUDE.md` for Claude Code
  - `.claude/commands/*` as Claude Code command conveniences
  - future project-specific adapters such as `GEMINI.md`, `CURSOR.md`, etc. may be added by projects
- Clarify the distinction between:
  - role: `manager`, `executor`, `reviewer`
  - skill: role instruction file
  - tool/model: local agent runtime such as Codex, Claude, or another compatible agent
  - adapter entrypoint/command: optional tool-specific helper such as `AGENTS.md`, `CLAUDE.md`, or `.claude/commands/*`
- Update general docs so they describe workflows in terms of roles, not fixed products.
- Update onboarding/setup wording so it does not tell every tool to start from `AGENTS.md`.
- Recommended onboarding language should be:
  - use your tool-specific adapter entrypoint if one exists
  - otherwise read `.ai-workflow/README.md`
  - then read `.ai-workflow/config.yaml`
  - then read the role skill for the assigned role
- Keep product-specific examples, but label them explicitly as examples or adapters.
- Update example prompts so they can be adapted by reading `config.yaml`.
- Update `AGENTS.md` so it is clearly an adapter entrypoint for compatible agents, not the protocol source of truth for all tools.
- Update `CLAUDE.md` so it is clearly a Claude adapter for the executor role by default, not a protocol-wide requirement.
- Update `.claude/commands/*` wording so command files do not imply that only Claude can execute tasks; they are Claude-specific conveniences for whichever role the project assigns to Claude.
- Consider adding a small read-only CLI command that prints configured role mappings, for example:
  - `python .ai-workflow/scripts/ai_task.py roles`
  - output role, default_tool, skill path
- If CLI support is added, it must read from config and remain stdlib-only.
- Preserve backwards compatibility: the default config may still map manager/reviewer to `codex` and executor to `claude`, but that must be described as a default example, not a hardcoded rule.

## Acceptance criteria

- General documentation no longer says or implies that Codex must be manager/reviewer or Claude must be executor.
- Config is documented as the place to choose role assignments.
- Universal protocol entrypoints and adapter-specific entrypoints are documented separately.
- `AGENTS.md` is framed as an adapter entrypoint, not the universal source of truth for every tool.
- Onboarding/setup docs do not tell every tool to start from `AGENTS.md`; they direct tools to their adapter if available, otherwise `.ai-workflow/README.md`.
- `AGENTS.md` instructs compatible agents to read config and the relevant role skill, without assuming a specific model/tool.
- `CLAUDE.md` is framed as a Claude-specific adapter/instruction file, not the universal executor source of truth.
- `.claude/commands/*` remain usable but are clearly adapter commands.
- If a `roles` or similar CLI command is added, it has `--help` and prints the configured role mapping.
- Existing workflow commands still work:
  - `validate`
  - `board`
  - `list`
  - `show`
- `validate` passes.
- No unrelated files are changed.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- `python .ai-workflow/scripts/ai_task.py board`
- `python .ai-workflow/scripts/ai_task.py list`
- `python .ai-workflow/scripts/ai_task.py show AI-007`
- If CLI role inspection is added, run its `--help` and the command itself.
- Manual text search for hardcoded role assumptions:
  - `Codex`
  - `Claude`
  - `claude`
  - `codex`
  Ensure remaining mentions are examples, default config values, or adapter-specific files.
- Forbidden file check: confirm no `.env*` or unrelated files were changed.

## Notes

- This task is about portability of role assignment, not implementing multi-agent orchestration.
- The default role mapping can remain unchanged; the meaning changes from "hardcoded requirement" to "default example".
- This task should remain in `draft` until human approval moves it to `ready`.
