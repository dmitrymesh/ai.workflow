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

Copy these files into the root of your target repository:

```text
.ai-workflow/
AGENTS.md
CLAUDE.md
.claude/commands/
```

Then run:

```bash
python .ai-workflow/scripts/ai_task.py init --profile unity
python .ai-workflow/scripts/ai_task.py validate
python .ai-workflow/scripts/ai_task.py board
```

For non-Unity projects:

```bash
python .ai-workflow/scripts/ai_task.py init --profile generic
```

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

Only a human validator should move:

```text
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

### 2. Executor implements

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

### 3. Reviewer checks result

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

### 4. Human validates

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

Machine-readable task metadata.

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
Move the task to ready only if acceptance criteria are clear.
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
