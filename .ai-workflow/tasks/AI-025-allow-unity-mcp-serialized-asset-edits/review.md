# Review: AI-025

Reviewed 2026-05-13.

## Decision

changes_requested

## Blocking issues

1. The updated docs make direct serialized Unity YAML edits stricter than the
   task contract allows. `task.md` requires the instructions to say direct
   manual edits remain forbidden **unless the task explicitly requests them**.
   The branch instead says they are "never allowed" in
   `.ai-workflow/skills/unity-guardrails.md` and "remain forbidden even when the
   task authorizes the change" in `AGENTS.md`. `executor.md` also says "Do not
   hand-edit Unity serialized YAML" without the explicit-request exception.
   Adjust the wording across the affected docs so manual serialized YAML edits
   remain forbidden by default, but can be performed only when `task.md`
   explicitly requests direct manual YAML editing and defines scope/validation.

## Non-blocking issues

None.

## Scope check

Passed. Changes are limited to AGENTS, workflow role/Unity guardrail docs, and
task artifacts. No Unity serialized files, package files, project settings, or
`.meta` files were changed.

## Acceptance criteria check

Blocked by the manual-edit exception mismatch above. The MCP/editor-backed
three-condition rule is otherwise consistent across manager, executor, reviewer,
and Unity guardrail docs, and `config.yaml` still preserves the sensitive Unity
file patterns.

## Test quality

Adequate for a documentation-only task. I reran `validate`, the required `rg`
scan, `git diff --name-only main...HEAD`, and `git diff --check`.

## Required fixes

Update the direct-manual-YAML wording so it matches the task requirement:
forbidden by default, allowed only when explicitly requested by `task.md` with
specific scope and validation.
