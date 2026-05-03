# AI-006: Evaluate done tasks as project memory

## Goal

Evaluate whether completed tasks in `.ai-workflow/tasks/done/` should be used as project memory for future LLM agents, and define a practical policy if the answer is yes.

The output should answer:

- Is `done/` useful as memory?
- How often should agents consult it?
- Which roles benefit from it?
- What should be read: full task folders, summaries, indexes, or only related tasks?
- Is the added context worth the token/cognitive cost?

## Context

Completed task folders contain valuable historical artifacts:

- original task contract (`task.md`)
- executor report (`report.md`)
- review decision (`review.md`, `decision.yaml`)
- validation result (`validation.md`)
- metadata and relationships (`metadata.yaml`)

This could help agents understand why the workflow evolved, avoid repeating previous mistakes, and find prior decisions. But reading all done tasks by default may add stale, irrelevant, or excessive context.

The current protocol already has relationships (`related`, `parent`, `children`, `blocks`, `blocked_by`) and generated board output. These may be better hooks for targeted memory retrieval than blindly reading all completed tasks.

## Scope

Allowed changes:

- `.ai-workflow/README.md`
- root `README.md`
- `.ai-workflow/skills/manager.md`
- `.ai-workflow/skills/executor.md`
- `.ai-workflow/skills/reviewer.md`
- `.ai-workflow/templates/report.md` or `.ai-workflow/templates/review.md` only if summaries need a new convention
- `.ai-workflow/scripts/*` only if adding a small read-only command such as `memory`, `history`, or `done-summary`
- `.ai-workflow/board.md` if regenerated
- `.ai-workflow/tasks/draft/AI-006-evaluate-done-tasks-as-project-memory/*`

Forbidden changes:

- Do not make every agent read every `done/` task by default.
- Do not add embeddings, vector databases, network calls, or non-stdlib dependencies.
- Do not add a server or daemon.
- Do not change status names or lifecycle transitions.
- Do not move, rewrite, compact, or delete existing done task folders.
- Do not mark any task as `done`.

## Requirements

- Evaluate concrete use cases where `done/` history helps:
  - manager creating related/follow-up tasks
  - executor understanding prior implementation decisions
  - reviewer checking repeated issues or previous accepted patterns
  - human auditing protocol evolution
- Evaluate risks/costs:
  - context bloat
  - stale decisions
  - irrelevant history
  - overfitting to old task-specific constraints
  - accidental reliance on reports instead of source code
- Define a recommended retrieval policy. Expected direction:
  - do not read all done tasks by default
  - read done tasks only when they are directly related by `metadata.yaml.related`, parent/child links, shared area, explicit user request, or keyword search
  - prefer summaries/indexes over full task folders for broad orientation
  - full task folders should be read only for closely related work or review/audit
- Decide whether a persistent project memory artifact is worth adding. Possible options:
  - no artifact; use targeted search over done tasks
  - generated `.ai-workflow/memory.md`
  - per-task summary field/section
  - generated done index grouped by area/status/date
- If recommending a memory artifact, define how it is generated, what it includes, and how it avoids becoming stale.
- Update role guidance so agents know when to consult completed tasks and when not to.
- If adding a CLI command, keep it read-only and stdlib-only.

## Acceptance criteria

- Documentation clearly answers whether `done/` should be treated as project memory and under what conditions.
- Guidance distinguishes targeted retrieval from blindly loading all done tasks.
- Manager/executor/reviewer guidance describes role-specific use of done-task history.
- The recommendation addresses token/context cost and stale context risks.
- If no CLI is added, docs explain how to use existing tools/search to inspect done history.
- If CLI is added, it has `--help`, is read-only, and is covered by smoke validation.
- Existing tasks in `done/` are not modified, moved, compacted, or deleted.
- `validate` passes.
- No unrelated files are changed.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- `python .ai-workflow/scripts/ai_task.py board`
- `python .ai-workflow/scripts/ai_task.py list`
- If CLI is added, run its `--help` and at least one read-only smoke command against existing done tasks.
- Manual review of documentation to confirm it does not instruct agents to load all done tasks by default.
- Forbidden file check: confirm existing done task folders were not changed except this task's own movement/artifacts.

## Notes

- This is primarily a policy/design task. Implement only small supporting docs or read-only tooling if it clearly improves the protocol.
- Bias toward targeted memory retrieval. The protocol should stay lightweight.
- This task should remain in `draft` until human approval moves it to `ready`.
