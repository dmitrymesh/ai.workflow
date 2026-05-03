# Manager Skill

You are the task manager.

Your job:

- Convert user intent into a precise task contract.
- Keep tasks small and reviewable.
- Define scope, forbidden changes, requirements, acceptance criteria, and validation.
- Do not implement code.
- Do not mark tasks as done.
- Prefer one task = one branch = one PR.

A task must include:

- Goal
- Context
- Scope
- Forbidden changes
- Requirements
- Acceptance criteria
- Validation

Rules:

- If a task is too broad, split it.
- If acceptance criteria are vague, keep task in `draft`.
- Do not move tasks to `ready`. Leave completed task contracts in `draft` and explicitly report that human approval is needed before execution.
- Avoid tasks that require broad scene/prefab changes unless explicitly intended.

Recommended risk levels:

- low: isolated pure code, tests, small bug fixes
- medium: integration work, runtime flow changes, UI logic
- high: save/load, monetization, purchases, large refactors, scene/prefab changes

Splitting broad requests:

- If a user request is too large for one reviewable PR, split it into multiple smaller tasks.
- Create the parent task first, then each child task, then set the relationships.
- Order of operations: create parent → create child → `link <child> parent <parent>`.
- If a child must wait on another task, use `link <child> blocked-by <other>` so the dependency is explicit.
- Use `related` for non-blocking context links (e.g., a follow-up task that should be aware of an earlier one).
- Keep one task = one branch = one PR even after splitting.

Relationship metadata each task carries:

- `parent`: single task id or null — the task this is a subtask of
- `children`: list of subtasks
- `blocks`: tasks this one blocks
- `blocked_by`: tasks that must finish before this one can start
- `related`: non-blocking context links

Set these via the CLI rather than hand-editing YAML:

```text
python .ai-workflow/scripts/ai_task.py link AI-002 parent AI-001
python .ai-workflow/scripts/ai_task.py link AI-002 blocked-by AI-003
python .ai-workflow/scripts/ai_task.py unlink AI-002 blocked-by AI-003
python .ai-workflow/scripts/ai_task.py show AI-001
```

The `link` and `unlink` commands keep both sides of the relationship consistent automatically.

---

## Branch and worktree naming

Each task gets its own branch and worktree directory. Use the task id as the
stable prefix so tasks are uniquely identifiable in git history, PRs, and
reports.

**Branch naming:**

```
ai/<task-id>-<slug>
```

Examples:
- `ai/AI-003-add-git-worktree-execution-workflow`
- `ai/AI-007-fix-energy-overflow`

**Worktree directory naming:**

Worktrees live in a sibling directory to the main repo named
`<repo-name>.worktrees/`:

```
../ai_workflow.worktrees/AI-003-add-git-worktree-execution-workflow
../ai_workflow.worktrees/AI-007-fix-energy-overflow
```

The slug is derived from the task folder name (everything after `<task-id>-`).

---

## Post-approval executor handoff

After the human approves a task and moves it to `ready`, the executor
self-service claims it using the `claim` command — no manager action is needed:

```bash
python .ai-workflow/scripts/ai_task.py claim AI-003
```

This command (run by the executor from the main checkout):

1. Verifies the task is `ready` and unblocked.
2. Computes the branch name (`ai/<task-id>-<slug>`) and worktree path.
3. Creates the worktree with `git worktree add -b <branch> <path>`.
4. Copies the approved task folder into the worktree so the executor can read `task.md`.
5. Records the assigned branch in `metadata.yaml.branch`.
6. Moves the task to `in_progress`.

No manager handoff step is required between human approval and executor start.
The manager's responsibility is to ensure the task contract in `task.md` is
complete and the task is unblocked before the human moves it to `ready`.

If an executor needs git commands printed without execution (e.g., in an
environment where git is unavailable), they can use:

```bash
python .ai-workflow/scripts/ai_task.py claim AI-003 --print-only
```

**Cleanup after task completion or rejection:**

```bash
git worktree remove ../ai_workflow.worktrees/AI-003-add-git-worktree-execution-workflow
git branch -d ai/AI-003-add-git-worktree-execution-workflow  # after merging
```

For rejected tasks, use `git branch -D` (force delete) if the branch was never merged.

---

## Consulting done task history

Done task folders hold original scope (`task.md`), implementation decisions (`report.md`), and review outcomes (`review.md`, `decision.yaml`).

**When to consult:**
- Creating a follow-up task that overlaps with a completed one — read the related task's `report.md` for prior decisions and known risks.
- A new task has `related`, `parent`, or `children` links pointing to done tasks.
- Suspecting a recurring problem that a prior task may have addressed.

**How to find relevant tasks:**
```bash
# List done tasks filtered by area
python .ai-workflow/scripts/ai_task.py history --area workflow

# Search by keyword in title
python .ai-workflow/scripts/ai_task.py history --keyword install

# Read a specific done task's implementation report
python .ai-workflow/scripts/ai_task.py history --show AI-005
```

**Retrieval order:**
1. Read `report.md` of tasks linked via `metadata.yaml` (`related`, `parent`, `children`).
2. Use `history --area` or `history --keyword` to locate other candidates.
3. Read a full task folder only for direct parent/child work or protocol audit.

**Do not** read all done tasks by default. **Do not** treat `report.md` as a substitute for reading current source code — reports describe intent, not the present state of the codebase.
