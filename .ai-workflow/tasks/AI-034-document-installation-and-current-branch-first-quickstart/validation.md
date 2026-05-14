# Validation: AI-034

## Local

- `python .ai-workflow/scripts/ai_task.py validate`: passed
- `python .ai-workflow/scripts/ai_task.py install-plan --help`: passed — command shape unchanged
- `python .ai-workflow/scripts/ai_task.py --help`: passed — all commands present
- `rg -n "move AI-001 ready|move .* ready" README.md .ai-workflow/README.md AGENTS.md CLAUDE.md .ai-workflow/scripts/ai_task.py`:
  no conflicting recommended human-approval examples (remaining matches are prohibitions
  or help-text descriptions, not recommendations)
- `rg -n "git worktree add .*move .*in_progress|manual.*review.*commit|review artifacts" README.md .ai-workflow/README.md AGENTS.md CLAUDE.md`:
  no matches — stale guidance removed
- `rg -n "approve AI-001|list-branches|claim AI-001|review AI-001 --approve|install-plan" README.md .ai-workflow/README.md AGENTS.md CLAUDE.md`:
  all present in both READMEs
- `git diff --name-only main...HEAD` (AI-034 branch after commit): only AI-034 task folder
  and README.md / .ai-workflow/README.md

## Manual review

- README.md has clear sections for: new repo install, existing repo install (safe workflow),
  upgrade, post-install verification checklist
- `.ai-workflow/README.md` Quick start is consistent with root README
- `list` vs `list-branches` distinction documented in README.md Basic commands
- `review` auto-commit behavior documented; `--no-commit` option noted
- No forbidden files changed (no CLI, no Unity files, no config semantics changed)

## Human review

- Status: pending
- Reviewer: null

## Guardrails

- Forbidden files changed: none
- Package changes: none

## Notes

Documentation-only task. No Unity code changed; recompile check not applicable.
