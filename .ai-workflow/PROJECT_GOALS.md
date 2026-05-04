# Project Goals

This protocol exists to support repeatable, low-overhead AI workflows across
many small Unity pet projects.

## Goals

- Make multi-agent AI workflow portable between projects without rewriting
  agent instructions each time.
- Keep Claude Code focused on execution work, while Codex handles task
  management and review to reduce expensive execution-model context usage.
- Improve task quality by separating planning, implementation, review, and
  human validation into explicit roles and artifacts.
- Move toward higher automation where a human can describe intent to the
  manager, review/approve the resulting task or PR, and then inspect the result
  in the game.
- Preserve project history in a token-efficient local format so agents can
  retrieve relevant past task context without loading all chat history or using
  external integrations.
- Keep the protocol useful without mandatory SaaS, dashboards, databases,
  GitHub/Linear/Jira integration, or a single vendor-specific agent runtime.

## Product Direction

The intended product shape is a minimal, git-native task protocol, not a full
agent orchestration platform.

Prefer building:

- portable `.ai-workflow/` templates;
- strict manager, executor, reviewer, and human-validation role boundaries;
- Unity-specific guardrails for scenes, prefabs, assets, packages, and
  serialized data;
- branch/worktree based task isolation;
- concise task history through `task.md`, `report.md`, `review.md`,
  `decision.yaml`, and `validation.md`;
- small CLI commands for create, discover/list, claim, submit, review, validate,
  board, and history;
- optional integration modes for local merge or hosted pull requests.

Avoid building by default:

- a dashboard-first product;
- a central server or database;
- a replacement for GitHub, Linear, Jira, or CI;
- a universal multi-agent framework;
- automatic infinite agent loops;
- broad automation that removes human approval for task contracts or final game
  validation.

## Decision Heuristics

- If a feature reduces repeated setup across Unity pet projects, it is likely
  aligned.
- If a feature reduces executor context usage by improving task contracts or
  targeted history retrieval, it is likely aligned.
- If a feature makes task state understandable from git and local files, it is
  likely aligned.
- If a feature requires external infrastructure before the protocol is useful,
  it should be optional or deferred.
- If a feature increases automation but weakens human approval, review, or
  validation boundaries, it should be rejected or redesigned.
