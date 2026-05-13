"""prune-worktrees command: list and optionally remove merged task worktrees."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, NamedTuple, Optional

from _core import repo_root
from _discovery import _discovery_cfg, _merged_into_main, _run_git


class _WorktreeEntry(NamedTuple):
    path: Path
    branch: Optional[str]  # None for detached HEAD


def _list_worktrees(root: Path) -> List[_WorktreeEntry]:
    """Parse `git worktree list --porcelain` and return all entries."""
    ok, out = _run_git(["worktree", "list", "--porcelain"], cwd=root)
    if not ok or not out:
        return []

    entries: List[_WorktreeEntry] = []
    current_path: Optional[str] = None
    current_branch: Optional[str] = None

    for raw in out.splitlines():
        line = raw.strip()
        if line.startswith("worktree "):
            if current_path is not None:
                entries.append(_WorktreeEntry(Path(current_path), current_branch))
            current_path = line[len("worktree "):]
            current_branch = None
        elif line.startswith("branch "):
            ref = line[len("branch "):]
            # Normalise refs/heads/ai/... -> ai/...
            if ref.startswith("refs/heads/"):
                ref = ref[len("refs/heads/"):]
            current_branch = ref

    if current_path is not None:
        entries.append(_WorktreeEntry(Path(current_path), current_branch))

    return entries


def _is_dirty(worktree_path: Path) -> bool:
    ok, out = _run_git(["status", "--porcelain"], cwd=worktree_path)
    if not ok:
        return True  # treat unreadable state as dirty (safe)
    return bool(out.strip())


def _remove_worktree(worktree_path: Path, root: Path) -> tuple[bool, str]:
    ok, out = _run_git(["worktree", "remove", str(worktree_path)], cwd=root)
    return ok, out


def prune_worktrees(args: argparse.Namespace) -> None:
    """List (or remove with --apply) worktrees whose branches are merged into main."""
    ok, _ = _run_git(["rev-parse", "--git-dir"])
    if not ok:
        raise SystemExit("Error: not a git repository.")

    root = repo_root()
    apply = getattr(args, "apply", False)

    prefix = _discovery_cfg()["branch_prefix"]  # e.g. "ai/"
    merged_local, _ = _merged_into_main()
    worktrees = _list_worktrees(root)

    # The main checkout is the first entry from git worktree list
    main_path = worktrees[0].path if worktrees else root

    candidates = []
    for entry in worktrees:
        if entry.path == main_path:
            continue
        if entry.branch is None:
            continue  # detached HEAD — skip
        if not entry.branch.startswith(prefix):
            continue  # not a task branch — skip
        if entry.branch not in merged_local:
            continue
        candidates.append(entry)

    if not candidates:
        print("No merged task worktrees found.")
        return

    if not apply:
        print(f"Merged task worktrees ({len(candidates)} candidate(s)):")
        print("Run with --apply to remove them.\n")
        for entry in candidates:
            print(f"  {entry.path}  [{entry.branch}]")
        return

    # Apply mode
    removed = 0
    skipped_dirty = 0
    failed = 0

    for entry in candidates:
        if _is_dirty(entry.path):
            print(f"  SKIP (dirty): {entry.path}  [{entry.branch}]")
            skipped_dirty += 1
            continue
        ok, err = _remove_worktree(entry.path, root)
        if ok:
            print(f"  Removed: {entry.path}  [{entry.branch}]")
            removed += 1
        else:
            print(f"  FAILED:  {entry.path}  [{entry.branch}]: {err.strip()}")
            failed += 1

    print()
    print(f"Done. Removed: {removed}  Skipped (dirty): {skipped_dirty}  Failed: {failed}")
    if skipped_dirty:
        print("Dirty worktrees were not removed. Commit or stash changes, then re-run.")
    if failed:
        raise SystemExit(1)
