# Portable AI Task Protocol

A lightweight, repository-local task protocol for working with AI coding agents.

The goal is not to replace Jira, GitHub Issues, Trello, or Linear. The goal is to create a portable execution layer inside a code repository:

```text
task contract → implementation report → review decision → validation → done
```

The system is file-based, git-friendly, and designed for workflows where one AI agent prepares/reviews tasks and another AI agent implements them.

Example role split (default — configurable in `.ai-workflow/config.yaml`):

```text
Codex       → manager / reviewer
Claude Code → executor
Human       → validator
Human       → final owner
```

Any compatible LLM or agent runtime can fill any role. Edit the `agents:` block in
`.ai-workflow/config.yaml` to change assignments. Run
`python .ai-workflow/scripts/ai_task.py roles` to print the current mapping.

## Core idea

Each task is a stable folder under `.ai-workflow/tasks/`:

```text
.ai-workflow/tasks/<task-id>-<slug>/
```

Task status is stored in `metadata.yaml` — the folder path never changes:

```text
.ai-workflow/tasks/AI-001-example-task/
  metadata.yaml    ← status: draft | ready | in_progress | ready_for_review |
                              changes_requested | done | rejected
  task.md
  report.md
  review.md
  decision.yaml
  validation.md
```

`board.md` is generated from the current task folders and is gitignored — it is a local view cache only. Do not edit it manually.

## Installation into a project

### New repository

For a brand-new git repository with no existing `AGENTS.md`, `CLAUDE.md`, or `.claude/`:

```bash
# Copy all protocol files
python .ai-workflow/scripts/ai_task.py install-plan /path/to/newproject --apply

# Initialise and verify
cd /path/to/newproject
python .ai-workflow/scripts/ai_task.py init --profile generic   # or: --profile unity
python .ai-workflow/scripts/ai_task.py validate
```

All files are created fresh — no merge snippets are needed.

### Existing repository

> **Do not blindly copy files into an existing project.** Projects often already
> have their own `AGENTS.md`, `CLAUDE.md`, `README.md`, or `.claude/` automation.
> Overwriting these silently destroys project-specific context.

Use the safe install workflow instead:

### 1. Preview the install plan

```bash
# From the protocol repo, preview what would happen:
python .ai-workflow/scripts/ai_task.py install-plan /path/to/myproject
```

The plan classifies every file as:

| Marker | Action | Meaning |
|--------|--------|---------|
| `[+]` | `CREATE` | File does not exist in target — safe to create |
| `[~]` | `UPDATE` | Protocol-owned file differs — will overwrite with `--apply` |
| `[!]` | `MERGE-REQUIRED` | File exists and is an integration point — never auto-overwritten |
| `[ ]` | `UNCHANGED` | File already matches source — nothing to do |
| `[-]` | `SKIP` | Project-owned file (`README.md`) — always skipped |

### 2. Apply protocol-owned files

```bash
python .ai-workflow/scripts/ai_task.py install-plan /path/to/myproject --apply
```

`--apply` creates or updates only **protocol-owned** files (`.ai-workflow/`,
new `.claude/commands/` files). It never touches `AGENTS.md`, `CLAUDE.md`,
`README.md`, or existing `.claude/commands/*` files.

### 3. Merge integration points manually

For files flagged `MERGE-REQUIRED`, the install plan prints a merge snippet.
Review the snippet and append the relevant section to your existing file:

- **`AGENTS.md`** — append a section pointing agents to `.ai-workflow/README.md`
  and the role skills
- **`CLAUDE.md`** — append executor rules pointing to `.ai-workflow/skills/executor.md`
- **`.claude/commands/*`** — compare with the protocol version and keep the version
  that matches your workflow

### 4. Initialise and verify

```bash
python .ai-workflow/scripts/ai_task.py init --profile unity   # or generic
python .ai-workflow/scripts/ai_task.py validate
python .ai-workflow/scripts/ai_task.py board
```

### Post-install verification checklist

After installing or upgrading, run these commands to confirm the protocol is functional:

```bash
# 1. Validate workflow state
python .ai-workflow/scripts/ai_task.py validate

# 2. Check role assignments
python .ai-workflow/scripts/ai_task.py roles

# 3. Scan the active task backlog
python .ai-workflow/scripts/ai_task.py list-branches

# 4. Browse done task history
python .ai-workflow/scripts/ai_task.py history

# 5. Confirm CLI help is accessible
python .ai-workflow/scripts/ai_task.py --help
```

If `validate` passes and all commands run without errors, the installation is working correctly.

> **Note on task creation:** In branch-first mode (`workflow.mode: branch_first`),
> `create` puts the task folder in the current checkout but does **not** create the
> task branch. A branch must be created and committed before `approve` will work.
> See the "Recommended workflow" § "Manager prepares task" section below for the
> full procedure, or the "Quick start" in `.ai-workflow/README.md`.

