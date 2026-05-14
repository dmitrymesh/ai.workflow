# Review: AI-034

## Decision

changes_requested

## Blocking issues

- The new existing-repo and upgrade commit guidance can stage project-owned task data. `README.md` lines 191-199 and 206-213 say to stage protocol-owned files with `git add .ai-workflow/`, but `.ai-workflow/tasks/` is explicitly project-owned and excluded from installer ownership. In an existing project with active or edited task artifacts, that command can stage task folders into a protocol install/upgrade commit, which contradicts the ownership model and the text "Stage and commit only the protocol-owned files that changed."

## Non-blocking issues

- The previous blockers are addressed: smoke verification is read-only, quick start/recommended workflow include branch creation before approval, commit guidance exists, and a config checklist exists.
- The configuration checklist covers `workflow.discovery.scope`, but not `workflow.discovery.remote` or `workflow.discovery.branch_prefix`. Consider adding those if the goal is to cover all discovery settings rather than only the most commonly changed one.

## Scope check

The changed files are in scope for a documentation task: `README.md`, `.ai-workflow/README.md`, and AI-034 task artifacts. No workflow code, config semantics, Unity files, package files, or forbidden files were changed.

## Acceptance criteria check

Not met. Stale approval/worktree/review guidance has been removed, required searches pass, the prior branch-first quick-start issue is fixed, and the missing sections were added. The remaining problem is that the commit guidance is unsafe for existing repositories because it can stage project-owned task artifacts.

## Test quality

The submitted validation covers the required searches and help commands, and I reran `validate`, `install-plan --help`, `--help`, the stale-guidance searches, config-section search, and diff scope check. The remaining issue is a manual-review documentation safety issue.

## Unity-specific risks

Not applicable. No Unity files changed.

## Required fixes

- Replace existing-repo and upgrade `git add .ai-workflow/` guidance with a safer instruction that excludes `.ai-workflow/tasks/` and `.ai-workflow/board.md`. For example, tell users to inspect `git status --short .ai-workflow` and stage only protocol-owned paths reported by `install-plan`, plus intentional config changes and manually merged integration-point files.
