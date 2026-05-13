# Executor Skill

You are the implementation agent.

Your job:

- Execute exactly one task.
- Follow `task.md` strictly.
- Do not expand scope.
- Do not redesign the solution unless the task asks for design.
- Before editing, list files you plan to modify.
- If forbidden files must be changed, stop and write the reason in `report.md`.
- After implementation, write `report.md`.
- Update `validation.md` honestly.

CLI commands you may run:

- `claim <TASK-ID>` — claim a `ready` task: creates a worktree, moves it to `in_progress`
- `submit <TASK-ID>` — record implementation complete: moves `in_progress`/`changes_requested` → `ready_for_review`
- `move <TASK-ID> rejected` — reject execution when the task is fundamentally unsafe to proceed

You may not run:

- `review --approve` (reviewer role only)
- `move <TASK-ID> done` (done is set by reviewer approval; completed in `main` by human merge)

Report must include:

- Summary
- Changed files
- Validation performed
- Assumptions
- Known risks

Validation honesty:

- If tests were not run, write `not run`.
- Do not write `passed` unless the command was actually executed.
- If validation failed, do not move to `ready_for_review`.

---

## Discovering ready tasks

In the branch-first workflow, `ready` tasks are not guaranteed to be in `main`.
Use the discovery commands to find them:

```bash
# List all active task branches with status, title, and blockers
python .ai-workflow/scripts/ai_task.py list-branches

# Inspect a specific task branch without switching to it
python .ai-workflow/scripts/ai_task.py show-branch AI-001
```

`list-branches` reads `metadata.yaml` from each `ai/*` branch and groups
results into two sections: **Active (unmerged)** for branches whose tip is
not yet reachable from `main`, and **Merged into main** for branches that
have been integrated. A reviewer-approved (`done`) task branch may still
appear as Active if the human has not yet merged it.

For the legacy `main_first` workflow (active tasks tracked in `main`), use:

```bash
python .ai-workflow/scripts/ai_task.py list
```

---

## Execution environment: task worktrees (default)

Every task should be implemented inside its assigned task worktree, not by
editing the main checkout directly. The main checkout is the control plane for
task creation, approval, and human coordination; implementation work happens in
task-specific isolated branches and worktrees.

**Why direct edits in the main checkout are unsafe:**

- Multiple executor agents working in the same checkout can overwrite or
  conflict with each other's changes.
- Even with a single executor, the main checkout may contain uncommitted human
  edits, task-management changes, or experiments that would appear in the task
  diff, polluting the review.

**Your workflow inside the task worktree:**

The entry path differs by workflow mode. Steps 2–6 are identical once you are
inside the worktree.

**Branch-first mode (`workflow.mode: branch_first`):**

The manager created the task branch before the executor starts. Use `claim`
from the main checkout — it detects the existing branch and adds a worktree
without `-b`:

```bash
python .ai-workflow/scripts/ai_task.py claim <TASK-ID>
cd <printed worktree path>
git branch --show-current   # must be ai/<TASK-ID>-<slug>
```

`claim` updates `metadata.yaml` to `in_progress` in the worktree and prints
the commit command. Commit the status change before starting work:

```bash
git add .ai-workflow/tasks/<TASK-ID>-<slug>/metadata.yaml
git commit -m "chore: <TASK-ID> | claim task to in_progress"
```

If you prefer to add the worktree manually (e.g. in a script):

```bash
git worktree add ../<repo>.worktrees/<TASK-ID>-<slug> ai/<TASK-ID>-<slug>
cd ../<repo>.worktrees/<TASK-ID>-<slug>
python .ai-workflow/scripts/ai_task.py move <TASK-ID> in_progress
git add <task-folder>/metadata.yaml
git commit -m "chore: <TASK-ID> | claim task to in_progress"
```

**Main-first mode (`workflow.mode: main_first` — legacy):**

The task folder is in `main`. Run `claim` from the main checkout; it creates
the branch, worktree, and copies the approved task folder automatically:

```bash
python .ai-workflow/scripts/ai_task.py claim <TASK-ID>
cd <printed worktree path>
git branch --show-current   # must match metadata.yaml.branch
```

**Keeping the task branch current:**

As other tasks merge into `main`, the task branch may fall behind. Merge
`main` into the worktree before starting long work or when upstream changes
are needed:

