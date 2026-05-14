# AI-035: Streamline README and remove stale protocol notes

## Goal

Streamline the repository README and protocol README so they are concise,
current, and focused on how to install and use the protocol, not on historical
implementation notes or stale future-work planning.

## Context

After `AI-034`, installation and branch-first quick-start documentation should
be current. The next issue is information architecture: the READMEs still appear
to contain too much historical or internal material for a user trying to adopt
the protocol.

Examples of content to review:

- migration details that are only relevant to old protocol layouts;
- "Future work (not in this task)" sections that were useful during earlier
  task planning but are no longer user-facing documentation;
- historical rationale duplicated across multiple sections;
- branch-first design-contract details that may belong in a reference section
  or archived design note rather than the main quick-start path;
- command descriptions that duplicate `--help` without adding operational value.

Relevant files:

- `README.md`
- `.ai-workflow/README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `.ai-workflow/skills/manager.md`
- `.ai-workflow/skills/executor.md`
- `.ai-workflow/skills/reviewer.md`
- `.ai-workflow/scripts/ai_task.py` help text as reference only

## Scope

Allowed changes:

- Remove or significantly condense stale/historical README material that is not
  needed for installation, daily usage, or troubleshooting.
- Move essential reference material behind clearer headings if it must remain.
- Ensure migration guidance is concise and framed as legacy/upgrade-only, not
  part of the normal path.
- Remove obsolete "future work" planning text from user-facing docs unless it
  still represents real current roadmap and belongs in a dedicated roadmap
  section.
- Reduce duplication between root `README.md` and `.ai-workflow/README.md`;
  prefer one canonical full guide and shorter adapter/protocol pointers where
  appropriate.
- Keep current branch-first installation and quick-start instructions from
  `AI-034` intact unless tightening wording.
- Update this task's `report.md` and `validation.md`.

Forbidden changes:

- Do not change CLI behavior, workflow semantics, config defaults, task
  lifecycle transitions, or role assignments.
- Do not remove safety-critical rules from adapter files or role skills.
- Do not delete documentation that is still required for safe installation,
  task execution, review, or Unity guardrails.
- Do not modify task history except this task folder.
- Do not modify Unity project files, packages, project settings, or `.meta`
  files.

## Requirements

- The main README must be approachable for a new adopter: installation,
  configuration, daily workflow, and troubleshooting should be easy to find.
- Historical implementation notes must not dominate the main user path.
- Any remaining migration content must be clearly marked as legacy/upgrade-only
  and kept brief.
- Any remaining design-contract/reference material must be clearly separated
  from quick start and install instructions.
- The docs must preserve important safety constraints:
  - install-plan does not overwrite project-owned files;
  - managers do not move tasks to `ready`;
  - executors do not mark tasks `done`;
  - reviewers use the current review command behavior;
  - branch-first backlog discovery uses `list-branches`;
  - Unity serialized file guardrails remain explicit.
- Remove or update stale references found by searching for:
  `Future work`, `not in this task`, `move AI-001 ready`, broad migration
  examples, and old manual branch-first worktree/review commit flows.

## Acceptance criteria

- `README.md` is shorter or better structured, with user-facing install and
  workflow paths near the top.
- `.ai-workflow/README.md` no longer repeats large obsolete planning sections
  unless they are still necessary protocol reference.
- No user-facing README section presents migration or future-work planning as
  part of the normal current workflow.
- `rg -n "Future work|not in this task|move AI-001 ready|move .* ready" README.md .ai-workflow/README.md AGENTS.md CLAUDE.md`
  returns no stale recommended workflow guidance. If matches remain, they are
  justified in `report.md`.
- `rg -n "migrate|migration" README.md .ai-workflow/README.md` shows migration
  content only in concise legacy/upgrade context.
- `python .ai-workflow/scripts/ai_task.py validate` passes.
- `git diff --name-only main...HEAD` shows only documentation files and this
  task folder.
- `report.md` summarizes what was removed, what was condensed, and what was
  intentionally kept.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- `python .ai-workflow/scripts/ai_task.py --help`
- `python .ai-workflow/scripts/ai_task.py install-plan --help`
- `rg -n "Future work|not in this task|move AI-001 ready|move .* ready" README.md .ai-workflow/README.md AGENTS.md CLAUDE.md`
- `rg -n "migrate|migration" README.md .ai-workflow/README.md`
- Manual documentation review for install path, daily workflow path, and safety
  rules.
- `git diff --name-only main...HEAD`

## Notes

This is an editorial cleanup task. If the executor finds contradictions that
require CLI changes, record follow-up tasks rather than changing code here.
