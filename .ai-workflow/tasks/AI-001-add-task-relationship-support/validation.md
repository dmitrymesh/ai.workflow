# Validation: AI-001

## Local

- Project compile: n/a (no compiled language; pure Python script + Markdown).
- Unit/EditMode tests: not run (no test suite exists in this repo; out of scope to add one).
- Integration/PlayMode tests: not run (n/a — generic profile, no Unity).
- `python .ai-workflow/scripts/ai_task.py validate`: **passed** on the final state.
- `python .ai-workflow/scripts/ai_task.py board`: **regenerated** without errors; new `Parent` / `Blocked By` columns present.
- `python .ai-workflow/scripts/ai_task.py list`: **shows** `parent=…` and `blocked_by=…` on each task row.
- CLI smoke test (scratch tasks AI-002/AI-003, removed afterwards):
  - `create` produced metadata.yaml containing `parent: null`, `children: []`, `blocks: []`, `blocked_by: []`, `related: []`. **passed**
  - `link <task> parent <other>`: set local `parent`, appended to other's `children`. **passed**
  - `link <task> child <other>`: set other's `parent`, appended to local `children`. (verified by inverting roles in the same run)
  - `link <task> blocks <other>`: appended to local `blocks` and other's `blocked_by`. **passed**
  - `link <task> blocked-by <other>`: appended to local `blocked_by` and other's `blocks`. **passed**
  - `link <task> related <other>`: appended to both `related` lists. **passed**
  - `unlink <task> parent`: cleared local `parent`, removed local id from former parent's `children`. **passed**
  - `unlink <task> blocked-by <other>`: removed entries from both sides. **passed**
  - `unlink <task> related <other>`: removed entries from both sides. **passed**
  - `show <task>`: printed all five relationship fields plus status/risk/area/branch/path. **passed**
- Validate failure-mode smoke test:
  - Hand-edited AI-003's `parent` to a non-existent id `AI-999`.
  - `validate` failed with both `Relationship error in AI-003: parent references missing task 'AI-999'` and `Reciprocity error: AI-002.children contains AI-003 but AI-003.parent=AI-999`. Exit code 1. **passed**
  - Restored AI-003 and `validate` passed again. **passed**
- Backward compatibility of pre-existing commands (`create`, `move`, `list`, `board`, `validate`, `path`): all exercised during the run, all working. **passed**

## Human review

- Status: pending
- Reviewer: null

## Guardrails

- Forbidden files changed: **none**. `git status --short` shows only the files explicitly listed in `task.md`'s allowed-changes scope (templates/metadata.yaml, scripts/ai_task.py, skills/manager.md, skills/reviewer.md, .ai-workflow/README.md, README.md, the regenerated board.md, and the AI-001 task folder itself). No `.env*`, no other forbidden generic patterns.
- Package / dependency changes: **none**. Script remains stdlib-only Python; no `requirements.txt` or similar added.
- Status lifecycle changes: **none**. The set of statuses and allowed transitions is unchanged.

## Notes

- `validate` does not enforce reciprocity for `related` links by design — the task spec only requires reciprocity for parent/child and blocks/blocked_by. The CLI itself produces reciprocal `related` links, so this only matters for hand-edited metadata.
- `templates/task.md` was not modified; relationships are recorded in `metadata.yaml` and managed via CLI as specified by the updated `manager.md`.
