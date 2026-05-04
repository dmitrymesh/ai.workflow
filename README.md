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

Move a task:

```bash
python .ai-workflow/scripts/ai_task.py move AI-001 ready
```

Claim a ready task (executor self-service — creates worktree, moves to `in_progress`):

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

List tasks:

```bash
python .ai-workflow/scripts/ai_task.py list
```

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
draft → ready
ready → in_progress          (via claim)
in_progress → ready_for_review   (via submit)
ready_for_review → changes_requested
ready_for_review → done          (via review --approve)
changes_requested → ready_for_review  (via submit after fixes)
any status → rejected
```

Executor agents move:

```text
ready → in_progress          (claim)
in_progress → ready_for_review   (submit)
changes_requested → in_progress  (re-claim or manual move, then submit)
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

### 2. Human approves task contract

A human reviews `task.md` and, if the scope, requirements, acceptance criteria, and validation plan are acceptable, moves the task to `ready`:

```bash
python .ai-workflow/scripts/ai_task.py move AI-001 ready
```

Only a human should perform this step.

### 3. Executor implements

The executor agent (configured in `.ai-workflow/config.yaml` under `agents.executor` — default: Claude Code) reads `.ai-workflow/skills/executor.md` and the task folder, then claims the task from the main checkout:

```bash
python .ai-workflow/scripts/ai_task.py claim AI-001
```

`claim` creates an isolated git worktree on a task branch (`ai/<task-id>-<slug>`),
copies the approved task folder into the worktree, and moves the task to `in_progress`.
The executor implements the task inside the worktree, writes `report.md` and
`validation.md`, then submits:

```bash
python .ai-workflow/scripts/ai_task.py submit AI-001
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

Then it writes:

```text
review.md
decision.yaml
```

Decision must be one of:

```text
approve
changes_requested
reject
```

If approved, task moves to `done`:

```bash
python .ai-workflow/scripts/ai_task.py review AI-001 --approve
```

If changes are needed:

```bash
python .ai-workflow/scripts/ai_task.py review AI-001 --changes-requested
```

### 5. Human merges

Once a task is `done`, a human reviews the task branch and merges it to `main`. After merge, clean up:

```bash
git worktree remove ../<repo>.worktrees/AI-001-<slug>
git branch -d ai/AI-001-<slug>
```

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
Execute task AI-001.

Rules:
- Follow task.md exactly.
- Do not expand scope.
- Before editing, list planned files.
- Do not modify forbidden Unity files unless task.md explicitly allows it.
- Run: python .ai-workflow/scripts/ai_task.py claim AI-001
- Work inside the printed worktree path. Verify the branch matches metadata.yaml.branch.
- Write report.md and validation.md.
- Run: python .ai-workflow/scripts/ai_task.py submit AI-001
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
