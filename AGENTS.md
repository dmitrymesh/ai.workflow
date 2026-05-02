# Repository Agent Instructions

This repository uses the Portable AI Task Protocol.

Before managing, executing, or reviewing AI tasks:

1. Read `.ai-workflow/README.md` if present.
2. Read `.ai-workflow/config.yaml`.
3. Read the relevant role skill:
   - `.ai-workflow/skills/manager.md`
   - `.ai-workflow/skills/executor.md`
   - `.ai-workflow/skills/reviewer.md`
4. Read the target task folder under `.ai-workflow/tasks/<status>/<task-id>/`.

General rules:

- Do not mark tasks as `done` unless explicitly acting as a human validator.
- Do not expand task scope.
- Do not silently ignore acceptance criteria.
- Do not claim tests passed unless they were actually run.
- Write `not run` when validation was not executed.
- Keep diffs small.
- Prefer explicit reports over chat-only summaries.

For Unity projects:

- Do not modify `.unity`, `.prefab`, `.asset`, or `.meta` files unless the task explicitly allows it.
- Do not modify packages or project settings unless the task explicitly allows it.
- Do not rename serialized fields without migration notes.
- Prefer pure C# logic and EditMode tests where possible.
