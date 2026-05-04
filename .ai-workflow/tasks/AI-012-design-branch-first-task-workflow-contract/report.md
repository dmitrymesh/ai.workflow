# Execution Report: AI-012

## Summary

Designed and documented the branch-first task workflow contract. The contract
is expressed as:

1. A new `## Branch-first workflow contract` section in `.ai-workflow/README.md`
   covering the full lifecycle, actor responsibilities, source-of-truth rules,
   integration modes, and discovery configuration.
2. A new `workflow:` block in `.ai-workflow/config.yaml` with four sub-sections
   (`mode`, `integration`, `discovery`, `task_ids`) that make the design
   machine-readable and selectable by future CLI tasks.

No CLI implementation files were changed.

## Changed files

- `.ai-workflow/README.md` — added `## Branch-first workflow contract` section
  (~180 lines) after the existing `## Git worktree execution workflow` section.
- `.ai-workflow/config.yaml` — added `workflow:` block with `mode`,
  `integration`, `discovery`, and `task_ids` sub-keys. All keys are commented
  to explain semantics and valid values.

## How the design addresses the four AI-010 problems

| # | Problem | Contract solution |
|---|---------|------------------|
| 1 | Merge conflicts from main-created tasks | In `branch_first` mode, the task folder is created in the task branch; `main` never receives a task folder that will also be edited in a branch. No divergent history. |
| 2 | No PR/local integration path | `workflow.integration.mode` is either `local_merge` (human merges locally) or `pull_request` (hosted PR). Both paths are first-class and documented with commands. |
| 3 | Uncommitted reviewer artifacts | The contract mandates that `review`, `decision.yaml`, and `metadata.yaml` are committed to the task branch by the `review` command before the reviewer hands off. Dry-run or local-only writes are a protocol violation. |
| 4 | Missed ready-state refresh | Executors discover `ready` tasks by scanning task branches via `list-branches` / `show-branch` commands (AI-013). No `main` refresh is required. |

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — run after changes; see
  validation.md for result.
- Manual review of changed files against all acceptance criteria in `task.md`.
- Confirmed no CLI implementation files (scripts/*.py) were modified.

## Assumptions

- The `workflow:` config block is accepted by the existing schema/validate
  logic as unknown-but-harmless YAML (no strict unknown-key rejection). If
  validate fails on the new keys, that constitutes a scope-expanding schema
  change belonging to AI-013; in that case the config additions would need to
  be deferred.
- "Future CLI" references in the README (AI-013, AI-014) are explicitly marked
  as future work placeholders, not implemented commands.

## Known risks

- The `branch_scan` ID strategy documented under `task_ids.strategy` has a
  race condition for multi-author teams (two managers simultaneously creating
  branches). The contract documents this and recommends `central_counter` for
  teams. Enforcement is a future task.
- The `review` command commit-mandate is currently a policy rule, not enforced
  by the CLI. A future task (AI-015) should add a guard.
