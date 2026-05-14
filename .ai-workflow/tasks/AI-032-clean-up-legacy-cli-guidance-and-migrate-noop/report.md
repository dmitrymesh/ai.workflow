# Report: AI-032

## Summary

Cleaned up stale CLI guidance in the module docstring of `ai_task.py` and improved the
`migrate` command's no-op messaging when the repo is already on the flat task layout.

## Changed files

- `.ai-workflow/scripts/ai_task.py` — Replaced `move AI-001 ready` with `approve AI-001`
  (and `approve AI-001 --print-only`) in the module docstring. Added a `# Legacy` comment
  before the `prepare-worktree` examples to match the "legacy" label already present in the
  subparser help text.
- `.ai-workflow/scripts/_migrate.py` — When `migrate` finds no legacy status-directory tasks
  (`moved == 0` and `skipped == 0`) it now prints:
  `Nothing to migrate — repo is already on the flat task layout.`
  rather than `Migration complete: 0 moved, 0 skipped.`
- `.ai-workflow/scripts/test_migrate.py` — New focused test file with two tests covering the
  no-op migrate message.

## Validation performed

- `python .ai-workflow/scripts/ai_task.py --help` — confirms no `move AI-001 ready` in output;
  `prepare-worktree` help text says "Legacy command: prefer 'claim'..."
- `python .ai-workflow/scripts/ai_task.py migrate` — prints "Nothing to migrate — repo is
  already on the flat task layout."
- `python .ai-workflow/scripts/test_cascade.py` — 8/8 tests passed
- `python .ai-workflow/scripts/test_review.py` — 14/14 tests passed
- `python .ai-workflow/scripts/test_migrate.py` — 2/2 tests passed (new)
- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `rg -n "move AI-001 ready" .ai-workflow/scripts/ai_task.py` — no matches (requirement met)
- `git diff --name-only main...HEAD` — only in-scope files and this task folder

## Assumptions

- `prepare-worktree` is labeled via a docstring comment `# Legacy (prefer 'claim' for the
  standard executor workflow):` rather than removing the examples; command remains available
  per task scope ("do not remove any command").
- The `# Legacy` comment inside a Python docstring is unconventional but mirrors the intent;
  the subparser help text already carries the canonical "Legacy command" label.

## Known risks

None. Changes are purely textual (docstring + print message) with no behavioral impact on
status transitions or command logic.
