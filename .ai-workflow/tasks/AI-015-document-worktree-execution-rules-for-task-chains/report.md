# Execution Report: AI-015

## Summary

Added a "Task chain execution rules" section to `.ai-workflow/README.md`
documenting practical rules for parent/child task chains and dependent worktree
branches. The section covers when a parent task needs a branch, the
one-executable-child-task-per-branch rule, the recommended serialized execution
order for blocked chains, a concrete AI-011 worked example, and the exception
criteria for approved parallel work.

## Changed files

- `.ai-workflow/README.md` — new "Task chain execution rules" section inserted
  between "Git worktree execution workflow" and "Branch-first workflow contract"

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `git diff --stat HEAD` — only `README.md` and task artifacts changed;
  no CLI scripts, no Unity files, no board.md
- Manual review against AI-012 branch-first contract — no contradictions found

## Assumptions

- Implemented in the task worktree on branch
  `ai/AI-015-document-worktree-execution-rules-for-task-chains`.
- The best location for this content is `.ai-workflow/README.md` as the
  canonical protocol reference consulted by all roles. Role skill files
  (executor.md, manager.md) already reference README.md for workflow detail.
- The worked example uses the AI-011 chain (AI-012 through AI-015) because
  acceptance criteria explicitly ask a new user to determine the correct
  execution order for that chain.
- The section does not contradict the AI-012 branch-first contract: the
  one-task-per-branch rule is consistent with the contract's lifecycle diagram,
  and the serialization guidance aligns with the contract's `blocked_by`
  semantics.

## Known risks

- None. All changes are documentation-only; no behavioral code was modified.
