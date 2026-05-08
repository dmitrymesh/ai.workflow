# AI-018: Audit workflow and plan CLI refactor

## Goal

Review the full `.ai-workflow` task protocol and `ai_task.py` CLI after the
recent workflow changes, then produce a concrete, prioritized refactor plan.

The goal is not to rewrite the tool in one pass. The goal is to determine
whether the current workflow is ready for real project use, identify the
highest-risk command and state-management problems, and define small follow-up
implementation tasks for the refactor.

## Context

Recent tasks changed the workflow model and command surface:

- AI-009/AI-010 simplified status management around stable task folders.
- AI-011 adopted branch-first as the intended workflow direction.
- AI-012 through AI-015 documented branch-first workflow, discovery, role docs,
  and task-chain execution rules.
- AI-016 added review-time relationship cascade behavior.
- AI-017 is dogfooding a concrete command-status bug found during review:
  `show` printed `status: tasks` in the flat task layout.
- Human approval in branch-first mode is currently awkward: approving a draft
  task requires entering the task worktree, running `move <TASK-ID> ready`, and
  committing metadata there. A likely product improvement is a main-checkout
  command such as `approve <TASK-ID>` that finds the task branch, moves
  `draft -> ready`, and commits the approval artifact on that branch.

The project goal is a minimal, git-native, portable AI task protocol for small
Unity pet projects. It should remain local-first, low-overhead, role-based, and
usable without dashboards, SaaS, databases, or a single vendor-specific runtime.

## Scope

Allowed changes:

- Review `.ai-workflow/README.md`, `.ai-workflow/PROJECT_GOALS.md`,
  `.ai-workflow/config.yaml`, role skill files, adapter docs, and all
  `.ai-workflow/scripts/*.py` modules.
- Run command smoke checks against the current branch-first workflow where safe.
- Produce a written workflow review covering fit against project goals,
  command correctness, source-of-truth rules, branch/worktree behavior,
  relationship handling, validation, and human approval boundaries.
- Produce a prioritized refactor plan with small follow-up task candidates.
- Add or update documentation only if needed to record the audit result inside
  this task's artifacts.

Forbidden changes:

- Do not perform the broad code refactor in this task.
- Do not switch workflow modes or rewrite lifecycle statuses.
- Do not modify Unity scene, prefab, asset, meta, package, or project settings
  files.
- Do not add non-stdlib Python dependencies.
- Do not introduce hosted-service requirements.
- Do not edit generated `.ai-workflow/board.md` as a source file.
- Do not mark any task `done` unless acting through the normal reviewer flow.

## Requirements

- Evaluate whether the current workflow satisfies `.ai-workflow/PROJECT_GOALS.md`.
- Identify concrete command bugs, confusing behavior, or source-of-truth
  conflicts. Each finding must name the affected command/file.
- Review branch-first task creation, approval, execution, review, and
  integration steps for gaps between docs and implementation.
- Review the human approval ergonomics for branch-first tasks, including
  whether a dedicated `approve <TASK-ID>` command should be added.
- Review whether newly created task worktrees follow the repository convention:
  `../ai_workflow.worktrees/<task-id>-<slug>`, not ad hoc temporary folders.
- Review whether command discovery works when active tasks live only in task
  branches.
- Review how a control-plane checkout (`main`) should update committed task
  branch state without requiring the human to manually `cd` into a worktree.
- Review relationship behavior, including parent/child and blocks/blocked_by
  consistency after review completion.
- Review test coverage and recommend the smallest useful CLI test structure.
- Produce a proposed refactor sequence, split into reviewable tasks.
- Record validation commands and results in `validation.md`; write `not run`
  for anything skipped.

## Acceptance criteria

- `report.md` contains a `## Workflow review` section with a clear verdict:
  ready, conditionally ready, or not ready for real Unity project use.
- `report.md` contains a `## Findings` section ordered by severity, with each
  finding tied to concrete files or commands.
- `report.md` contains a `## Refactor plan` section that lists small follow-up
  tasks, each with scope, risk, and suggested validation.
- `report.md` includes a specific finding on branch-first human approval
  friction and a recommendation for or against adding `approve <TASK-ID>`.
- `report.md` explicitly states whether AI-017 should be completed before any
  broader refactor starts.
- `report.md` explicitly states whether current task worktree locations follow
  the documented sibling-directory convention, and lists any exceptions.
- `validation.md` records exact command smoke checks, including at minimum:
  `validate`, `list`, `list-branches`, `show-branch` for an active branch, and
  `git worktree list`.
- The audit identifies any CLI, role-skill, or manager-procedure gap that could
  cause future tasks to be created outside the standard worktree location.
- No implementation refactor is performed as part of this task.
- The task remains small enough that the reviewer can verify the audit without
  reading unrelated code changes.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- `python .ai-workflow/scripts/ai_task.py list`
- `python .ai-workflow/scripts/ai_task.py list-branches`
- `python .ai-workflow/scripts/ai_task.py show-branch AI-017` if the branch
  exists locally; otherwise record `not run` with reason
- `git worktree list`
- Read-only inspection of `.ai-workflow/scripts/*.py`
- Diff review confirming no forbidden files changed

## Notes

This is the audit task that should precede broad refactoring. The expected
output is a concrete implementation backlog, not a large mixed refactor.

AI-017 is intentionally left as a separate dogfood implementation task because
it exercises a narrow real bug in the new branch-first workflow.
