# Validation: AI-030

## Commands run

| Command | Result |
|---|---|
| `python .ai-workflow/scripts/ai_task.py validate` | passed (0 errors) |
| `python .ai-workflow/scripts/ai_task.py --help` | passed — all 22 commands listed |
| `python .ai-workflow/scripts/ai_task.py list` | passed — warning printed in branch_first mode; done task history shown |
| `python .ai-workflow/scripts/ai_task.py list-branches` | passed — AI-030 active; 21 merged branches listed |
| `python .ai-workflow/scripts/ai_task.py prune-worktrees` | passed — 19 merged worktree candidates listed |
| `python .ai-workflow/scripts/ai_task.py update-from-main --all` | passed — AI-030 already current; 2 merged skipped; 19 inactive (done) skipped |
| `python .ai-workflow/scripts/test_cascade.py` | FAILED — 6/8 tests error (regression from AI-020 auto-commit; see report §4) |
| `python .ai-workflow/scripts/test_claim.py` | passed — 21/21 |
| `python .ai-workflow/scripts/test_prune.py` | passed — 18/18 |
| `python .ai-workflow/scripts/test_review.py` | passed — 14/14 |
| `python .ai-workflow/scripts/test_show.py` | passed — 3/3 |
| `python .ai-workflow/scripts/test_update_from_main.py` | passed — 43/43 |
| `rg -n "prepare-worktree|migrate|main_first|main-first|move .* ready|legacy|deprecated|obsolete" .ai-workflow AGENTS.md CLAUDE.md` | passed — results reviewed; all occurrences accounted for in report §2-3 |
| `git diff --name-only main...HEAD` | passed — only task folder files; no production code changed |

## Forbidden file check

passed — no Unity serialized files, packages, project settings, or `.meta` files changed.
