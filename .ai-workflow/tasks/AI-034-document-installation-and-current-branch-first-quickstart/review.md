# Review: AI-034

## Decision

changes_requested

## Blocking issues

- `README.md`'s post-install smoke test is not executable in the documented branch-first install path. It tells users to run `create "Smoke test"` and then `approve AI-001` from the same checkout, but `create` only creates a task folder in the current checkout; it does not create the required `ai/AI-001-*` task branch. I reproduced the documented sequence in a disposable installed repo: `approve AI-001` failed with `No task branch found for AI-001 (scope=local, prefix=ai/).` See `README.md` lines 132-137.
- `.ai-workflow/README.md` quick start has the same invalid branch-first sequence: `create "Example task"` followed directly by `approve AI-001`. This conflicts with the task requirement that quick-start examples match current branch-first behavior, where the manager creates and commits a draft task branch before human approval. See `.ai-workflow/README.md` lines 145-149.

## Non-blocking issues

- `README.md`'s recommended workflow says the manager "creates or updates a task folder" and then immediately documents `approve`, but it does not show or link to the branch-first manager step that creates the draft task branch. The text at `README.md` lines 346-377 should be aligned with the actual branch-first creation procedure.

## Scope check

The changed files are in scope for a documentation task: `README.md`, `.ai-workflow/README.md`, and AI-034 task artifacts. No workflow code, config semantics, Unity files, package files, or forbidden files were changed.

## Acceptance criteria check

Not met. The stale `move AI-001 ready` guidance is removed and the required validation commands pass, but the new quick-start and post-install verification examples do not match current branch-first CLI behavior because they omit task branch creation before `approve`.

## Test quality

The submitted validation covers the required searches and help commands. I also ran a disposable install smoke reproduction, which exposed the blocking issue: `approve AI-001` fails after the documented `create "Smoke test"` step because no task branch exists.

## Unity-specific risks

Not applicable. No Unity files changed.

## Required fixes

- Update the post-install smoke test so it is actually executable in a branch-first installation. It must either include the manager branch creation/commit step before `approve`, or use a different safe verification that does not imply `create` alone creates a task branch.
- Update `.ai-workflow/README.md` quick start to show the branch-first draft-branch creation path or clearly point to the full root README section for branch-first task creation before `approve`.
- Align the root README recommended workflow so the manager step explicitly includes creating/committing the draft task branch, or links directly to an existing authoritative branch-first creation section.
