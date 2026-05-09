# Execution Report: AI-028

## Summary

Updated the branch-first manager workflow docs to include an explicit
`git checkout main` step after committing a draft task contract, so the
shared checkout always returns to `main` after task creation. Added a note
that task artifacts live on the task branch and that human approval is
performed from `main` via `approve`.

## Changed files

- `.ai-workflow/skills/manager.md` — added `git checkout main` as step 4 in branch-first task creation; added paragraph explaining the source-of-truth split; updated approval text to note the human stays on `main` throughout
- `.ai-workflow/README.md` — added return-to-`main` step 3 in "Manager: creating a task in branch-first mode"; added `approve AI-NNN` approval snippet; updated lifecycle diagram to show manager returning to `main` and human approving from `main` via `approve`

## Validation performed

- `python .ai-workflow/scripts/ai_task.py validate` — passed
- `rg -n "checkout main|approve|approval|branch-first|task branch|control plane" .ai-workflow/README.md .ai-workflow/skills/manager.md AGENTS.md CLAUDE.md` — all key terms present in expected locations
- `git diff --name-only main...HEAD` — only task folder files and the two doc files changed; no CLI files modified

## Assumptions

- `AGENTS.md` and `CLAUDE.md` do not reference the manager's branch-first creation steps and needed no changes.
- The `approve` command referenced in the updated docs was implemented by AI-021 and is already present on this branch (merged from `main`).

## Known risks

- None. Pure documentation change.
