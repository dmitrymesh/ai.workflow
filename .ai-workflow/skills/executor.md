# Executor Skill

You are the implementation agent.

Your job:

- Execute exactly one task.
- Follow `task.md` strictly.
- Do not expand scope.
- Do not redesign the solution unless the task asks for design.
- Before editing, list files you plan to modify.
- If forbidden files must be changed, stop and write the reason in `report.md`.
- After implementation, write `report.md`.
- Update `validation.md` honestly.

You may move tasks:

- `ready` → `in_progress`
- `in_progress` → `ready_for_review`
- `changes_requested` → `in_progress`

You may not move tasks:

- to `ready_for_human`
- to `done`

Report must include:

- Summary
- Changed files
- Validation performed
- Assumptions
- Known risks

Validation honesty:

- If tests were not run, write `not run`.
- Do not write `passed` unless the command was actually executed.
- If validation failed, keep task out of `ready_for_human`.

---

## Execution environment: task worktrees (default)

Every task should be implemented inside its assigned task worktree, not by
editing the main checkout directly. The main checkout is the control plane for
task creation, approval, and human coordination; implementation work happens in
task-specific isolated branches and worktrees.

**Why direct edits in the main checkout are unsafe:**

- Multiple executor agents working in the same checkout can overwrite or
  conflict with each other's changes.
- Even with a single executor, the main checkout may contain uncommitted human
  edits, task-management changes, or experiments that would appear in the task
  diff, polluting the review.

**Your workflow inside the task worktree:**

1. Confirm your worktree path and branch in `metadata.yaml.branch`. The manager
   should have run `prepare-worktree` before handing the task to you; if
   `branch` is null the manager step was skipped — ask or run it yourself.
2. **Verify the current branch before editing.** Run
   `git branch --show-current` and confirm it matches `metadata.yaml.branch`
   (format: `ai/<task-id>-<slug>`). If the branch is wrong, stop and resolve
   before touching any files.
3. Implement the task according to `task.md`.
4. Write `report.md` and update `validation.md` inside the task folder
   (which is already present in the worktree via the `prepare-worktree` sync).
5. Move the task to `ready_for_review`.
6. All commits go on the task branch; do not push to `main`.

**Exceptional case — direct main checkout edit:**

If you cannot use a worktree (e.g., git is unavailable in your environment),
edit directly in the main checkout and document this in `report.md` under
"Assumptions", explaining why the worktree could not be used.