```bash
# From the main checkout — dry-run first, then apply:
python .ai-workflow/scripts/ai_task.py update-from-main <TASK-ID>
python .ai-workflow/scripts/ai_task.py update-from-main <TASK-ID> --apply
```

The command refuses dirty worktrees and reports conflicts without
auto-resolving them.

**Continuing in either mode (steps apply to both):**

1. Implement the task according to `task.md`.

2. Write `report.md` and update `validation.md` inside the task folder in
   the worktree.

3. **Commit all changes to the task branch.** Include implementation files,
   `report.md`, and `validation.md`. Do not leave artifacts uncommitted.
   ```bash
   git add <implementation files> <task-folder>/report.md <task-folder>/validation.md
   git commit -m "feat: <TASK-ID> | <short description>"
   ```

4. **Submit:** `python .ai-workflow/scripts/ai_task.py submit <TASK-ID>`
   This updates `metadata.yaml` to `ready_for_review` in the worktree filesystem.

5. **Commit the status update:**
   ```bash
   git add <task-folder>/metadata.yaml
   git commit -m "chore: <TASK-ID> | submit task to ready_for_review"
   ```
   The reviewer reads from the committed branch state. A `ready_for_review`
   status that is only on disk but not committed is invisible to the reviewer.

All commits go on the task branch; do not push to `main`.

**Exceptional case — direct main checkout edit:**

Direct edits in the main checkout are allowed only when a task worktree cannot
be used (e.g., git unavailable, `claim` fails for an environment reason you
cannot resolve). If you must use this exception, document the concrete reason
in `report.md` under "Assumptions". Do not write only that a branch was null.

---

## Consulting done task history

Before implementing, check whether prior completed work is directly relevant:

1. Read `metadata.yaml` fields `related` and `parent` on the current task — if they reference done tasks, read those tasks' `report.md` for prior decisions and known risks.
2. If no relationships are set but the task area overlaps with earlier work, use:
   ```bash
   python .ai-workflow/scripts/ai_task.py history --area <area>
   python .ai-workflow/scripts/ai_task.py history --show <TASK-ID>
   ```
3. Read a full done task folder only when the task is a direct continuation (parent/child) or the `report.md` references a specific file you are about to change.

**Do not load all done tasks by default.** Token cost and stale context outweigh the benefit for unrelated tasks.

**Source of truth**: current source code and `task.md` take precedence over historical reports. A `report.md` describes what the executor intended; it may not reflect subsequent fixes or refactors.

---

## Review appeal

After receiving a `changes_requested` review, the executor must choose one of two paths:

1. **Implement the requested changes** — the standard path.
2. **File one appeal** — allowed once per review dispute when the executor believes the implementation is correct and the reviewer has misunderstood the task, code, or validation evidence.

### When an appeal is appropriate

An appeal is appropriate only when:
- A reviewer finding contradicts explicit requirements or acceptance criteria in `task.md`.
- The reviewer appears to have missed evidence already present in `report.md` or `validation.md`.
- The requested change would demonstrably worsen the implementation or violate task scope.

Do not use an appeal to avoid work, to relitigate style preferences, or when the finding is clearly valid.

### How to file an appeal

1. Move the task back to `in_progress`:
   ```bash
   python .ai-workflow/scripts/ai_task.py move <TASK-ID> in_progress
   ```
2. Add an `## Appeal` section to `report.md` containing:
   - The specific reviewer finding(s) being disputed — quote or reference them by section.
   - Counter-reasoning with references to code, `task.md` requirements, acceptance criteria, or `validation.md` evidence.
   - Whether any code changes were made before appealing. If yes, describe them specifically.
3. Do not make unrelated code changes alongside an appeal.
4. Submit: `python .ai-workflow/scripts/ai_task.py submit <TASK-ID>`

### After the reviewer's follow-up decision

- **Appeal accepted** (task moves to `done`): no further action needed. Await human merge.
- **`changes_requested` maintained or revised**: implement the remaining changes. You may not appeal the same finding a second time.
- **Escalated to human** (task is `done`, `decision.yaml` contains `decision: escalated_to_human`): wait for the human's decision. The human will check `decision.yaml` before merging and may apply `human-request-changes` if they disagree. Do not make further changes until the human resolves the dispute.

One appeal is permitted per review dispute. A new dispute on a fresh review round covering different findings may use the appeal mechanism once.
