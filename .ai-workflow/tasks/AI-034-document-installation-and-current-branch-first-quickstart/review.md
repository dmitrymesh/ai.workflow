# Review: AI-034

## Decision

changes_requested

## Blocking issues

- `README.md` still does not explain what to commit after installation. This is an explicit task requirement: "Documentation must explain what to commit after installation." The install sections describe `install-plan --apply`, `init`, `validate`, merge snippets, and smoke checks, but there is no post-install commit guidance for the generated protocol files and integration-point edits. A new or existing project user can finish the documented install flow without knowing which files should be staged and committed.
- The post-install docs do not provide a practical config decision checklist for the requested setup choices. The task scope calls out clarifying `generic` vs `unity`, `workflow.mode`, `integration.mode`, `agents.*`, and discovery settings after install. The current README only mentions `--profile generic # or unity` and scattered later references; it does not tell an installer what to review or choose in `.ai-workflow/config.yaml` after installation.

## Non-blocking issues

- The previous `create` followed directly by `approve` blocker is addressed: the smoke test is now read-only, and the quick start/recommended workflow include branch creation before approval.

## Scope check

The changed files are in scope for a documentation task: `README.md`, `.ai-workflow/README.md`, and AI-034 task artifacts. No workflow code, config semantics, Unity files, package files, or forbidden files were changed.

## Acceptance criteria check

Not met. Stale approval/worktree/review guidance has been removed, required searches pass, and the prior branch-first quick-start issue is fixed. However, the install documentation still misses explicit post-install commit guidance and the requested config/profile decision checklist.

## Test quality

The submitted validation covers the required searches and help commands, and I reran `validate`, `install-plan --help`, `--help`, the stale-guidance searches, and the diff scope check. This is sufficient for the text changes, but the missing install guidance is visible by manual review.

## Unity-specific risks

Not applicable. No Unity files changed.

## Required fixes

- Add explicit post-install commit guidance. It should distinguish new installs from upgrades and tell users to commit protocol-owned files, merged integration-point edits, and any intentional config changes, while not committing generated local artifacts such as `board.md`.
- Add a concise post-install config checklist covering profile (`generic` vs `unity`), `workflow.mode`, `integration.mode`/provider, `agents.*`, and `workflow.discovery` settings.
