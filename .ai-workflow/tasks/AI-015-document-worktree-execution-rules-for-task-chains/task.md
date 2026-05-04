# AI-015: Document worktree execution rules for task chains

## Goal

Document practical execution rules for parent/child task chains and dependent
worktree branches so other users can run multi-task workflow changes with fewer
merge/order mistakes.

## Context

While planning AI-011 through AI-014, the expected execution model was clarified:

- Parent tasks such as AI-011 are umbrella/context tasks and usually do not need
  their own implementation branch unless they have direct deliverables.
- Each executable child task should use its own task branch/worktree.
- Dependent tasks should usually wait for their blockers to be merged before
  being claimed, so each task starts from updated `main`.
- Documentation tasks that describe CLI behavior should wait until the CLI task
  has produced final command names.

These rules are currently implicit in conversation, not protocol documentation.

## Scope

Allowed changes:

- Update `.ai-workflow/README.md` and/or role skills with concise rules for
  executing task chains using worktrees.
- Clarify when a parent task should or should not have its own branch.
- Clarify the expected branch/worktree strategy for child tasks.
- Clarify that blocked tasks should normally wait for blocker merge before
  claim, unless explicitly approved for parallel work.
- Clarify how documentation tasks should depend on implementation tasks when
  they document concrete CLI behavior.

Forbidden changes:

- Do not implement new CLI behavior in this task.
- Do not change task statuses or transitions.
- Do not modify workflow config unless AI-012 requires a matching documentation
  example and the change is explicitly justified.
- Do not modify task folders except this task's `report.md` and
  `validation.md`.
- Do not edit generated `.ai-workflow/board.md`.

## Requirements

- The docs must explain "one executable child task = one branch/worktree".
- The docs must explain that umbrella parent tasks are coordination artifacts
  unless their task contract says otherwise.
- The docs must explain the recommended order:
  - approve/claim/execute/review/merge the first dependency;
  - start the dependent task from updated `main`;
  - avoid parallel execution when task outputs affect command names, docs, or
    shared protocol files.
- The docs must explain what exception allows parallel work: disjoint write
  scope and explicit dependency/merge strategy.
- The docs must avoid contradicting the branch-first contract from AI-012.

## Acceptance criteria

- A new user can read the docs and determine whether AI-011 needs its own
  branch and why.
- A new user can determine the correct execution order for AI-012, AI-013,
  AI-014, and AI-015.
- The documentation explicitly warns that starting a blocked task before its
  blocker is merged may create stale assumptions or merge conflicts.
- No implementation files are changed.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- Review changed documentation for consistency with AI-012.
- Review `git diff` to confirm changes are documentation-only and scoped.

## Notes

Blocked by AI-012 so this documentation can align with the selected
branch-first workflow contract.
