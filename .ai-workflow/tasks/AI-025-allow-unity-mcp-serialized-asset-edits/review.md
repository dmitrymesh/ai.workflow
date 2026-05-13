# Review: AI-025

Reviewed 2026-05-13.

## Follow-up review 2026-05-14

The previous blocking issue is fixed. Manager, executor, reviewer, and Unity
guardrail guidance now apply the same rule: Unity serialized files are forbidden
by default; MCP/Editor-backed changes are allowed only with explicit task
authorization, named scope, tooling, and validation; direct manual YAML edits
are allowed only when `task.md` explicitly requests direct YAML editing and
defines the scope and validation.

## Follow-up review 2026-05-13

The original blocking issue is partially fixed: `AGENTS.md`, `executor.md`, and
`unity-guardrails.md` no longer say direct Unity YAML edits are never allowed.
However, manager and reviewer guidance still conflict with that exception.

## Decision

approve

## Blocking issues

None.

## Non-blocking issues

None.

## Scope check

Passed. Changes are limited to AGENTS, workflow role/Unity guardrail docs, and
task artifacts. No Unity serialized files, package files, project settings, or
`.meta` files were changed.

## Acceptance criteria check

Passed. The MCP/editor-backed three-condition rule is present, direct manual
YAML edits remain forbidden by default with an explicit task-contract exception,
manager/executor/reviewer guidance is internally consistent, `config.yaml` still
preserves the sensitive Unity file patterns, and no Unity serialized files were
changed.

## Test quality

Adequate for a documentation-only task. I reran `validate`, the required `rg`
scan, `git diff --name-only main...HEAD`, and `git diff --check`.

## Required fixes

None.
