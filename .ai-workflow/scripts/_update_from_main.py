"""update-from-main command: merge main into active task branch worktrees.

Operates from the main/control-plane checkout.

Usage:
    update-from-main AI-026                            # dry-run for one task
    update-from-main AI-026 --apply                    # merge main into AI-026 worktree
    update-from-main --all                             # dry-run for all worktree-backed tasks
    update-from-main --all --apply                     # merge main into all eligible worktrees
    update-from-main --all --include-no-worktree       # also include branches without worktrees
    update-from-main --all --include-no-worktree --apply
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import List, NamedTuple, Optional, Tuple

from _core import repo_root
from _discovery import (
    _discovery_cfg,
    _list_local_branches,
    _merged_into_main,
    _parse_workflow_config,
    _read_task_meta_from_branch,
    _run_git,
    _task_id_from_branch,
)

# Statuses that represent active in-flight work eligible for update.
_ACTIVE_STATUSES = {"draft", "ready", "in_progress", "ready_for_review", "changes_requested"}


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

class _UpdateResult(NamedTuple):
    branch: str
    task_id: str
    # outcome values: updated | already_current | dry_run | skipped_dirty |
    #                 skipped_no_worktree | skipped_merged | conflict | error
    outcome: str
    detail: str


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _find_worktree_for_branch(branch: str, root: Path) -> Optional[Path]:
    """Return the path of an existing local worktree checked out on the branch."""
    ok, out = _run_git(["worktree", "list", "--porcelain"], cwd=root)
    if not ok or not out:
        return None
    current_path: Optional[str] = None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("worktree "):
            current_path = line[len("worktree "):].strip()
        elif line.startswith("branch ") and current_path:
            ref = line[len("branch "):].strip()
            if ref == f"refs/heads/{branch}" or ref == branch:
                return Path(current_path)
    return None


def _commits_main_ahead(branch: str, root: Path) -> int:
    """Return commits in main not yet in the task branch (-1 on error)."""
    ok, out = _run_git(["rev-list", f"{branch}..main", "--count"], cwd=root)
    if not ok:
        return -1
    try:
        return int(out.strip())
    except ValueError:
        return -1


def _is_worktree_dirty(worktree_path: Path) -> bool:
    """Return True if the worktree has any uncommitted changes."""
    ok, out = _run_git(["status", "--porcelain"], cwd=worktree_path)
    return bool(out.strip()) if ok else True


def _merge_main(worktree_path: Path) -> Tuple[bool, str]:
    """Run `git merge main` inside the worktree. Returns (success, output)."""
    try:
        result = subprocess.run(
            ["git", "merge", "main"],
            cwd=str(worktree_path),
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return False, "git is not available"
    output = (result.stdout.strip() + "\n" + result.stderr.strip()).strip()
    return result.returncode == 0, output


def _worktree_path_for_branch(branch: str, root: Path) -> Path:
    """Compute the standard worktree path for a task branch (same convention as claim)."""
    slug = branch.split("/", 1)[-1].replace("/", "-")
    return root.parent / f"{root.name}.worktrees" / slug


def _worktree_add(branch: str, wt_path: Path, root: Path) -> Tuple[bool, str]:
    """Add a git worktree for the given existing branch at wt_path."""
    ok, out = _run_git(["worktree", "add", str(wt_path), branch], cwd=root)
    return ok, out


def _worktree_remove(wt_path: Path, root: Path) -> Tuple[bool, str]:
    """Remove a git worktree."""
    ok, out = _run_git(["worktree", "remove", str(wt_path)], cwd=root)
    return ok, out


def _find_branch_for_task(task_id: str) -> str:
    """Return the local branch name for a task ID, or raise SystemExit."""
    cfg = _discovery_cfg()
    prefix = cfg["branch_prefix"]
    for b in _list_local_branches(prefix):
        if _task_id_from_branch(b) == task_id.upper():
            return b
    raise SystemExit(
        f"No local task branch found for {task_id} (prefix={prefix})."
    )


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def _process_branch(
    branch: str, task_id: str, root: Path, apply: bool,
    allow_no_worktree: bool = False,
) -> _UpdateResult:
    """Compute or perform the update for one branch.

    When allow_no_worktree=True, branches without an existing local worktree
    are handled by creating a temporary worktree, merging, then cleaning it up
    on success (or leaving it in place on conflict for manual resolution).
    """
    # Skip branches already merged into main
    merged_local, _ = _merged_into_main()
    if branch in merged_local:
        return _UpdateResult(branch, task_id, "skipped_merged", "already merged into main")

    # Find existing local worktree
    worktree = _find_worktree_for_branch(branch, root)

    if worktree is None:
        if not allow_no_worktree:
            return _UpdateResult(branch, task_id, "skipped_no_worktree",
                                 "no local worktree — open one to update this branch")

        # No-worktree path: check if main has anything new first
        ahead = _commits_main_ahead(branch, root)
        if ahead == 0:
            return _UpdateResult(branch, task_id, "already_current",
                                 "branch already contains all commits from main")
        if ahead < 0:
            return _UpdateResult(branch, task_id, "error",
                                 "could not compare branch to main (is 'main' a valid branch?)")

        temp_path = _worktree_path_for_branch(branch, root)
        if not apply:
            return _UpdateResult(branch, task_id, "dry_run_no_worktree",
                                 f"{ahead} commit(s) from main pending — "
                                 f"a temporary worktree would be created at {temp_path}, "
                                 "run with --apply to merge")

        # Apply: create temporary worktree, merge, clean up on success
        ok, err = _worktree_add(branch, temp_path, root)
        if not ok:
            return _UpdateResult(branch, task_id, "error",
                                 f"failed to create temporary worktree at {temp_path}: {err}")
        success, msg = _merge_main(temp_path)
        if success:
            _worktree_remove(temp_path, root)
            return _UpdateResult(branch, task_id, "updated",
                                 (msg or "Merge complete.") + " Temporary worktree cleaned up.")
        return _UpdateResult(branch, task_id, "conflict",
                             f"merge conflict — worktree left at {temp_path} for manual resolution\n"
                             f"To resolve: cd {temp_path} && git merge --continue\n{msg}")

    # Existing worktree path (unchanged)

    # Check if already up to date
    ahead = _commits_main_ahead(branch, root)
    if ahead == 0:
        return _UpdateResult(branch, task_id, "already_current",
                             "branch already contains all commits from main")
    if ahead < 0:
        return _UpdateResult(branch, task_id, "error",
                             "could not compare branch to main (is 'main' a valid branch?)")

    # Refuse dirty worktrees
    if _is_worktree_dirty(worktree):
        return _UpdateResult(branch, task_id, "skipped_dirty",
                             f"worktree at {worktree} has uncommitted changes — "
                             "commit or stash before updating")

    # Dry-run
    if not apply:
        return _UpdateResult(branch, task_id, "dry_run",
                             f"{ahead} commit(s) from main pending — "
                             "run with --apply to merge")

    # Apply: merge main
    success, msg = _merge_main(worktree)
    if success:
        return _UpdateResult(branch, task_id, "updated",
                             msg or "Merge complete.")
    return _UpdateResult(branch, task_id, "conflict",
                         f"merge conflict in {worktree} — resolve manually, "
                         f"then `git merge --continue`\n{msg}")


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

_OUTCOME_LABEL = {
    "updated":                "Updated",
    "already_current":        "Already current",
    "dry_run":                "Would update (dry-run — use --apply)",
    "dry_run_no_worktree":    "Would update via temporary worktree (dry-run — use --apply)",
    "skipped_dirty":          "Skipped — dirty worktree",
    "skipped_no_worktree":    "Skipped — no local worktree",
    "skipped_merged":         "Skipped — merged into main",
    "skipped_inactive":       "Skipped — inactive status (done/rejected)",
    "conflict":               "CONFLICT — manual resolution required",
    "error":                  "Error",
}

_OUTCOME_ORDER = [
    "updated", "already_current", "dry_run", "dry_run_no_worktree",
    "skipped_dirty", "skipped_no_worktree", "skipped_merged", "skipped_inactive",
    "conflict", "error",
]


def _print_summary(results: List[_UpdateResult]) -> None:
    groups: dict = {}
    for r in results:
        groups.setdefault(r.outcome, []).append(r)

    print()
    for outcome in _OUTCOME_ORDER:
        items = groups.get(outcome, [])
        if not items:
            continue
        label = _OUTCOME_LABEL.get(outcome, outcome)
        print(f"{label} ({len(items)}):")
        for r in items:
            print(f"  {r.task_id}  {r.branch}")
            if r.detail:
                for line in r.detail.splitlines():
                    print(f"    {line}")
    print()


# ---------------------------------------------------------------------------
# Command handler
# ---------------------------------------------------------------------------

def update_from_main(args: argparse.Namespace) -> None:
    """Merge main into active task branch worktrees."""
    ok, _ = _run_git(["rev-parse", "--git-dir"])
    if not ok:
        raise SystemExit("Error: not a git repository.")

    ok, _ = _run_git(["rev-parse", "--verify", "main"])
    if not ok:
        raise SystemExit("Error: 'main' branch not found.")

    cfg = _parse_workflow_config()
    mode = cfg.get("mode", "main_first")
    if mode != "branch_first":
        raise SystemExit(
            f"Error: update-from-main is only supported in branch_first workflow mode "
            f"(current mode: {mode})."
        )

    task_id: Optional[str] = getattr(args, "task_id", None)
    update_all: bool = getattr(args, "update_all", False)
    apply: bool = getattr(args, "apply", False)
    include_no_worktree: bool = getattr(args, "include_no_worktree", False)

    if not task_id and not update_all:
        raise SystemExit("Specify a task ID or use --all.")
    if task_id and update_all:
        raise SystemExit("Specify either a task ID or --all, not both.")

    root = repo_root()

    print("Mode:", "apply" if apply else "dry-run (use --apply to perform merges)")

    results: List[_UpdateResult] = []

    if task_id:
        branch = _find_branch_for_task(task_id)
        print(f"Target: {task_id}  ({branch})")
        # Single-task mode always allows no-worktree update
        results.append(_process_branch(branch, task_id, root, apply,
                                       allow_no_worktree=True))
    else:
        disc_cfg = _discovery_cfg()
        prefix = disc_cfg["branch_prefix"]
        branches = _list_local_branches(prefix)
        print(f"Scanning {len(branches)} local task branch(es)...")
        for branch in branches:
            tid = _task_id_from_branch(branch) or "?"
            meta = _read_task_meta_from_branch(branch, tid)
            status = (meta or {}).get("status", "")
            if status and status not in _ACTIVE_STATUSES:
                results.append(_UpdateResult(branch, tid, "skipped_inactive",
                                             f"status={status}"))
                continue
            results.append(_process_branch(branch, tid, root, apply,
                                           allow_no_worktree=include_no_worktree))

    _print_summary(results)

    if any(r.outcome == "conflict" for r in results):
        raise SystemExit(1)
