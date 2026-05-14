# Validation: AI-034

## Local

- `python .ai-workflow/scripts/ai_task.py validate`: passed
- `python .ai-workflow/scripts/ai_task.py install-plan --help`: passed — command shape unchanged
- `python .ai-workflow/scripts/ai_task.py --help`: passed — all commands present
- `rg -n "move AI-001 ready|move .* ready" README.md .ai-workflow/README.md AGENTS.md CLAUDE.md .ai-workflow/scripts/ai_task.py`:
  one match in README.md (line 615: prohibition, not recommendation) — no conflicts
- `rg -n "git worktree add .*move .*in_progress|manual.*review.*commit|review artifacts" README.md .ai-workflow/README.md AGENTS.md CLAUDE.md`:
  no matches — stale guidance removed
- `rg -n "approve AI-001|list-branches|claim AI-001|review AI-001 --approve|install-plan" README.md .ai-workflow/README.md AGENTS.md CLAUDE.md`:
  all present in both READMEs
- `rg -n "git checkout -b ai/" .ai-workflow/README.md README.md`:
  branch creation steps present in quick start and manager section
- `rg -n "What to commit|Configuration checklist|board.md" README.md`:
  new sections present; board.md explicitly excluded from commit
- `git diff --name-only main...HEAD` (AI-034 branch after commit): only AI-034 task folder
  and README.md / .ai-workflow/README.md

## Manual review

- README.md has clear sections for: new repo install (with commit step), existing repo
  install (with commit guidance), upgrade (with commit guidance), post-install verification
- "What to commit after installation" distinguishes new install, existing repo, and upgrade;
  explicitly excludes board.md
- "Configuration checklist" covers profile, workflow.mode, integration.mode/provider,
  agents.*.default_tool, and workflow.discovery.scope
- Post-install verification checklist uses only read-only commands — executable without
  task branch creation
- `.ai-workflow/README.md` quick start includes branch creation before `approve` —
  sequence is fully executable in a branch-first installation
- README.md `### Manager prepares task` shows explicit branch-first branch creation procedure
- `list` vs `list-branches` distinction documented
- `review` auto-commit documented; `--no-commit` noted
- No forbidden files changed

## Human review

- Status: pending
- Reviewer: null

## Guardrails

- Forbidden files changed: none
- Package changes: none

## Notes

Documentation-only task. No Unity code changed; recompile check not applicable.
All blocking issues across both reviews are addressed:
1. Smoke test is read-only and executable without task branch creation.
2. `.ai-workflow/README.md` quick start includes branch creation before `approve`.
3. Root README has explicit manager branch creation step.
4. Post-install commit guidance added with new/existing/upgrade distinction.
5. Config decision checklist added covering all post-init settings.
