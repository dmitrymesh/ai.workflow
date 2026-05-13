# AI-027: Require Unity MCP recompile validation

## Goal

Update the Unity workflow instructions so executors working on Unity-profile
projects must trigger a Unity project recompilation through the available Unity
MCP/editor integration after completing a task, then inspect Unity logs or
compiler diagnostics for errors before submitting.

## Context

Unity tasks can pass file-level checks while still leaving the Unity editor in
a compile-error state. For Unity-profile projects, executor validation should
include an editor-backed recompilation step and log/error inspection when a
Unity MCP server or equivalent editor automation is available.

This task updates the protocol guidance only. It does not implement a Unity MCP
server or change a Unity project.

Relevant files:

- `AGENTS.md`
- `CLAUDE.md`
- `.ai-workflow/skills/unity-guardrails.md`
- `.ai-workflow/skills/executor.md`
- `.ai-workflow/skills/reviewer.md`
- `.ai-workflow/skills/manager.md`
- `.ai-workflow/profiles/unity/README.md`
- `.ai-workflow/templates/task.md`
- `.ai-workflow/config.yaml`

## Scope

Allowed changes:

- Add Unity-profile validation guidance requiring executor-triggered Unity
  recompilation through MCP/editor automation when available.
- Require executor validation reports to state whether recompilation was run,
  whether compile errors were present, and where the logs/diagnostics were
  checked.
- Clarify that if Unity MCP/editor automation is unavailable, the executor must
  write `not run` with the concrete reason instead of claiming success.
- Update reviewer guidance to verify the recompilation/log check for Unity
  tasks.
- Update manager guidance or task template text so Unity tasks include this
  validation expectation when applicable.
- Keep wording tool-agnostic enough to support Unity MCP or equivalent editor
  automation, while naming Unity MCP as the preferred route.

Forbidden changes:

- Do not implement or configure a Unity MCP server.
- Do not modify Unity scenes, prefabs, assets, `.meta` files, packages, or
  project settings.
- Do not add dependencies.
- Do not change task statuses, transitions, branch-first workflow behavior, or
  unrelated CLI behavior.
- Do not require PlayMode tests for every Unity task; only require recompilation
  and log/error inspection unless the task itself needs tests.

## Requirements

- Unity-profile executor instructions must require recompilation through Unity
  MCP/editor automation after task implementation when that tooling is
  available.
- Executor instructions must require checking Unity compiler errors and relevant
  editor logs before submission.
- Validation instructions must require honest reporting:
  - `passed` only if recompilation/log inspection was actually performed and no
    relevant errors were found.
  - `failed` if compile errors or task-related Unity errors remain.
  - `not run` if Unity MCP/editor automation is unavailable, with the reason.
- Reviewer instructions must treat missing Unity recompilation/log validation as
  a review concern for Unity-profile tasks unless `validation.md` documents why
  it could not be run.
- Manager guidance must help managers include this validation requirement in
  Unity task contracts.
- The wording must not imply that non-Unity projects need Unity MCP validation.

## Acceptance criteria

- Unity guardrails mention Unity MCP/editor-backed recompilation and log/error
  inspection as required validation for Unity-profile execution when available.
- Executor guidance clearly says what to record in `validation.md`.
- Reviewer guidance clearly says how to evaluate missing or failed Unity
  recompilation validation.
- Manager guidance or task template makes the validation expectation
  discoverable when creating Unity tasks.
- No Unity project serialized files, packages, project settings, or `.meta`
  files are changed by this task.
- `python .ai-workflow/scripts/ai_task.py validate` passes.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- `rg -n "Unity|MCP|recompil|compile|log|validation|not run" AGENTS.md CLAUDE.md .ai-workflow`
- `git diff --name-only main...HEAD`
- Manual diff review confirming no Unity project files were changed

## Notes

Leave this task in `draft`. A human must approve it by moving it to `ready`
before execution.
