# Review: AI-015

## Decision

changes_requested

## Blocking issues

- The AI-011 worked example contradicts AI-013's task contract. The new section says "AI-012 and AI-013 can be executed in parallel" because their write scopes are disjoint, but AI-013's `task.md` explicitly says it is blocked by AI-012 because it must follow the approved workflow contract. This weakens the rule the section is trying to teach: disjoint files are not enough when the blocker defines behavior or command semantics the dependent task implements.

## Non-blocking issues

- None.

## Scope check

In scope. The diff changes `.ai-workflow/README.md` and AI-015 task artifacts only; no implementation files or generated board changes are present.

## Acceptance criteria check

Not satisfied yet. The docs explain parent/child branch strategy and warn about early blocked work, but the concrete AI-011 ordering example gives the wrong guidance for AI-013 relative to AI-012.

## Test quality

`validate` passes. I reran `python .ai-workflow/scripts/ai_task.py validate`, inspected the diff, and checked the new section against AI-012/AI-013 task contracts.

## Unity-specific risks

Not applicable.

## Required fixes

- Correct the worked example so AI-013 starts only after AI-012 is approved/merged, unless the text explicitly marks any earlier execution as a human-approved exception with a defined merge strategy. Keep the AI-015 guidance consistent with its own blocked-by relationship.
