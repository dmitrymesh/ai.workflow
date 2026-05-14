# Report: AI-034

## Summary

Updated `README.md` and `.ai-workflow/README.md` to reflect the current branch-first
CLI behavior, add a new-repository installation path, add a post-install smoke test
checklist, and fix all stale workflow guidance.

Second attempt fixes three blocking issues raised in review:
- Replaced broken `create` + `approve` smoke test with safe read-only verification commands.
- Added branch-first task branch creation steps to `.ai-workflow/README.md` quick start
  before the `approve` call.
- Added `### Manager prepares task` subsection to the root README recommended workflow
  showing the explicit branch creation procedure.

## Changed files

### `README.md`

- **New repository installation path** — added a `### New repository` subsection before
  the existing "Existing repository" safe-install flow. New repos can simply run
  `install-plan /path --apply` + `init` + `validate` without merge snippets.
- **Post-install verification checklist** — replaced broken `create "Smoke test"` +
  `approve AI-001` sequence with safe read-only commands: `validate`, `roles`,
  `list-branches`, `history`, `--help`. Added inline note explaining that `create` alone
  does not create a task branch and `approve` requires the branch to exist.
- **Basic commands: `approve` replaces `move AI-001 ready`** — the block describing
  `move AI-001 ready` is replaced by `approve AI-001` with a description noting it
  moves `draft` → `ready` on the task branch.
- **`list` vs `list-branches` explanation** — expanded the description of both commands
  and added a block-quote that explicitly explains when each should be used.
- **Recommended workflow step 2** — replaced `move AI-001 ready` with `approve AI-001`.
- **Recommended workflow — Manager prepares task (new)** — added `### Manager prepares task`
  subsection with explicit branch-first branch creation procedure:
  `git checkout -b ai/AI-001-<slug>` → `git add` → `git commit` → `git checkout main`.
- **Recommended workflow step 3** — replaced two-mode `git worktree add` + `move in_progress`
  block with single `claim AI-001` invocation. A note explains that `claim` handles both
  branch-first (pre-existing branch) and main-first (creates branch) modes.
- **Recommended workflow step 4** — removed the manual `git add … git commit` block after
  `review`. Added a note that `review` auto-commits by default and describes `--no-commit`
  for local inspection.
- **Example executor prompt** — replaced "git worktree add existing branch + move in_progress"
  with `claim AI-001` and a `cd` + `git branch --show-current` verification step.

### `.ai-workflow/README.md`

- **Quick start** — added branch-first task branch creation steps between `create` and
  `approve`: `git checkout -b ai/AI-001-example-task` → `git add` → `git commit` →
  `git checkout main`. This makes the quick-start sequence actually executable in a
  branch-first installation.

### Files NOT changed

- `AGENTS.md` — already uses `list-branches` and does not show stale guidance.
- `CLAUDE.md` — already uses `list-branches`; executor instructions are current.

## Install paths covered

| Path | Where documented |
|------|-----------------|
| New/empty repository | README.md § "New repository" |
| Existing repository | README.md § "Existing repository" (was: "Installation into a project") |
| Upgrade | README.md § "Upgrade path" (unchanged) |
| Post-install verification | README.md § "Post-install verification checklist" (new) |
| Ownership model | README.md § "Ownership model" (unchanged) |
| Merge snippets for AGENTS.md, CLAUDE.md | `.ai-workflow/README.md` (unchanged) |

## Assumptions

- The `approve` command is the canonical human-approval path; `move <ID> ready` remains
  available as a low-level escape hatch but is no longer shown as the recommended path.
- The `review` command's `--no-commit` flag is documented inline; no separate section needed.
- The `.ai-workflow/README.md` branch-first workflow contract section (§ "Branch-first
  workflow contract") was not changed — it is a design-doc section and remains accurate.
- The post-install verification checklist uses read-only commands only; no task branch
  creation is required to run the verification.

## Known risks

- No CLI feature gaps were discovered during documentation work.
