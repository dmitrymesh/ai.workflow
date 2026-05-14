# Report: AI-034

## Summary

Updated `README.md` and `.ai-workflow/README.md` to reflect the current branch-first
CLI behavior, add a new-repository installation path, add a post-install smoke test
checklist, and fix all stale workflow guidance.

## Changed files

### `README.md`

- **New repository installation path** — added a `### New repository` subsection before
  the existing "Existing repository" safe-install flow. New repos can simply run
  `install-plan /path --apply` + `init` + `validate` without merge snippets.
- **Post-install verification checklist** — added `### Post-install verification checklist`
  after the "Initialise and verify" step. Uses `approve` + `list-branches` + `reject` as
  a safe, disposable smoke test.
- **Basic commands: `approve` replaces `move AI-001 ready`** — the block describing
  `move AI-001 ready` is replaced by `approve AI-001` with a description noting it
  moves `draft` → `ready` on the task branch.
- **`list` vs `list-branches` explanation** — expanded the description of both commands
  and added a block-quote that explicitly explains when each should be used.
- **Recommended workflow step 2** — replaced `move AI-001 ready` with `approve AI-001`.
- **Recommended workflow step 3** — removed the two-mode `git worktree add` + `move in_progress`
  block; replaced with a single `claim AI-001` invocation. A note explains that `claim`
  handles both branch-first (pre-existing branch) and main-first (creates branch) modes.
- **Recommended workflow step 4** — removed the manual `git add … git commit` block after
  `review`. Added a note that `review` auto-commits by default and describes `--no-commit`
  for local inspection.
- **Example executor prompt** — replaced "git worktree add existing branch + move in_progress"
  with `claim AI-001` and a `cd` + `git branch --show-current` verification step.

### `.ai-workflow/README.md`

- **Quick start** — replaced `move AI-001 ready` with `approve AI-001` in the quick-start
  code block. Comment updated from "approve the contract by moving to ready" to just
  "approve the contract".

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

## Known risks

- The post-install smoke test uses `move AI-001 rejected --force` to clean up; this relies
  on `--force` allowing the `ready → rejected` transition, which is permitted by config.yaml.
- No CLI feature gaps were discovered during documentation work.