### Upgrade path

If `.ai-workflow/` is already installed:

```bash
# See what changed in protocol-owned files:
python .ai-workflow/scripts/ai_task.py install-plan /path/to/myproject

# Apply protocol updates (existing tasks/ are never touched):
python .ai-workflow/scripts/ai_task.py install-plan /path/to/myproject --apply
```

`tasks/` and `board.md` are **always excluded** from install/upgrade — existing
task data is never deleted or overwritten.

### Ownership model

| Path | Owner | Install behaviour |
|------|-------|-------------------|
| `.ai-workflow/` (excl. `tasks/`, `board.md`) | Protocol | CREATE / UPDATE with `--apply` |
| `.ai-workflow/tasks/` | Project | Never touched |
| `.ai-workflow/board.md` | Generated (untracked) | Never touched |
| `AGENTS.md` | Project (integration) | CREATE if absent; MERGE-REQUIRED if exists |
| `CLAUDE.md` | Project (integration) | CREATE if absent; MERGE-REQUIRED if exists |
| `.claude/commands/*` | Project (integration) | CREATE if absent; MERGE-REQUIRED if exists |
| `README.md` | Project | Always SKIP |

## Basic commands

Create a task:

```bash
python .ai-workflow/scripts/ai_task.py create "Add RewardPreviewService" --risk low --area gameplay,tests
```

Approve a draft task (human step — moves `draft` → `ready` on the task branch):

```bash
python .ai-workflow/scripts/ai_task.py approve AI-001
```

Claim a ready task (executor — creates or opens a worktree, moves to `in_progress`):

```bash
python .ai-workflow/scripts/ai_task.py claim AI-001
```

Submit a completed task for review:

```bash
python .ai-workflow/scripts/ai_task.py submit AI-001
```

Review a submitted task:

```bash
python .ai-workflow/scripts/ai_task.py review AI-001 --approve
python .ai-workflow/scripts/ai_task.py review AI-001 --changes-requested
```

Reopen a `done` task for further changes (human pre-merge veto):

```bash
python .ai-workflow/scripts/ai_task.py human-request-changes AI-001 --feedback "Please address X before merge"
```

Migrate tasks from the legacy status-by-directory layout to the current flat layout:

```bash
python .ai-workflow/scripts/ai_task.py migrate
```

Discover active tasks from task branches — use `list-branches` as your primary backlog view in branch-first mode:

```bash
# All active task branches with status, title, and blockers
python .ai-workflow/scripts/ai_task.py list-branches

# Inspect one task branch without switching to it
python .ai-workflow/scripts/ai_task.py show-branch AI-001
```

List tasks from the current checkout only — useful for viewing completed history or when using the legacy main-first mode; **not** the full backlog view in branch-first mode:

```bash
python .ai-workflow/scripts/ai_task.py list
```

> **`list` vs `list-branches`**: In branch-first mode, active tasks live on their own branches and are not tracked in `main`. `list` reads only from `main` and will show empty draft/ready/in-progress queues. Use `list-branches` to see all active tasks regardless of mode. Use `list` to browse completed history or when `workflow.mode = main_first`.

Generate board:

```bash
python .ai-workflow/scripts/ai_task.py board
```

Validate workflow state:

```bash
python .ai-workflow/scripts/ai_task.py validate
```

Show task path:

```bash
python .ai-workflow/scripts/ai_task.py path AI-001
```

Show task details (including relationships):

```bash
python .ai-workflow/scripts/ai_task.py show AI-001
```

Add or remove a relationship:

```bash
python .ai-workflow/scripts/ai_task.py link   AI-002 parent     AI-001
python .ai-workflow/scripts/ai_task.py link   AI-003 blocked-by AI-001
python .ai-workflow/scripts/ai_task.py unlink AI-003 blocked-by AI-001
python .ai-workflow/scripts/ai_task.py unlink AI-002 parent
```

## Task relationships

Each task records relationships in `metadata.yaml`:

```text
parent       single task id or null
children     list of subtasks
blocks       list of tasks this one blocks
blocked_by   list of tasks that block this one
related      non-blocking context links
```

Use `link` / `unlink` instead of editing YAML by hand — the CLI keeps both sides of every link in sync (`parent` ↔ `children`, `blocks` ↔ `blocked_by`, `related` ↔ `related`).

Parent/child example — split a broad request into a parent and two children:

```bash
python .ai-workflow/scripts/ai_task.py create "Add reward preview"            # AI-020
python .ai-workflow/scripts/ai_task.py create "Reward preview: service"       # AI-021
python .ai-workflow/scripts/ai_task.py create "Reward preview: UI binding"    # AI-022
python .ai-workflow/scripts/ai_task.py link AI-021 parent AI-020
python .ai-workflow/scripts/ai_task.py link AI-022 parent AI-020
```

