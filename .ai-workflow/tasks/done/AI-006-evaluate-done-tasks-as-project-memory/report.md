# Execution Report: AI-006

## Summary

Evaluated done-task folders as project memory and defined a targeted-retrieval
policy. Added role-specific guidance to manager/executor/reviewer skills and a
"Done task history" section to the README. Added a read-only `history` CLI
command for listing and inspecting done tasks by area, keyword, or task ID.

**Policy decision:** done tasks are useful memory, but only via targeted
retrieval. Do not load all done tasks by default. Read linked tasks' `report.md`
first; use `history --area` / `history --show` for broader orientation; read
full folders only for direct parent/child work or protocol audit.

**Memory artifact chosen:** `history` CLI command (read-only, stdlib-only) over
a static `memory.md` — live data avoids staleness and requires no maintenance.

## Changed files

- `.ai-workflow/scripts/_history.py` — new module: `history` command
- `.ai-workflow/scripts/ai_task.py` — added `history` subcommand and import;
  updated module layout comment and usage examples
- `.ai-workflow/skills/manager.md` — added "Consulting done task history"
  section with retrieval policy and CLI examples
- `.ai-workflow/skills/executor.md` — added "Consulting done task history"
  section with retrieval policy and CLI examples
- `.ai-workflow/skills/reviewer.md` — added "Consulting done task history"
  section with retrieval policy and CLI examples
- `.ai-workflow/README.md` — added "Done task history" section with policy,
  table of artifacts, and `history` command reference

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `python .ai-workflow/scripts/ai_task.py board` — passed
- `python .ai-workflow/scripts/ai_task.py list` — passed
- `python .ai-workflow/scripts/ai_task.py history --help` — passed
- `python .ai-workflow/scripts/ai_task.py history` — listed all 5 done tasks
- `python .ai-workflow/scripts/ai_task.py history --area workflow` — returned 5
- `python .ai-workflow/scripts/ai_task.py history --keyword install` — returned 1 (AI-005)
- `python .ai-workflow/scripts/ai_task.py history --show AI-005` — printed report
- Forbidden file check: no done task folders modified; no status names changed;
  no non-stdlib dependencies added; no embeddings/vector stores/daemons added

## Assumptions

- Worked directly in the main checkout because `metadata.yaml.branch` is null
  (no worktree was prepared for this task). This is the documented exceptional
  case in `executor.md`.
- The `history --show` command prints the full `report.md`; truncation was
  deemed unnecessary given reports are typically short.

## Known risks

- None. All changes are additive documentation and a read-only CLI command.
  No existing behaviour was altered.
