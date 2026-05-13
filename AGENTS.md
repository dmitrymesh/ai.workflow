# Repository Agent Instructions

> **Adapter entrypoint** — This file is for Codex-compatible and generic agent environments.
> For other tools, use the tool-specific adapter if one exists (e.g. `CLAUDE.md` for Claude Code),
> or read `.ai-workflow/README.md` directly.

This repository uses the Portable AI Task Protocol.

Before managing, executing, or reviewing AI tasks:

1. Read `.ai-workflow/README.md` if present.
2. Read `.ai-workflow/config.yaml` — it defines which role this tool is assigned to (`agents.manager`, `agents.executor`, or `agents.reviewer`).
3. Read the role skill for your assigned role:
   - `.ai-workflow/skills/manager.md`
   - `.ai-workflow/skills/executor.md`
   - `.ai-workflow/skills/reviewer.md`
4. **Discover active tasks** — active tasks may be in task branches, not in `main`:
   ```bash
   python .ai-workflow/scripts/ai_task.py list-branches   # branch-first mode
   python .ai-workflow/scripts/ai_task.py list            # main-first / history
   ```
5. Read the target task folder. Task folders have stable paths:
   `.ai-workflow/tasks/<task-id>-<slug>/`

General rules:

- Do not move tasks from `draft` to `ready`. Only a human may approve the task contract and move it to `ready`.
- Do not mark tasks as `done` unless explicitly acting as a human validator.
- Do not expand task scope.
- Do not silently ignore acceptance criteria.
- Do not claim tests passed unless they were actually run.
- Write `not run` when validation was not executed.
- Keep diffs small.
- Prefer explicit reports over chat-only summaries.

For Unity projects:

- Do not modify `.unity`, `.prefab`, `.asset`, or `.meta` files unless `task.md`
  explicitly authorizes it, names the specific scope, and states that Unity MCP
  or Editor-backed tooling will be used. Direct hand edits to Unity serialized
  YAML remain forbidden even when the task authorizes the change.
- Do not modify packages or project settings unless the task explicitly allows it.
- Do not rename serialized fields without migration notes.
- Prefer pure C# logic and EditMode tests where possible.