Blocking example — UI binding cannot start until the service ships:

```bash
python .ai-workflow/scripts/ai_task.py link AI-022 blocked-by AI-021
```

`validate` will fail with a clear message if a relationship references a missing task id or if `parent`/`children` or `blocks`/`blocked_by` are not reciprocal. `board` and `list` show `Parent` and `Blocked By` columns so blocked tasks are easy to spot.

## Status lifecycle

Task status is stored in `metadata.yaml.status`. Allowed statuses and transitions:

```text
draft              → ready, rejected
ready              → in_progress (via claim), rejected
in_progress        → ready_for_review (via submit), rejected
ready_for_review   → changes_requested, done (via review --approve), rejected
changes_requested  → ready_for_review (via submit after fixes), rejected
done               → changes_requested (via human-request-changes)
```

Executor agents move:

```text
ready → in_progress                       (claim)
in_progress → ready_for_review            (submit)
changes_requested → ready_for_review      (submit after addressing review feedback)
```

Reviewer agents move:

```text
ready_for_review → changes_requested   (review --changes-requested)
ready_for_review → done                (review --approve)
```

Only a human should move:

```text
draft → ready
```

The executor must not mark tasks as `done`.

## Recommended workflow

### 1. Manager prepares task

The manager agent (configured in `.ai-workflow/config.yaml` under `agents.manager` — default: Codex) creates or updates a task folder.

The manager should fill:

```text
task.md
metadata.yaml
```

The task must include:

```text
Goal
Context
Scope
Forbidden changes
Requirements
Acceptance criteria
Validation
```

The manager leaves the task in `draft` and reports that human approval is needed. The manager does not move the task to `ready`.

In **branch-first** mode (`workflow.mode: branch_first`), the manager also creates and commits
the task branch before returning to `main`:

```bash
# After creating the task folder, commit it to a dedicated task branch:
python .ai-workflow/scripts/ai_task.py create "My task" --risk low
#    → note the printed task ID (e.g. AI-001) and folder slug

git checkout -b ai/AI-001-<slug>
git add .ai-workflow/tasks/AI-001-<slug>/
git commit -m "draft: AI-001 | My task"
git checkout main
```

The task branch is the source of truth for all active task artifacts; `main` is the control plane.

### 2. Human approves task contract

A human reviews `task.md` and, if the scope, requirements, acceptance criteria, and validation plan are acceptable, approves the task:

```bash
python .ai-workflow/scripts/ai_task.py approve AI-001
```

`approve` moves `draft` → `ready` on the task branch. Only a human should perform this step.

### 3. Executor implements

The executor agent (configured in `.ai-workflow/config.yaml` under `agents.executor` — default: Claude Code) reads `.ai-workflow/skills/executor.md` and discovers ready tasks:

```bash
python .ai-workflow/scripts/ai_task.py list-branches   # branch-first
python .ai-workflow/scripts/ai_task.py list            # or main-first / history
```

Run `claim` from the main checkout:

```bash
python .ai-workflow/scripts/ai_task.py claim AI-001
cd <printed worktree path>
git branch --show-current   # must match metadata.yaml.branch
```

`claim` works in both workflow modes: in **branch-first** mode it opens a worktree on the pre-existing task branch; in **main-first** (legacy) mode it creates the branch and worktree automatically.

The executor implements the task inside the worktree, writes `report.md` and
`validation.md`, then **commits** those artifacts before submitting:

```bash
git add <files> .ai-workflow/tasks/AI-001-slug/report.md .ai-workflow/tasks/AI-001-slug/validation.md
git commit -m "feat: AI-001 | <description>"

python .ai-workflow/scripts/ai_task.py submit AI-001

git add .ai-workflow/tasks/AI-001-slug/metadata.yaml
git commit -m "chore: AI-001 | submit task to ready_for_review"
```

All commits go on the task branch; do not push to `main`.

### 4. Reviewer checks result

The reviewer agent (configured in `.ai-workflow/config.yaml` under `agents.reviewer` — default: Codex) reads:

```text
task.md
report.md
git diff main...ai/<task-id>-<slug>
reviewer.md skill
```

Then it writes `review.md` and `decision.yaml` and runs the review command.
The `review` command **auto-commits** the artifacts to the task branch by default:

```bash
python .ai-workflow/scripts/ai_task.py review AI-001 --approve   # or --changes-requested
```

Add `--no-commit` to write artifacts without committing (useful for local inspection before committing manually).

Decision must be one of: `approve`, `changes_requested`, `reject`.

The auto-commit ensures the executor receives feedback when they re-enter the worktree, and the complete record (contract → implementation → review) travels together to `main`.

### 5. Human merges

Once a task is `done`, a human reviews the task branch and merges it to `main`. After merge, clean up:

