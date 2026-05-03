# AI-004: Refactor ai_task CLI module

## Goal

Refactor `.ai-workflow/scripts/ai_task.py` into a more maintainable structure without changing the public CLI behavior.

The current script has grown to roughly 700+ lines and now mixes repository discovery, metadata parsing, task transitions, relationship management, board generation, validation, and worktree preparation in one file. The goal is to reduce coupling and make future protocol changes safer.

## Context

`ai_task.py` started as a compact script but now supports:

- task creation and movement
- generated board output
- validation
- task relationships
- task inspection
- git worktree preparation
- a minimal YAML parser/dumper

This is becoming hard to review and increases the chance that a change in one area breaks another. A conservative refactor is appropriate, but behavior must remain stable because this script is the main protocol tool.

## Scope

Allowed changes:

- `.ai-workflow/scripts/ai_task.py`
- new Python modules under `.ai-workflow/scripts/` if needed
- `.ai-workflow/README.md` only if command usage or developer notes need updating
- root `README.md` only if command usage or developer notes need updating
- `.ai-workflow/board.md` if regenerated
- `.ai-workflow/tasks/draft/AI-004-refactor-ai-task-cli-module/*`

Forbidden changes:

- Do not change status names or allowed transitions.
- Do not change existing command names, arguments, or output semantics except for minor formatting that is explicitly documented.
- Do not remove support for any existing command:
  - `init`
  - `create`
  - `move`
  - `list`
  - `board`
  - `validate`
  - `path`
  - `link`
  - `unlink`
  - `show`
  - `prepare-worktree`
- Do not add external dependencies.
- Do not replace the protocol with a server, database, or vendor-specific integration.
- Do not silently rewrite task metadata formats beyond normalizing fields already supported by the protocol.
- Do not mark any task as `done`.

## Requirements

- Split responsibilities into clearer units. Suggested module boundaries:
  - paths/repository discovery
  - metadata YAML parsing/dumping
  - task lookup and persistence
  - board/list rendering
  - validation
  - relationship commands
  - worktree preparation
  - CLI parser/entrypoint
- Keep `python .ai-workflow/scripts/ai_task.py ...` as the supported entrypoint.
- Preserve the current file-based protocol and templates.
- Preserve behavior for existing tasks, including tasks that already contain relationship metadata.
- Keep implementation stdlib-only.
- Prefer simple modules/functions over introducing classes unless classes clearly reduce complexity.
- Add a lightweight internal smoke-test path if practical, or document a precise manual smoke-test matrix in `validation.md`.
- Avoid a broad rewrite. Move code carefully, keep names understandable, and keep diffs reviewable.

## Acceptance criteria

- `ai_task.py` is smaller and acts primarily as CLI entrypoint or thin dispatcher.
- Responsibilities are separated into one or more focused modules under `.ai-workflow/scripts/`.
- All existing CLI commands still work with the same command names and expected behavior.
- Relationship validation still catches:
  - missing referenced task ids
  - self-references
  - parent/children reciprocity issues
  - blocks/blocked_by reciprocity issues
- `prepare-worktree --help` still works.
- `validate` passes on the repository.
- `board` regenerates successfully.
- The executor report lists the refactor boundaries and confirms no behavior changes were intended.
- No unrelated protocol files are modified.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- `python .ai-workflow/scripts/ai_task.py board`
- `python .ai-workflow/scripts/ai_task.py list`
- `python .ai-workflow/scripts/ai_task.py show AI-004`
- `python .ai-workflow/scripts/ai_task.py prepare-worktree --help`
- Smoke-check at least one relationship command path using temporary tasks or a non-mutating strategy; fully clean up any temporary tasks before review.
- Smoke-check that `create`, `path`, and `move` still work. If temporary tasks are used, fully clean them up before review.
- Forbidden file check: confirm no `.env*` or unrelated files were changed.

## Notes

- This is a maintenance refactor, not a feature task.
- If the executor finds that safe refactoring requires tests first, they may add a small stdlib-only test harness under `.ai-workflow/scripts/` or document why the task should be split.
- This task should remain in `draft` until human approval moves it to `ready`.
