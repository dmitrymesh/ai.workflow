# Review: AI-017

## Decision

approve

## Blocking issues

- None.

## Non-blocking issues

- `report.md` still says `test_show.py` has 5 focused tests, while the actual file has 3 `test_show` tests and `validation.md` correctly records 11 total tests across `test_show` and `test_cascade`. This is documentation drift only; the validation record is accurate.

## Scope check

In scope. Code changes are limited to `show_task` status display and focused regression tests, plus task artifacts and reciprocal `related` metadata links. No forbidden files were changed.

## Acceptance criteria check

Met.

- `show AI-016` prints `status:     done`.
- `show AI-011` prints `status:     done`.
- `list` continues to group tasks by `metadata.yaml.status`; `AI-017` is under `ready_for_review` before approval.
- Existing cascade tests pass.
- `validate` passes.
- `report.md` includes the required dogfood note.

## Test quality

Good focused coverage. `test_show` covers metadata status source, all non-terminal statuses, and display-only/no-mutation behavior. Existing cascade tests still pass.

## Required fixes

- None.
