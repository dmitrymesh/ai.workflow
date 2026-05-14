# AI-034: Document installation and current branch-first quickstart

## Goal

Make the installation and onboarding documentation sufficient for both a new
repository and an existing project, and update quick-start workflow examples to
match the current branch-first CLI behavior.

## Context

The current documentation has a useful safe-install foundation (`install-plan`,
ownership model, merge snippets, `init`, `validate`), but it is not yet
self-contained enough for a user installing the protocol into a new or existing
project without prior context.

Known gaps:

- Root `README.md` explains `install-plan`, but does not clearly distinguish
  installation into an empty/new repository from installation into an existing
  repository.
- Root `README.md` still contains stale quick-start guidance such as
  `move AI-001 ready` for human approval instead of `approve AI-001`.
- Root `README.md` still describes the branch-first executor worktree opening
  path as manual `git worktree add` + `move in_progress`, while the current
  standard executor path is `claim`.
- Root `README.md` still tells reviewers to manually commit review artifacts
  after `review`, while `review` now auto-commits by default.
- `.ai-workflow/README.md` has a shorter installation section and also contains
  stale quick-start guidance.
- The install docs do not include a clear post-install smoke test that verifies
  the installed protocol works.

Relevant files:

- `README.md`
- `.ai-workflow/README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `.ai-workflow/scripts/_install.py`
- `.ai-workflow/scripts/ai_task.py`
- `.ai-workflow/config.yaml`
- `.ai-workflow/skills/manager.md`
- `.ai-workflow/skills/executor.md`
- `.ai-workflow/skills/reviewer.md`

## Scope

Allowed changes:

- Rewrite or extend installation documentation for:
  - new/empty repositories;
  - existing repositories with their own `AGENTS.md`, `CLAUDE.md`, `README.md`,
    or `.claude/` files;
  - upgrade of an existing `.ai-workflow/` installation.
- Update quick-start and recommended workflow examples to current branch-first
  behavior:
  - manager creates a draft task branch;
  - human uses `approve`;
  - executor uses `list-branches` and `claim`;
  - executor commits implementation/report/validation, then `submit`, then
    commits submit metadata if the CLI still requires it;
  - reviewer uses `review`, which auto-commits by default.
- Add a post-install smoke test/checklist that uses safe dry-run or disposable
  task steps.
- Clarify profile and config decisions after install: `generic` vs `unity`,
  `workflow.mode`, `integration.mode`, `agents.*`, and discovery settings.
- Align adapter entrypoint snippets if they are stale or incomplete.
- Update this task's `report.md` and `validation.md`.

Forbidden changes:

- Do not change CLI behavior or protocol semantics in this task.
- Do not remove commands.
- Do not alter task lifecycle transitions.
- Do not change role assignments in this repository's config except for
  documentation examples.
- Do not modify Unity project files, packages, project settings, or `.meta`
  files.

## Requirements

- A user must be able to follow the docs to install the protocol into a brand
  new git repository.
- A user must be able to follow the docs to safely install or upgrade the
  protocol in an existing project without overwriting project-owned files.
- Documentation must explicitly state what `install-plan --apply` does and does
  not overwrite.
- Documentation must explain what to commit after installation.
- Documentation must include a current branch-first happy path using `approve`,
  `list-branches`, and `claim`.
- Documentation must no longer present `move AI-001 ready` as the recommended
  approval path.
- Documentation must no longer require manual review artifact commits after the
  default `review` command unless describing `--no-commit` or legacy behavior.
- Documentation must explain when `list` is useful versus when `list-branches`
  is the correct backlog view.
- Documentation must include a practical verification checklist after install.
- Keep the docs concise enough to be usable, avoiding duplicate contradictory
  procedures between root `README.md` and `.ai-workflow/README.md`.

## Acceptance criteria

- `README.md` has clear sections for new repo install, existing repo install,
  upgrade, and post-install verification.
- `.ai-workflow/README.md` installation/quick-start text is consistent with the
  root README or clearly points to it for full installation details.
- `rg -n "move AI-001 ready|move .* ready" README.md .ai-workflow/README.md AGENTS.md CLAUDE.md .ai-workflow/scripts/ai_task.py`
  finds no recommended human-approval example that conflicts with `approve`.
- `rg -n "git worktree add .*move .*in_progress|manual.*review.*commit|review artifacts" README.md .ai-workflow/README.md AGENTS.md CLAUDE.md`
  finds no stale recommended branch-first workflow that conflicts with current
  `claim` or review auto-commit behavior.
- `python .ai-workflow/scripts/ai_task.py validate` passes.
- `python .ai-workflow/scripts/ai_task.py install-plan --help` still matches
  the documented command shape.
- `report.md` lists every documentation file changed and summarizes the
  install paths covered.
- `validation.md` records all validation commands and any manual checks.

## Validation

Required:

- `python .ai-workflow/scripts/ai_task.py validate`
- `python .ai-workflow/scripts/ai_task.py install-plan --help`
- `python .ai-workflow/scripts/ai_task.py --help`
- `rg -n "move AI-001 ready|move .* ready" README.md .ai-workflow/README.md AGENTS.md CLAUDE.md .ai-workflow/scripts/ai_task.py`
- `rg -n "approve AI-001|list-branches|claim AI-001|review AI-001 --approve|install-plan" README.md .ai-workflow/README.md AGENTS.md CLAUDE.md`
- Manual review of install docs for new repo, existing repo, upgrade, and
  post-install verification coverage.
- `git diff --name-only main...HEAD`

## Notes

This is a documentation task. If implementing the docs reveals a CLI feature
gap, record it in `report.md` as a follow-up instead of changing code here.
