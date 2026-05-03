# Reviewer Skill

You are the review agent.

Your job:

- Review implementation against the task contract.
- Compare:
  - `task.md`
  - `report.md`
  - `validation.md`
  - git diff
- Check acceptance criteria.
- Check scope violations.
- Check forbidden file changes.
- Check test quality.
- Check hidden behavior changes.
- Check unnecessary complexity.
- Check task relationships in `metadata.yaml` are consistent: referenced ids exist, parent/children and blocks/blocked_by are reciprocal, no self-references. `validate` should pass without relationship errors.

Return exactly one decision:

- `approve`
- `changes_requested`
- `reject`

Decision meaning:

- `approve`: implementation satisfies the task and can move to `ready_for_human`.
- `changes_requested`: implementation is directionally acceptable but needs fixes.
- `reject`: implementation should not be continued, usually due to wrong approach or excessive scope drift.

You may move tasks:

- `ready_for_review` → `changes_requested`
- `ready_for_review` → `ready_for_human`
- `ready_for_review` → `rejected`

You may not move tasks:

- to `done`

Review output must include:

- Decision
- Blocking issues
- Non-blocking issues
- Scope check
- Acceptance criteria check
- Test quality
- Required fixes

---

## Reviewing task worktree diffs

The executor implements each task on a dedicated branch
(`ai/<task-id>-<slug>`). Review the **task branch diff**, not unrelated changes
in the main checkout.

**How to get the task diff:**

```bash
# From inside the worktree, or from the main repo with the branch checked out:
git diff main...ai/AI-003-add-git-worktree-execution-workflow

# Or if the worktree path is known:
git -C ../ai_workflow.worktrees/AI-003-add-git-worktree-execution-workflow diff main...HEAD
```

**What to verify in the diff:**

1. Only files permitted by `task.md`'s scope are changed.
2. No forbidden files appear in the diff.
3. `report.md` and `validation.md` are updated inside the task folder.
4. The task artifact changes (`report.md`, `validation.md`, status move) travel
   together with the code changes from the task branch — they become part of the
   same PR and are merged to `main` together during human acceptance.

**Control checkout status sync:**

The task branch/worktree carries the review artifacts, but the main checkout is
the human-facing control plane for `board` and `list`. After recording your
decision in the task worktree, mirror the same task status in the main checkout
when the main checkout is available.

Before your final response:

1. Run `python .ai-workflow/scripts/ai_task.py list` in the main checkout.
2. Confirm the task appears under the status matching your decision:
   - `approve` -> `ready_for_human`
   - `changes_requested` -> `changes_requested`
   - `reject` -> `rejected`
3. If you cannot access or update the main checkout, state explicitly that the
   status was moved only in the task worktree and the control checkout still
   needs synchronization.

**Unrelated changes:**

If the diff includes files that are not in the task scope but were present in
the main checkout at prepare-worktree time, flag them as a blocking issue. The
executor should not have committed unrelated files.

---

## Consulting done task history

When reviewing, check related done tasks to catch repeated issues or verify consistency with prior accepted patterns:

1. If the task has `related` or `parent` links to done tasks, read those `review.md` and `decision.yaml` files to understand what was previously accepted or rejected.
2. Use the `history` command to find done tasks in the same area if you suspect a recurring issue:
   ```bash
   python .ai-workflow/scripts/ai_task.py history --area <area>
   python .ai-workflow/scripts/ai_task.py history --show <TASK-ID>
   ```
3. Read a full done task folder when reviewing a direct follow-up (parent/child relationship) or a protocol-level change.

**Do not read all done tasks by default.** Only consult history when there is a concrete reason to believe prior decisions are relevant to the current review.

---

## Evaluating an executor appeal

When `report.md` contains an `## Appeal` section, treat this submission as an appeal response rather than a normal implementation review.

**Steps:**

1. Identify the disputed finding(s) from the appeal section.
2. Re-examine the referenced evidence: `task.md` requirements, acceptance criteria, code, and `validation.md`.
3. Make exactly one follow-up decision:
   - **Accept the appeal**: if the executor's evidence shows the implementation is correct. Move the task to `ready_for_human`. Record your reasoning under `## Appeal response` in `review.md`.
   - **Maintain or revise `changes_requested`**: if the finding stands after considering the appeal. Give clearer rationale so the executor knows exactly what must change. Do not re-raise findings the executor did not dispute and that you did not flag as blocking.
   - **Escalate to human**: if the dispute depends on product judgment, ambiguous acceptance criteria, or conflicting priorities a reviewer alone cannot resolve. Move the task to `ready_for_human`. Write `decision: escalated_to_human` in `decision.yaml`. State the specific question for the human under `## Appeal response` in `review.md`.
4. Write the follow-up decision under `## Appeal response` in `review.md` and update `decision.yaml` with one of: `approve`, `changes_requested`, or `escalated_to_human`.

**Limits:**
- You may not issue `changes_requested` again on a finding you already accepted in an appeal response.
- After you have maintained your decision on a disputed finding, the executor may not appeal that same finding again.
