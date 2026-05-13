"""Approve command: move a draft task to ready on the task branch.

Operates from the control-plane (main) checkout — no manual worktree entry needed.
"""
from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

from _core import dump_simple_yaml, parse_simple_yaml_str, repo_root, today, write_text
from _discovery import (
    _discovery_cfg,
    _list_local_branches,
    _list_remote_branches,
    _ls_task_folder_paths,
    _run_git,
    _task_id_from_branch,
)


# ---------------------------------------------------------------------------
# Branch lookup
# ---------------------------------------------------------------------------

def _find_task_branch(task_id: str) -> str:
    """Return the local or remote branch name for a task, or raise SystemExit."""
    cfg = _discovery_cfg()
    scope = cfg["scope"]
    remote = cfg["remote"]
    prefix = cfg["branch_prefix"]

    if scope in ("local", "both"):
        for b in _list_local_branches(prefix):
            if _task_id_from_branch(b) == task_id:
                return b

    if scope in ("remote", "both"):
        for b in _list_remote_branches(prefix, remote):
            if _task_id_from_branch(b) == task_id:
                return b

    raise SystemExit(
        f"No task branch found for {task_id} "
        f"(scope={scope}, prefix={prefix})."
    )


def _read_task_folder_and_meta(
    branch: str, task_id: str
) -> Tuple[str, Dict]:
    """Return (repo_relative_folder_path, meta_dict) for task_id on the branch."""
    for folder_path in _ls_task_folder_paths(branch):
        if Path(folder_path).name.upper().startswith(task_id.upper()):
            ok, content = _run_git(["show", f"{branch}:{folder_path}/metadata.yaml"])
            if ok and content:
                return folder_path, parse_simple_yaml_str(content)
    raise SystemExit(
        f"Task folder or metadata.yaml not found on branch '{branch}' for {task_id}."
    )


# ---------------------------------------------------------------------------
# Git helper (checked)
# ---------------------------------------------------------------------------

