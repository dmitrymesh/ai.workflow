# AI-005: Add safe project installation workflow

## Goal

Add a safe installation workflow for applying the Portable AI Task Protocol to an existing project without blindly overwriting project files.

The workflow must handle likely collisions with files such as `AGENTS.md`, `CLAUDE.md`, `README.md`, `.claude/commands/*`, and any future top-level helper files.

## Context

The current installation guidance says to copy these files into a target repository:

- `.ai-workflow/`
- `AGENTS.md`
- `CLAUDE.md`
- `.claude/commands/`

This is risky for real projects because those projects may already have their own `AGENTS.md`, `CLAUDE.md`, `README.md`, `.claude/`, or other automation files. A plain copy can overwrite local instructions, lose project-specific context, or create unclear merge conflicts.

The protocol should install as a self-contained system first, then integrate with existing project files through explicit, reviewable merge steps.

## Scope

Allowed changes:

- `.ai-workflow/README.md`
- root `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `.claude/commands/*`
- `.gitignore` only to ignore local Claude settings such as `.claude/settings.local.json`
- `.ai-workflow/scripts/*` if adding an installer or dry-run command
- `.ai-workflow/templates/*` only if installer support files are needed
- new installer docs or templates under `.ai-workflow/`
- `.ai-workflow/board.md` if regenerated
- `.ai-workflow/tasks/draft/AI-005-add-safe-project-installation-workflow/*`

Forbidden changes:

- Do not implement a blind recursive copy that overwrites existing files.
- Do not require GitHub, GitLab, Jira, package managers, or network access.
- Do not add non-stdlib dependencies.
- Do not remove the existing local workflow commands.
- Do not change status names or the core lifecycle.
- Do not mark any task as `done`.

## Requirements

- Define a safe install strategy. Expected direction:
  - install protocol-owned files under `.ai-workflow/` first
  - treat top-level files (`AGENTS.md`, `CLAUDE.md`, `README.md`) and `.claude/commands/*` as integration points, not blindly owned files
  - if a target file does not exist, installer may create it from a template
  - if a target file exists, installer must not overwrite it without an explicit opt-in flag
  - for existing files, provide a merge snippet or patch instructions that a human can review
- Document the ownership model:
  - `.ai-workflow/` is protocol-owned
  - root project docs/instructions remain project-owned
  - generated files such as `.ai-workflow/board.md` remain generated
- Add a dry-run installation plan. This can be documentation-only or CLI-backed, but it must list:
  - files that would be created
  - files that already exist and require merge/review
  - files that would be skipped
  - any commands/snippets needed after copy
- If CLI support is added, prefer a command such as:
  - `python .ai-workflow/scripts/ai_task.py install-plan <target-path>`
  - or a dedicated stdlib-only installer script
- Include explicit collision handling for:
  - `AGENTS.md`
  - `CLAUDE.md`
  - `README.md`
  - `.claude/`
  - existing `.ai-workflow/`
- Provide recommended merge snippets for `AGENTS.md` and `CLAUDE.md` that point to `.ai-workflow/` rather than duplicating large instructions.
- Define an upgrade path for projects that already have `.ai-workflow/` installed:
  - dry-run first
  - show changed protocol-owned files
  - preserve project task folders unless explicitly requested
  - never delete existing tasks during install/upgrade
- Ignore local Claude settings in `.gitignore` if they are created during development:
  - `.claude/settings.local.json` should not be committed as part of protocol changes
  - keep `.claude/commands/*` installable and version-controlled
- Keep the solution portable across Windows/macOS/Linux.

## Acceptance criteria

- Installation docs no longer recommend a blind copy as the only path.
- Docs clearly describe how to avoid overwriting existing `AGENTS.md`, `CLAUDE.md`, `README.md`, and `.claude/`.
- A dry-run install/upgrade plan exists, either as CLI behavior or as precise documented steps.
- Collision behavior is explicit: create, skip, merge-required, or explicit overwrite.
- Existing `.ai-workflow/tasks/` data is preserved by the documented upgrade path.
- Any CLI/script added is stdlib-only and has `--help`.
- `.claude/settings.local.json` is ignored by git or otherwise absent from the task diff.
- `.claude/commands/*` remains installable and is not accidentally ignored.
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
- If installer CLI/script is added, run its `--help`.
- If installer CLI/script is added, run a dry-run against a temporary target directory containing pre-existing `AGENTS.md`, `CLAUDE.md`, `README.md`, `.claude/`, and `.ai-workflow/`; fully clean up the temporary directory before review.
- Manual review of docs to confirm they do not instruct users to blindly overwrite existing project files.
- Forbidden file check: confirm no `.env*` or unrelated files were changed.

## Notes

- This task is about safe installation and upgrade strategy, not publishing a package.
- Prefer conservative behavior: skip/merge-required is better than overwrite.
- This task should remain in `draft` until human approval moves it to `ready`.
