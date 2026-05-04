# Claude Code Instructions

> **Adapter entrypoint** — This file is the Claude Code adapter for this repository.
> By default, Claude Code is assigned the **executor** role. Check `.ai-workflow/config.yaml`
> (`agents.executor.default_tool`) to confirm or change the role assignment.

This repository uses `.ai-workflow/` for AI task execution.

Before executing a task:

1. Read `.ai-workflow/skills/executor.md`.
2. Read `.ai-workflow/skills/unity-guardrails.md` if this is a Unity project.
3. Discover ready tasks: `python .ai-workflow/scripts/ai_task.py list-branches`
4. Read the target task folder.
5. Follow `task.md` exactly.

Execution rules:

- Do not redesign the task.
- Do not expand scope.
- Before editing, list the files you plan to modify.
- If you need to modify forbidden files, stop and write the reason in `report.md`.
- After implementation, write `report.md`.
- Update `validation.md` honestly.
- **Commit** implementation + report.md + validation.md to the task branch before submitting.
- Run `submit <TASK-ID>` to move to `ready_for_review`.
- **Commit** the updated `metadata.yaml` after submit so the branch state is review-ready.
- Never move a task to `done`.
