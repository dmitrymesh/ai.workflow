# Execution Report: AI-018

## Summary

Audit of the `.ai-workflow` protocol and `ai_task.py` CLI after AI-009 through
AI-017. No code changes were made. Output is a workflow review, prioritized
findings, and a concrete refactor backlog.

## Changed files

- None (audit task; report.md and validation.md only)

## Validation performed

See `validation.md` for exact commands and results.

---

## Workflow review

**Verdict: conditionally ready for real Unity project use.**

The protocol satisfies the project goals in `PROJECT_GOALS.md`: it is
git-native, local-first, role-separated, and portable. The task lifecycle
artifacts (task.md / report.md / review.md / decision.yaml / validation.md)
are coherent. Branch isolation and the relationship cascade (AI-016) work
correctly. The `validate` command passes cleanly.

What makes it only *conditionally* ready:

1. The `claim` CLI command is broken for branch-first mode — it creates a new
   branch with `-b` instead of adding a worktree to the already-existing task
   branch. Executors currently work around this by running `git worktree add`
   manually (following executor.md), but the CLI itself is wrong.
2. Human approval from the main checkout requires entering the task branch
   directly. There is no `approve` command; the human must `cd` into the task
   worktree, run `move <TASK-ID> ready`, commit, and exit. This friction is high
   enough to risk skipping the approval commit.
3. The `review` command writes review artifacts to disk but does not commit
   them. The reviewer must manually `git add` and `git commit` after running
   `review --approve`. This is documented in reviewer.md but not enforced by
   the CLI, creating a real risk of uncommitted reviewer artifacts.

All three gaps are small, targeted fixes — none requires a broad rewrite.

---

## Findings

### HIGH — claim is broken in branch-first mode

**File:** `.ai-workflow/scripts/_worktree.py`, `claim_task()`

`claim_task` runs `git worktree add -b <branch> <path>`, which creates a *new*
branch. In branch-first mode the task branch already exists. Running `claim`
produces a git error: "A branch named 'ai/AI-NNN-slug' already exists." The
executor must fall back to the manual `git worktree add <path> <existing-branch>`
workflow documented in executor.md.

**Fix:** detect whether the branch already exists (e.g., `git rev-parse --verify`)
and use `git worktree add <path> <branch>` (no `-b`) when it does. When the
branch does not exist (main-first flow), keep the current `-b` creation path.

---

### HIGH — review command does not commit artifacts

**Files:** `.ai-workflow/scripts/_tasks.py`, `review_task()`; `reviewer.md`

`review_task` writes `metadata.yaml` to disk and regenerates `board.md` but
does not `git add` or `git commit` anything. The reviewer.md skill documents the
required manual commit, but nothing stops a reviewer from skipping it. In the
branch-first model an uncommitted review means the executor's worktree re-entry
finds no `review.md` and the branch cannot be cleanly merged.

**Fix:** after writing the review artifacts, call `git add <task-folder>` and
`git commit` from within `review_task` (or a new `_commit_review_artifacts`
helper). Allow `--no-commit` flag for environments where git is unavailable.

---

### MEDIUM — no `approve <TASK-ID>` command for human approval from main

**Files:** `manager.md`, `executor.md`, `README.md`

In branch-first mode, the human approves a task by entering its branch/worktree,
running `move <TASK-ID> ready`, and committing. The README quick-start shows
`move AI-001 ready` as a one-liner, which works in main-first mode but requires
the human to already be on the task branch in branch-first mode. There is no
command that finds the task branch from the main checkout and performs the
approval commit there.

**Recommendation:** add `approve <TASK-ID>` (or `move <TASK-ID> ready --commit`)
that: (1) locates the task branch via `list-branches`-style discovery, (2) runs
`git worktree add --detach` or uses `git read-tree` to update the branch, or
(3) simplest: prints the exact git commands for a human to copy-paste. A
full auto-commit implementation is the ideal; a `--print-only` first step is
acceptable if the full auto is out of scope.

---

### MEDIUM — `list` unusable in branch-first discovery; quick-start misleads

**Files:** `README.md` quick-start section; `_board.py`

The `list` command scans `tasks_root()` — the current branch's
`.ai-workflow/tasks/` directory. In branch-first mode, tasks on separate
unmerged branches are invisible to `list`. The README quick-start does not
advertise `list` as the discovery command (it shows `create`, `move ready`,
`claim`, `submit`, `board`), but the quick-start description lacks an explicit
pointer to `list-branches` as the branch-first discovery path. Running `list`
from a branch-first project shows only tasks merged into the current branch,
not the full active backlog.

**Fix:** add `list-branches` to the README quick-start as the branch-first
discovery command. Optionally have `list` print a warning when
`workflow.mode = branch_first` and `list-branches` would return more results.

---

### LOW — `_discovery.py` duplicates the YAML parser from `_core.py`

**Files:** `_discovery.py` (`_parse_yaml_string`), `_core.py` (`parse_simple_yaml`)

Both functions implement the same minimal YAML parser. `_discovery.py` parses
from a string while `_core.py` parses from a `Path`. The duplication is a
maintenance liability: any YAML format extension (e.g., supporting `area:` as
an inline list) must be applied in two places.

**Fix:** extend `parse_simple_yaml` to accept `str | Path` (or add a thin
`parse_simple_yaml_string` wrapper in `_core.py`), then import it in
`_discovery.py`.

---

### LOW — stale worktrees for merged tasks

**Context:** `git worktree list`