```bash
git worktree remove ../<repo>.worktrees/AI-001-<slug>
git branch -d ai/AI-001-<slug>
```

To clean up multiple merged worktrees at once, use `prune-worktrees`:

```bash
# List all worktrees whose branches are already merged into main:
python .ai-workflow/scripts/ai_task.py prune-worktrees

# Remove them (skips dirty worktrees and reports failures):
python .ai-workflow/scripts/ai_task.py prune-worktrees --apply
```

The command never touches the main checkout, active unmerged task worktrees, or
worktrees with uncommitted changes.

## Unity profile

The Unity profile adds guardrails for Unity projects.

Forbidden unless explicitly allowed in `task.md`:

```text
.unity scene changes
.prefab changes
.asset changes
.meta changes
Packages/manifest.json changes
ProjectSettings changes
serialized field renames without migration
save/load format changes
```

Recommended:

```text
Prefer pure C# services
Prefer EditMode tests for logic
Use PlayMode tests only for Unity lifecycle or scene behavior
Keep PRs small
Avoid package changes
Do not rely on arbitrary waits in tests
```

## Files

### `.ai-workflow/config.yaml`

Defines statuses, allowed transitions, profile, agent role mapping, and forbidden file patterns.

### `.ai-workflow/board.md`

Generated board. Do not edit manually. Gitignored — local view only.

### `.ai-workflow/tasks/<task-id>-<slug>/metadata.yaml`

Machine-readable task metadata. `status` field is the source of truth for task state. Also stores relationship fields (`parent`, `children`, `blocks`, `blocked_by`, `related`) and the task branch name.

### `.ai-workflow/tasks/<task-id>-<slug>/task.md`

Task contract. This is the main source of truth for an AI executor.

### `.ai-workflow/tasks/<task-id>-<slug>/report.md`

Executor report.

### `.ai-workflow/tasks/<task-id>-<slug>/review.md`

Reviewer output.

### `.ai-workflow/tasks/<task-id>-<slug>/decision.yaml`

Machine-readable review decision.

### `.ai-workflow/tasks/<task-id>-<slug>/validation.md`

Manual or automated validation result.

### `.ai-workflow/skills/`

Role instructions for AI agents.

### `.claude/commands/`

Optional Claude Code slash commands.

## Example manager prompt (default tool: Codex — adapt using config.yaml)

```text
Read your adapter entrypoint (e.g. AGENTS.md) or .ai-workflow/README.md.
Read .ai-workflow/config.yaml to confirm your role.
Read .ai-workflow/skills/manager.md.

Create a new task for:
"Add RewardPreviewService".

Use the Unity profile.
Keep the task small.
Do not implement code.
Fill task.md and metadata.yaml.
Leave the task in draft.
Do not move the task to ready — report that human approval is needed before execution.
```

## Example executor prompt (default tool: Claude Code — adapt using config.yaml)

```text
Read your adapter entrypoint (e.g. CLAUDE.md) or .ai-workflow/README.md.
Read .ai-workflow/config.yaml to confirm your role.
Read .ai-workflow/skills/executor.md.

Discover ready tasks:
  python .ai-workflow/scripts/ai_task.py list-branches

Execute task AI-001.

Rules:
- Follow task.md exactly.
- Do not expand scope.
- Before editing, list planned files.
- Do not modify forbidden Unity files unless task.md explicitly allows it.
- Run: python .ai-workflow/scripts/ai_task.py claim AI-001
- cd to the printed worktree path. Verify: git branch --show-current must match metadata.yaml.branch.
- Work inside the worktree. Verify the branch matches metadata.yaml.branch.
- Write report.md and validation.md.
- Commit implementation + report.md + validation.md to the task branch.
- Run: python .ai-workflow/scripts/ai_task.py submit AI-001
- Commit the updated metadata.yaml after submit.
```

## Example reviewer prompt (default tool: Codex — adapt using config.yaml)

```text
Read your adapter entrypoint (e.g. AGENTS.md) or .ai-workflow/README.md.
Read .ai-workflow/config.yaml to confirm your role.
Read .ai-workflow/skills/reviewer.md.

Review task AI-001.

Inputs:
- task.md
- report.md
- git diff main...ai/AI-001-<slug>
- validation.md

Return a decision:
- approve
- changes_requested
- reject

Write review.md and decision.yaml.
Run: python .ai-workflow/scripts/ai_task.py review AI-001 --approve
  or python .ai-workflow/scripts/ai_task.py review AI-001 --changes-requested
```

## Design constraints

This project intentionally avoids:

```text
database
backend server
vendor-specific agent protocol
mandatory GitHub/Jira integration
automatic infinite agent loops
```

It is designed as a small portable protocol that can later be connected to local UI, GitHub Issues, Jira, Jenkins, or other automation.
