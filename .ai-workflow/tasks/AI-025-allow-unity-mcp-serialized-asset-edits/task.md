# AI-025: Allow Unity MCP serialized asset edits

## Goal

Update the workflow instructions so Unity executors may modify scenes,
prefabs, assets, and related `.meta` files through Unity MCP or equivalent
Unity editor-backed tooling when the task contract explicitly authorizes that
kind of change.

## Context

Current Unity guardrails treat `.unity`, `.prefab`, `.asset`, `.meta`,
package, and project settings files as forbidden unless explicitly allowed in
`task.md`. This protects serialized Unity data from accidental text edits, but
it can be too restrictive for legitimate Unity work when the executor has a
Unity MCP server available.

The intended policy is not to allow unrestricted serialized file edits. The
policy should distinguish editor-backed Unity changes from direct manual YAML
or metadata edits, and require the manager to name the allowed asset or scene
scope in the task contract.

Relevant files:

- `AGENTS.md`
- `CLAUDE.md`
- `.ai-workflow/skills/unity-guardrails.md`
- `.ai-workflow/skills/manager.md`
- `.ai-workflow/skills/executor.md`
- `.ai-workflow/skills/reviewer.md`
- `.ai-workflow/config.yaml`
- `.ai-workflow/templates/task.md`

## Scope

Allowed changes:

- Revise Unity guardrail wording to allow Unity MCP/editor-backed serialized
  Unity file changes when explicitly authorized by `task.md`.
- Clarify that direct hand edits to Unity serialized YAML remain forbidden
  unless explicitly requested.
- Clarify what a task contract must include when allowing such changes:
  affected scenes/prefabs/assets, allowed operation type, and validation
  expectations.
- Update manager/executor/reviewer guidance so all roles apply the same rule.
- Update templates or config comments if needed to make the policy discoverable.

Forbidden changes:

- Do not remove the Unity forbidden file patterns from `config.yaml` unless the
  implementation replaces them with an equally explicit policy mechanism.
- Do not make Unity scene, prefab, asset, package, project settings, or `.meta`
  changes as part of this task.
- Do not add MCP server integration code.
- Do not change task status transitions, branch-first workflow semantics, or
  unrelated CLI behavior.
- Do not broaden the policy to allow arbitrary serialized Unity file edits.

## Requirements

- The updated instructions must state that Unity MCP/editor-backed changes to
  `.unity`, `.prefab`, `.asset`, and `.meta` files are allowed only when
  `task.md` explicitly authorizes them.
- The updated instructions must state that the task contract should name the
  allowed scene/prefab/asset scope as specifically as practical.
- The updated instructions must state that direct manual edits to serialized
  Unity YAML remain forbidden unless the task explicitly requests them.
- The executor guidance must no longer require stopping solely because an
  explicitly authorized Unity MCP/editor-backed change touches a listed Unity
  file pattern.
- The reviewer guidance must evaluate authorized Unity MCP/editor-backed
  changes against task scope instead of treating them as automatic forbidden
  file violations.
- The manager guidance must prompt managers to explicitly authorize Unity
  serialized asset changes when they are intended.

## Acceptance criteria

- Unity guardrails clearly distinguish explicitly authorized
  MCP/editor-backed changes from unauthorized direct serialized file edits.
- Manager, executor, and reviewer instructions are internally consistent.
- `AGENTS.md` and, if applicable, `CLAUDE.md` no longer imply that all Unity
  serialized file changes are blocked even when MCP/editor-backed changes were
  explicitly authorized.
- `config.yaml` still preserves a discoverable list of Unity sensitive file
  patterns or an equivalent replacement.
- No Unity project serialized files, packages, project settings, or `.meta`
  files are changed by this task.
- `python .ai-workflow/scripts/ai_task.py validate` passes.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- `rg -n "unity|prefab|asset|meta|forbidden|MCP|editor-backed" AGENTS.md CLAUDE.md .ai-workflow`
- `git diff --name-only main...HEAD`
- Manual diff review confirming no Unity serialized/project files changed

## Notes

Leave this task in `draft`. A human must approve it by moving it to `ready`
before execution.