def _git(args: list, cwd: Path, label: str = "") -> str:
    """Run a git command; raise SystemExit with a human-readable message on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise SystemExit("git is not available")
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        tag = f" ({label})" if label else ""
        raise SystemExit(f"git {args[0]} failed{tag}: {detail}")
    return result.stdout.strip()


# ---------------------------------------------------------------------------
# --print-only output
# ---------------------------------------------------------------------------

def _print_approval_commands(branch: str, folder_path: str, task_id: str) -> None:
    root = repo_root()
    tmp_path = root.parent / f"{root.name}.worktrees" / f".approve-{task_id}"
    meta_rel = f"{folder_path}/metadata.yaml"

    print(f"# Approve {task_id}: draft -> ready")
    print()
    print("Step 1 — create a temporary worktree:")
    print(f"  git worktree add {tmp_path} {branch}")
    print()
    print("Step 2 — update metadata.yaml (set status to ready, update updated_at):")
    print(f"  # Edit: {tmp_path / meta_rel}")
    print('  # Change:  status: "draft"  ->  status: "ready"')
    print(f'  # Change:  updated_at: "<old>"  ->  updated_at: "{today()}"')
    print()
    print("Step 3 — commit the approval:")
    print(f"  git -C {tmp_path} add {meta_rel}")
    print(f'  git -C {tmp_path} commit -m "chore: {task_id} | approve task to ready"')
    print()
    print("Step 4 — remove the temporary worktree:")
    print(f"  git worktree remove --force {tmp_path}")


# ---------------------------------------------------------------------------
# Live execution
# ---------------------------------------------------------------------------

def _find_existing_worktree(branch: str, root: Path) -> Optional[Path]:
    """Return the path of an existing worktree checked out on the given branch, or None."""
    ok, out = _run_git(["worktree", "list", "--porcelain"], cwd=root)
    if not ok or not out:
        return None

    current_path: Optional[str] = None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("worktree "):
            current_path = line[len("worktree "):].strip()
        elif line.startswith("branch ") and current_path:
            # branch refs/heads/ai/AI-023-slug
            ref = line[len("branch "):].strip()
            if ref == f"refs/heads/{branch}" or ref == branch:
                return Path(current_path)
    return None


def _assert_worktree_clean(worktree_path: Path, meta_rel: str) -> None:
    """Raise SystemExit if the worktree has staged changes or if the target file is locally modified.

    Guards against two unsafe situations when reusing an existing worktree:
    - Staged changes unrelated to this approval being swept into the commit.
    - Local modifications to metadata.yaml being silently overwritten.
    """
    ok, out = _run_git(["status", "--porcelain"], cwd=worktree_path)
    if not ok:
        raise SystemExit(
            f"Could not read worktree status at {worktree_path}. "
            "Cannot safely reuse this worktree."
        )

    if not out:
        return  # clean worktree — nothing to check

    # git always uses forward slashes in porcelain output
    meta_rel_norm = meta_rel.replace("\\", "/")

    staged: list = []
    meta_dirty = False

    for line in out.splitlines():
        if len(line) < 4:
            continue
        index_status = line[0]   # staged
        worktree_status = line[1]  # working tree
        path = line[3:].strip().replace("\\", "/")

        if index_status not in (" ", "?"):
            staged.append(path)

        if path == meta_rel_norm and worktree_status != " ":
            meta_dirty = True

    if staged:
        listing = "\n".join(f"  {p}" for p in staged)
        raise SystemExit(
            f"Existing worktree at {worktree_path} has staged changes:\n{listing}\n"
            "Unstage or commit these changes before approving."
        )

    if meta_dirty:
        raise SystemExit(
            f"Existing worktree at {worktree_path} has local modifications to "
            f"{meta_rel}. Commit or discard them before approving."
        )


def _execute_approval(
    branch: str, folder_path: str, task_id: str, meta: dict
) -> None:
    root = repo_root()
    meta_rel = f"{folder_path}/metadata.yaml"

    print(f"Approving {task_id}: draft -> ready on branch {branch}")

    existing = _find_existing_worktree(branch, root)
    if existing:
        worktree_path = existing
        use_temp = False
        print(f"  Using existing worktree: {worktree_path}")
        # Refuse to proceed if the worktree has staged changes or a dirty target file.
        _assert_worktree_clean(worktree_path, meta_rel)
    else:
        # Create a temporary worktree with a time-suffixed path to avoid collisions.
        worktree_path = (
            root.parent / f"{root.name}.worktrees" / f".approve-{task_id}-{int(time.time())}"
        )
        use_temp = True
        _git(
            ["worktree", "add", str(worktree_path), branch],
            cwd=root,
            label="create temp worktree",
        )
        print(f"  Temp worktree: {worktree_path}")

    try:
        meta_file = worktree_path / folder_path / "metadata.yaml"
        if not meta_file.exists():
            raise SystemExit(f"metadata.yaml not found at: {meta_file}")

        meta["status"] = "ready"
        meta["updated_at"] = today()
        write_text(meta_file, dump_simple_yaml(meta))

        _git(["add", meta_rel], cwd=worktree_path, label="stage metadata")
        _git(
            ["commit", "-m", f"chore: {task_id} | approve task to ready"],
            cwd=worktree_path,
            label="commit approval",
        )
        print(f"  Committed approval to {branch}")
    finally:
        if use_temp:
            _git(
                ["worktree", "remove", "--force", str(worktree_path)],
                cwd=root,
                label="cleanup",
            )
            print(f"  Removed temp worktree")

    print()
    print(f"Done. {task_id} is now ready.")
    print(f"Executors can claim it via: python .ai-workflow/scripts/ai_task.py list-branches")


# ---------------------------------------------------------------------------
# Command handler
# ---------------------------------------------------------------------------

def approve_task(args: argparse.Namespace) -> None:
    """Human-facing approve: move a draft task to ready on the task branch."""
    ok, _ = _run_git(["rev-parse", "--git-dir"])
    if not ok:
        raise SystemExit("Error: not a git repository.")

    task_id = args.task_id.strip().upper()

    branch = _find_task_branch(task_id)
    folder_path, meta = _read_task_folder_and_meta(branch, task_id)

    current_status = str(meta.get("status") or "?")
    if current_status != "draft":
        raise SystemExit(
            f"approve requires task to be draft (current: {current_status})."
        )

    if getattr(args, "print_only", False):
        _print_approval_commands(branch, folder_path, task_id)
    else:
        _execute_approval(branch, folder_path, task_id, meta)
