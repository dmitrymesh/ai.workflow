"""update-from-main command: merge main into active task branch worktrees.

Operates from the main/control-plane checkout.

Usage:
    update-from-main AI-026              # dry-run for one task
    update-from-main AI-026 --apply      # merge main into AI-026 worktree
    update-from-main --all               # dry-run for all active worktrees
    update-from-main --all --apply       # merge main into all eligible worktrees
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
    _run_git,
    _task_id_from_branch,
)


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
    branch: str, task_id: str, root: Path, apply: bool
) -> _UpdateResult:
    """Compute or perform the update for one branch. Pure function of inputs."""
    # Skip branches already merged into main
    merged_local, _ = _merged_into_main()
    if branch in merged_local:
        return _UpdateResult(branch, task_id, "skipped_merged", "already merged into main")

    # Require a local worktree
    worktree = _find_worktree_for_branch(branch, root)
    if worktree is None:
        return _UpdateResult(branch, task_id, "skipped_no_worktree",
                             "no local worktree — open one to update this branch")

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
    "updated":              "Updated",
    "already_current":      "Already current",
    "dry_run":              "Would update (dry-run — use --apply)",
    "skipped_dirty":        "Skipped — dirty worktree",
    "skipped_no_worktree":  "Skipped — no local worktree",
    "skipped_merged":       "Skipped — merged into main",
    "conflict":             "CONFLICT — manual resolution required",
    "error":                "Error",
}

_OUTCOME_ORDER = [
    "updated", "already_current", "dry_run",
    "skipped_dirty", "skipped_no_worktree", "skipped_merged",
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

    task_id: Optional[str] = getattr(args, "task_id", None)
    update_all: bool = getattr(args, "update_all", False)
    apply: bool = getattr(args, "apply", False)

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
        results.append(_process_branch(branch, task_id, root, apply))
    else:
        cfg = _discovery_cfg()
        prefix = cfg["branch_prefix"]
        branches = _list_local_branches(prefix)
        print(f"Scanning {len(branches)} local task branch(es)...")
        for branch in branches:
            tid = _task_id_from_branch(branch) or "?"
            results.append(_process_branch(branch, tid, root, apply))

    _print_summary(results)

    if any(r.outcome == "conflict" for r in results):
        raise SystemExit(1)
