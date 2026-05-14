# Report: AI-034

## Summary

Updated `README.md` and `.ai-workflow/README.md` to reflect the current branch-first
CLI behavior, add a new-repository installation path, add a post-install smoke test
checklist, fix all stale workflow guidance, add post-install commit guidance, and add
a configuration decision checklist.

## Changed files

### `README.md`

- **New repository installation path** — added a `### New repository` subsection before
  the existing "Existing repository" safe-install flow. New repos can simply run
  `install-plan --apply` + `init` + `validate`, then commit.
- **Commit step in new repo section** — added explicit `git add`/`git commit` after
  `validate` so new-repo installers know exactly what to stage.
- **Post-install verification checklist** — uses safe read-only commands: `validate`,
  `roles`, `list-branches`, `history`, `--help`. No `create` + `approve` smoke test;
  includes inline note explaining that `create` alone does not create a task branch.
- **What to commit after installation (new)** — added `### What to commit after installation`
  subsection with separate blocks for new repos, existing repos (after merge-snippet
  edits), and upgrades. Explicitly calls out that `board.md` must not be committed.
- **Configuration checklist (new)** — added `### Configuration checklist` subsection with
  a table covering all post-init decisions: `profile`, `workflow.mode`,
  `workflow.integration.mode`, `workflow.integration.provider`, `agents.*.default_tool`,
  and `workflow.discovery.scope`.
- **Basic commands: `approve` replaces `move AI-001 ready`** — the block describing
  `move AI-001 ready` is replaced by `approve AI-001`.
- **`list` vs `list-branches` explanation** — expanded block-quote explaining when each
  command is appropriate.
- **Recommended workflow step 2** — replaced `move AI-001 ready` with `approve AI-001`.
- **Recommended workflow — Manager prepares task** — added `### Manager prepares task`
  subsection with explicit branch-first branch creation procedure.
- **Recommended workflow step 3** — replaced two-mode `git worktree add` + `move in_progress`
  with single `claim AI-001`.
- **Recommended workflow step 4** — removed manual `git add/commit` after `review`;
  added note about auto-commit and `--no-commit`.
- **Example executor prompt** — replaced "git worktree add + move in_progress" with
  `claim AI-001`.

### `.ai-workflow/README.md`

- **Quick start** — added branch-first task branch creation steps between `create` and
  `approve`: `git checkout -b ai/AI-001-example-task` → `git add` → `git commit` →
  `git checkout main`.

### Files NOT changed

- `AGENTS.md` — already uses `list-branches` and does not show stale guidance.
- `CLAUDE.md` — already uses `list-branches`; executor instructions are current.

## Install paths covered

| Path | Where documented |
|------|-----------------|
| New/empty repository | README.md § "New repository" |
| Existing repository | README.md § "Existing repository" |
| Upgrade | README.md § "Upgrade path" + "What to commit after installation" |
| Post-install verification | README.md § "Post-install verification checklist" |
| What to commit | README.md § "What to commit after installation" (new) |
| Config decisions | README.md § "Configuration checklist" (new) |
| Ownership model | README.md § "Ownership model" |
| Merge snippets for AGENTS.md, CLAUDE.md | `.ai-workflow/README.md` |

## Assumptions

- `board.md` is generated/local and must not be committed; this is documented explicitly.
- The configuration checklist covers every key that installers might need to customize;
  no additional config keys need documentation here.
- The `review` command's `--no-commit` flag is documented inline; no separate section needed.

## Known risks

- No CLI feature gaps were discovered during documentation work.
