> Claude Code adapter command for the executor role.
> Role assignments are configured in `.ai-workflow/config.yaml`.

Read `.ai-workflow/skills/executor.md`.

Execute task: $ARGUMENTS

Rules:

- Locate the task folder by ID or path.
- Read `task.md`.
- Read `metadata.yaml`.
- Move task to `in_progress` if it is currently `ready`.
- Before editing, list planned files.
- Follow task scope exactly.
- Do not modify forbidden files unless explicitly allowed.
- Write `report.md`.
- Update `validation.md`.
- Move task to `ready_for_review` when complete.
- Do not move task to `done`.
