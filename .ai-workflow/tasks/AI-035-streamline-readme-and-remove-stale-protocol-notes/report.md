# Report: AI-035

## Summary

Removed stale "Future work" planning text, obsolete future-CLI comments, and
historical problem-framing from `.ai-workflow/README.md`. Marked `migrate` as
legacy/upgrade-only in both READMEs.

## What was removed

### `.ai-workflow/README.md`

- **`### Future work (not in this task)` section** — deleted. Listed AI-013, AI-014,
  AI-015 as future work; all three tasks are done. No longer valid user-facing docs.
- **Branch-first workflow contract intro** — replaced stale "design document...
  intended future behavior... Implementation lives in later tasks (AI-013, AI-014,
  AI-015)... not yet enforced by the CLI" with "This section is the reference
  contract for the branch-first task workflow. All CLI commands and config keys
  described here are implemented and in use."
- **Stale comment `(future CLI — AI-013)`** — removed from list-branches example.
- **"Future CLI support (AI-014) will include:" block** — removed `open-pr` example
  and surrounding future-CLI framing from the `pull_request` integration section.
  Replaced with direct note to use the platform UI or provider CLI.
- **`### Visibility constraint` subsection** — removed. Described a worktree
  visibility problem and its solution (`claim` copies approved task folder).
  The solution is already documented in the `claim` section; the problem framing
  is implementation history not needed by new users.
- **`### Why worktrees?` historical framing** — condensed to `### Worktree rule`.
  Removed the "two problems" prose; kept only the rule and the control-plane
  explanation.

### `README.md`

No sections removed. The file was already clean from AI-034.

## What was condensed

### `.ai-workflow/README.md`

- `## Git worktree execution workflow` opener is now ~4 lines instead of ~18.
  All operational content (naming conventions, `claim` docs, executor/reviewer
  workflow, cleanup) is unchanged.

## What was intentionally kept

- **`## Branch-first workflow contract`** — full section retained as reference.
  Source of truth table, lifecycle diagram, manager/executor/reviewer steps,
  integration modes, config keys reference, backward compatibility. Only the
  stale future-work intro was updated.
- **`## Git worktree execution workflow`** — naming conventions, claim command,
  executor/reviewer workflow, update-from-main, cleanup. All current.
- **`## Review appeal`** — current; not duplicated elsewhere.
- **`## Task chain execution rules`** — current reference for blocked chains.
- **Unity guardrails in `README.md`** — unchanged.
- **Safety constraints** — all preserved: install-plan ownership, draft→ready
  approval only by human, executor does not mark done, reviewer uses current
  `review` command, `list-branches` for branch-first discovery, Unity guardrails.

## Migrate framing

`migrate` is now labeled **Legacy upgrade only** in both files. The command is
still documented for users upgrading from the old status-by-directory layout.

## Files changed

- `.ai-workflow/README.md` — removed Future work section, stale intro, future-CLI
  blocks; condensed worktree section opener; marked migrate as legacy.
- `README.md` — labeled migrate as legacy upgrade only.

## Known risks

None. No CLI, config, or protocol semantics changed.
