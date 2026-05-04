# Review: AI-014

## Decision

changes_requested

## Blocking issues

- `.ai-workflow/skills/manager.md` still has a generic "Post-approval executor handoff" section that tells the executor to use `claim` from the main checkout and describes creating a new branch/worktree from main. This is now only valid for `main_first`, but it appears immediately after the branch-first creation section without being labeled as legacy or split by mode. As written, a manager following the branch-first docs can still hand off incorrect main-first instructions, which violates the acceptance criterion that role skills stop presenting `main` as the active task control plane after approval.

## Non-blocking issues

- Previous concerns about executor/README mode split, out-of-scope AI-012/AI-013 metadata edits, and `list-branches` merged wording are fixed.

## Scope check

Documentation changes are now scoped to requested docs plus AI-014 artifacts. AI-012 and AI-013 metadata edits were removed.

## Acceptance criteria check

Not satisfied yet. Executor and README now split branch-first vs main-first correctly, but manager role instructions still preserve a generic main-checkout `claim` handoff.

## Test quality

`validate` passes. I reran `validate`, inspected the branch diff, and checked the updated role/user-facing docs against AI-012 and the current `claim` behavior.

## Unity-specific risks

Not applicable.

## Required fixes

- Update `.ai-workflow/skills/manager.md` post-approval handoff to be mode-aware. For branch-first, say the manager/human has already committed the ready task branch and executors discover it with `list-branches` then open a worktree on the existing branch; keep `claim from main` only under `main_first` legacy guidance.
