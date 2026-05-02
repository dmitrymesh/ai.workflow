# Claude Code Instructions

This repository uses `.ai-workflow/` for AI task execution.

Before executing a task:

1. Read `.ai-workflow/skills/executor.md`.
2. Read `.ai-workflow/skills/unity-guardrails.md` if this is a Unity project.
3. Read the target task folder.
4. Follow `task.md` exactly.

Execution rules:

- Do not redesign the task.
- Do not expand scope.
- Before editing, list the files you plan to modify.
- If you need to modify forbidden files, stop and write the reason in `report.md`.
- After implementation, write `report.md`.
- Update `validation.md` honestly.
- Move task to `ready_for_review` only after implementation is complete.
- Never move a task to `done`.