Eight worktrees exist for tasks AI-008 through AI-015 that are already merged
(per `list-branches`). These add noise to `git worktree list`, consume inodes,
and can confuse tools that enumerate worktrees. There is no automated or
documented cleanup step in the post-merge workflow, other than the one-liner in
the README cleanup section.

**Fix:** add a `cleanup-merged-worktrees` (or `prune-worktrees`) command that
lists all worktrees whose branches are merged into `main` and prompts the human
to remove them. Or add a post-merge checklist item to the integration section
of the README.

---

### INFO — AI-017 fix not visible in AI-018 worktree

The `show` command in this worktree still prints `status: tasks` (the pre-fix
behavior). This is because the AI-018 branch was created before AI-017 was
merged to `main`. This is expected behavior in the branch-first model — task
branches do not automatically receive fixes from sibling branches. Executors
working on long-lived branches should rebase onto `main` after important fixes
land. Not a protocol defect; noted here as a usability observation.

---

### INFO — reviewer.md commit discipline is documented but not enforced

The reviewer.md skill and README both document the required post-review commit.
This is recorded here as a known gap (matched by the HIGH finding above) and
is not a separate finding, but confirms that the CLI must enforce this rather
than relying on documentation alone.

---

## AI-017 and the refactor start

**AI-017 should be merged to `main` before any broad refactor starts.** It fixes
a concrete command-trust issue (`show` printing `status: tasks`). Until it is
merged, all task branches created after the AI-017 branch point will have the
correct code; branches created before (like AI-018) will see the old bug. The
refactor tasks below should start from a `main` that includes AI-017.

---

## Worktree naming convention check

All current worktrees follow the documented convention:
`../ai_workflow.worktrees/<TASK-ID>-<slug>`.

| Worktree | Convention? |
|----------|-------------|
| `AI-008-add-executor-review-appeal-step` | ✓ |
| `AI-009-simplify-git-workflow-task-status-management` | ✓ |
| `AI-010-update-root-readme-for-flat-task-workflow` | ✓ |
| `AI-012-design-branch-first-task-workflow-contract` | ✓ |
| `AI-013-implement-branch-task-discovery-commands` | ✓ |
| `AI-014-update-agent-docs-for-branch-first-workflow` | ✓ |
| `AI-015-document-worktree-execution-rules-for-task-chains` | ✓ |
| `AI-018-audit-workflow-and-plan-cli-refactor` | ✓ |

No exceptions. The `_worktree.py` `_branch_and_worktree_path` helper computes
the correct convention-compliant path automatically for `claim` (main-first).
In branch-first mode the executor opens the worktree manually; manager.md and
executor.md both specify the correct path format. The main gap is that a
manual typo could produce a non-convention path, but no such deviation was
observed.

The gap that could cause future tasks to be created outside the standard
location: in branch-first mode, `claim` is broken and executors do
`git worktree add` manually. An executor who does not read manager.md carefully
could place the worktree anywhere. After fixing `claim` (AI-019), the CLI will
enforce the correct path automatically.

---

## Refactor plan

Tasks are listed in recommended execution order. Each is sized for one
reviewable PR.

### AI-019 — Fix `claim` for branch-first mode
- **Scope:** `_worktree.py`, `claim_task()`. Detect existing branch; use
  `git worktree add <path> <branch>` (no `-b`) when branch exists.
- **Risk:** low — narrow change, isolated to claim path
- **Validation:** `claim` on an existing branch succeeds; `claim` on a new task
  (main-first) still creates the branch; regression test for both paths

### AI-020 — Auto-commit review artifacts in `review_task`
- **Scope:** `_tasks.py`, `review_task()`. After writing artifacts, run
  `git add <task-folder> && git commit`. Add `--no-commit` escape hatch.
- **Risk:** medium — alters reviewer workflow; must handle edge cases (dirty
  working tree, git unavailable)
- **Validation:** after `review --approve`, `git log --oneline -1` shows the
  review commit; `--no-commit` leaves files unstaged

### AI-021 — Add `approve <TASK-ID>` command
- **Scope:** new command in `ai_task.py` + `_tasks.py` (or `_worktree.py`).
  From the main checkout: find the task branch, run `move <TASK-ID> ready`,
  commit the metadata change to the task branch. `--print-only` to print git
  commands without running them.
- **Risk:** low — new command, does not change existing commands
- **Validation:** `approve AI-NNN --print-only` prints correct commands;
  `approve AI-NNN` commits `ready` status to the task branch

### AI-022 — Deduplicate YAML parser (`_discovery.py` vs `_core.py`)
- **Scope:** `_core.py` (add string-input variant); `_discovery.py` (remove
  local `_parse_yaml_string`, import from `_core`).
- **Risk:** low — pure refactor, no behavior change; covered by existing tests
- **Validation:** all `test_cascade.py` and `test_show.py` tests pass;
  `list-branches` and `show-branch` output unchanged

### AI-023 — Add worktree pruning helper
- **Scope:** new `prune-worktrees` command (or README checklist update) that
  identifies worktrees whose branches are merged into main.
- **Risk:** low — new command or doc-only change
- **Validation:** `prune-worktrees` lists AI-008 through AI-015 worktrees
  as candidates for removal; does not remove anything without `--apply`

---

## Assumptions

- This audit treats the project as operating in branch-first mode.
  `config.yaml` confirms `workflow.mode: branch_first`. All observations
  are based on actual observed behavior.
- AI-017 fix was confirmed merged to `main` via `list-branches` output but
  not yet visible in this AI-018 worktree.

## Known risks

- None introduced by this task (no code changes).
