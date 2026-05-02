# Portable AI Task Protocol

A lightweight, repository-local task protocol for working with AI coding agents.

The goal is not to replace Jira, GitHub Issues, Trello, or Linear. The goal is to create a portable execution layer inside a code repository:

```text
task contract → implementation report → review decision → validation → done
```

The system is file-based, git-friendly, and designed for workflows where one AI agent prepares/reviews tasks and another AI agent implements them.

Example role split:

```text
Codex       → manager / reviewer
Claude Code → executor
Human       → validator
Human       → final owner
```

## Core idea

Each task is a folder.

The folder moves between status directories:

```text
.ai-workflow/tasks/draft/
.ai-workflow/tasks/ready/
.ai-workflow/tasks/in_progress/
.ai-workflow/tasks/ready_for_review/
.ai-workflow/tasks/changes_requested/
.ai-workflow/tasks/ready_for_human/
.ai-workflow/tasks/done/
.ai-workflow/tasks/rejected/
```

A task folder contains its own contract and artifacts:

```text
AI-001-example-task/
  metadata.yaml
  task.md
  report.md
  review.md
  decision.yaml
  validation.md
```

The task status is determined by its directory. `metadata.yaml` also stores the status so the CLI can validate consistency.

`board.md` is generated from the current task folders. It should not be edited manually.

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
| `.ai-workflow/board.md` | Generated | Never touched |
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
python .ai-workflow/scripts/ai_task.py move AI-001 in_progress
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
python .ai-workflow/scripts/ai_task.py create "Add reward preview"            # AI-010
python .ai-workflow/scripts/ai_task.py create "Reward preview: service"       # AI-011
python .ai-workflow/scripts/ai_task.py create "Reward preview: UI binding"    # AI-012
python .ai-workflow/scripts/ai_task.py link AI-011 parent AI-010
python .ai-workflow/scripts/ai_task.py link AI-012 parent AI-010
```

Blocking example — UI binding cannot start until the service ships:

```bash
python .ai-workflow/scripts/ai_task.py link AI-012 blocked-by AI-011
```

`validate` will fail with a clear message if a relationship references a missing task id or if `parent`/`children` or `blocks`/`blocked_by` are not reciprocal. `board` and `list` show `Parent` and `Blocked By` columns so blocked tasks are easy to spot.

## Status lifecycle

Default allowed transitions:

```text
draft → ready
ready → in_progress
in_progress → ready_for_review
ready_for_review → changes_requested
changes_requested → in_progress
ready_for_review → ready_for_human
ready_for_human → done
any status → rejected
```

Executor agents may usually move:

```text
ready → in_progress
in_progress → ready_for_review
changes_requested → in_progress
```

Reviewer agents may usually move:

```text
ready_for_review → changes_requested
ready_for_review → ready_for_human
```

Only a human should move:

```text
draft → ready
ready_for_human → done
```

The executor should not mark tasks as `done`.

## Recommended workflow

### 1. Manager prepares task

Codex or another manager agent creates or updates a task folder.

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

Claude Code or another executor agent reads:

```text
.ai-workflow/skills/executor.md
.ai-workflow/tasks/ready/<task-id>/task.md
```

Then it implements the task and writes:

```text
report.md
validation.md
```

After implementation it moves the task to:

```text
ready_for_review
```

### 4. Reviewer checks result

Codex or another reviewer agent reads:

```text
task.md
report.md
git diff
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

If approved, task moves to:

```text
ready_for_human
```

If changes are needed, task moves to:

```text
changes_requested
```

### 5. Human validates

A human runs the final checks.

If everything is accepted:

```text
ready_for_human → done
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

Generated board. Do not edit manually.

### `.ai-workflow/tasks/<status>/<task>/metadata.yaml`

Machine-readable task metadata, including relationship fields (`parent`, `children`, `blocks`, `blocked_by`, `related`).

### `.ai-workflow/tasks/<status>/<task>/task.md`

Task contract. This is the main source of truth for an AI executor.

### `.ai-workflow/tasks/<status>/<task>/report.md`

Executor report.

### `.ai-workflow/tasks/<status>/<task>/review.md`

Reviewer output.

### `.ai-workflow/tasks/<status>/<task>/decision.yaml`

Machine-readable review decision.

### `.ai-workflow/tasks/<status>/<task>/validation.md`

Manual or automated validation result.

### `.ai-workflow/skills/`

Role instructions for AI agents.

### `.claude/commands/`

Optional Claude Code slash commands.

## Example Codex manager prompt

```text
Read AGENTS.md and .ai-workflow/skills/manager.md.

Create a new task for:
"Add RewardPreviewService".

Use the Unity profile.
Keep the task small.
Do not implement code.
Fill task.md and metadata.yaml.
Leave the task in draft.
Do not move the task to ready — report that human approval is needed before execution.
```

## Example Claude executor prompt

```text
Read CLAUDE.md.
Execute task AI-001.

Rules:
- Follow task.md exactly.
- Do not expand scope.
- Before editing, list planned files.
- Do not modify forbidden Unity files unless task.md explicitly allows it.
- Write report.md and validation.md.
- Move the task to ready_for_review when finished.
```

## Example Codex reviewer prompt

```text
Read AGENTS.md and .ai-workflow/skills/reviewer.md.

Review task AI-001.

Inputs:
- task.md
- report.md
- git diff
- validation.md

Return a decision:
- approve
- changes_requested
- reject

Write review.md and decision.yaml.
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
