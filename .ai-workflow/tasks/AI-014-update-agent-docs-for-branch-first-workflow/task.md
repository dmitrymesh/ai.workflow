# AI-014: Update agent docs for branch-first workflow

## Goal

Update agent-facing and user-facing documentation so managers, executors, and
reviewers follow the branch-first task workflow consistently.

## Context

AI-012 defines the branch-first workflow contract and AI-013 implements
discovery support. After those changes, the documentation and role skills must
stop describing `main` as the live control plane for active tasks.

The docs must clearly describe that active task communication happens through
commits in the task branch, and that final integration can be local merge or
hosted PR depending on config.

## Scope

Allowed changes:

- Update `.ai-workflow/README.md`.
- Update root `README.md` if it needs user-facing workflow changes.
- Update `AGENTS.md` and `CLAUDE.md` adapter instructions if they reference the
  old main-first workflow.
- Update `.ai-workflow/skills/manager.md`,
  `.ai-workflow/skills/executor.md`, and `.ai-workflow/skills/reviewer.md`.
- Update example prompts and command snippets to use the branch-first workflow
  and the discovery commands from AI-013.

Forbidden changes:

- Do not implement CLI behavior in this documentation task.
- Do not change workflow config except for documentation examples that match
  AI-012.
- Do not modify task folders except this task's `report.md` and
  `validation.md`.
- Do not edit generated `.ai-workflow/board.md`.

## Requirements

- Manager docs must say where task branches/worktrees are created and what
  commit is expected after creating a draft task contract.
- Human approval docs must say how approval is recorded in the task branch.
- Executor docs must say how to discover ready tasks, enter the correct
  worktree/branch, commit implementation/report/validation artifacts, and
  submit according to the branch-first model.
- Reviewer docs must say review artifacts are committed to the task branch for
  executor handoff.
- Docs must describe both configured integration modes:
  - local merge through git client or future local integration command;
  - hosted pull request workflow.
- Docs must preserve the rule that only a human approves `draft -> ready` and
  agents do not silently expand scope.

## Acceptance criteria

- No role skill tells agents that active task folders are managed primarily in
  `main` after claim.
- Executor and reviewer instructions include commit expectations for task
  artifacts.
- User-facing docs explain how active tasks are discovered when they are not in
  `main`.
- Integration mode examples match `.ai-workflow/config.yaml` and AI-012.
- The updated docs are concise enough to remain usable as agent entrypoints.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- Search updated docs/skills for stale main-first or status-directory workflow
  instructions that conflict with AI-012.
- Review `git diff` to confirm changes are documentation-only and scoped.

## Notes

Blocked by AI-012 because documentation should follow the approved contract.
If AI-013 changes command names during implementation, this task should use the
final command names from that implementation.
