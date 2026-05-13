# Review: AI-025

Reviewed 2026-05-13.

## Follow-up review 2026-05-13

The original blocking issue is partially fixed: `AGENTS.md`, `executor.md`, and
`unity-guardrails.md` no longer say direct Unity YAML edits are never allowed.
However, manager and reviewer guidance still conflict with that exception.

## Decision

changes_requested

## Blocking issues

1. `.ai-workflow/skills/manager.md:42` and
   `.ai-workflow/skills/reviewer.md:15` are not consistent with the explicit
   direct-YAML exception now documented in `unity-guardrails.md`. Manager
   guidance only describes authorizing Unity MCP/Editor tooling and says "not
   direct YAML edits"; reviewer guidance only accepts Unity serialized diffs
   when task.md specifies MCP or Editor-backed tooling. If a task explicitly
   requests direct manual YAML editing with scope and validation, as permitted
   by `unity-guardrails.md`, the manager guidance does not explain how to write
   that contract and the reviewer guidance would still flag it as missing the
   MCP/editor condition. Update manager and reviewer docs so all roles apply the
   same rule: direct YAML edits are forbidden by default, but may be accepted
   only when `task.md` explicitly requests direct YAML editing and defines the
   exact scope and validation.

## Non-blocking issues

None.

## Scope check

Passed. Changes are limited to AGENTS, workflow role/Unity guardrail docs, and
task artifacts. No Unity serialized files, package files, project settings, or
`.meta` files were changed.

## Acceptance criteria check

Blocked by the manager/reviewer inconsistency above. The MCP/editor-backed
three-condition rule is otherwise present, `config.yaml` still preserves the
sensitive Unity file patterns, and no Unity serialized files were changed.

## Test quality

Adequate for a documentation-only task. I reran `validate`, the required `rg`
scan, `git diff --name-only main...HEAD`, and `git diff --check`.

## Required fixes

Update manager and reviewer guidance to match the direct-manual-YAML exception
already present in `unity-guardrails.md` and `executor.md`.
