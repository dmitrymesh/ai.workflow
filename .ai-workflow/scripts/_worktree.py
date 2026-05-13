"""Git worktree preparation and task claim commands."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from _board import generate_board
from _core import (
    dump_simple_yaml,
    find_task,
    parse_simple_yaml,
    repo_root,
    save_meta,
    slugify,
    tasks_root,
    today,
    write_text,
)
from _discovery import (
    _discovery_cfg,
    _list_local_branches,
    _read_task_meta_from_branch,
    _task_id_from_branch,
)


def _branch_and_worktree_path(task_id: str, meta: dict) -> tuple[str, Path]:
    folder_name_prefix = task_id + "-"
    # Derive slug from task title or metadata
    title = str(meta.get("title", ""))
    slug = slugify(title) if title else "task"

    branch_name = f"ai/{task_id}-{slug}"
    root = repo_root()
    repo_name = root.name
    worktrees_base = root.parent / f"{repo_name}.worktrees"
    worktree_path = worktrees_base / f"{task_id}-{slug}"
    return branch_name, worktree_path


def _branch_exists_locally(branch_name: str) -> bool:
    """Return True if branch_name already exists in the local repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", branch_name],
        cwd=str(repo_root()),
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _worktree_exists_for_branch(branch_name: str) -> bool:
    """Return True if a worktree is already checked out on branch_name."""
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=str(repo_root()),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return False
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("branch "):
            ref = line[len("branch "):]
            if ref == f"refs/heads/{branch_name}" or ref == branch_name:
                return True
    return False


def _find_task_on_branch(task_id: str):
    """Find a task on a local task branch when it is not in the main checkout.

    Returns (branch_name, meta) or None if no matching branch is found.
    Used in branch-first mode where task folders live on task branches, not main.
    """
    cfg = _discovery_cfg()
    prefix = cfg["branch_prefix"]
    for branch in _list_local_branches(prefix):
        if _task_id_from_branch(branch) == task_id.upper():
            meta = _read_task_meta_from_branch(branch, task_id)
            if meta:
                return branch, meta
    return None


def _add_existing_worktree(branch_name: str, worktree_path: Path) -> bool:
    """Add a worktree to an existing branch (no -b). Returns True on success."""
    if worktree_path.exists():
        print(f"Worktree directory already exists: {worktree_path}")
        return True
    try:
        subprocess.run(
            ["git", "worktree", "add", str(worktree_path), branch_name],
            cwd=str(repo_root()),
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"Added worktree at {worktree_path} on existing branch {branch_name}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        msg = getattr(exc, "stderr", str(exc)).strip()
        print(f"Could not add worktree to existing branch {branch_name}: {msg or exc}")
        return False


def _print_worktree_commands(
    branch_name: str,
    worktree_path: Path,
    task_dir: "Path | None",
    dest_task_dir: "Path | None",
    branch_exists: bool = False,
) -> None:
    if branch_exists:
        print("Step 1 — add worktree to existing branch:")
        print(f"  git worktree add {worktree_path} {branch_name}")
    else:
        print("Step 1 — create the worktree and branch:")
        print(f"  git worktree add -b {branch_name} {worktree_path}")
    if task_dir is not None and dest_task_dir is not None:
        print()
        print("Step 2 — sync the approved task folder into the worktree:")
        if sys.platform == "win32":
            print(f'  xcopy /E /I /Y "{task_dir}" "{dest_task_dir}\\"')
        else:
            print(f'  cp -r "{task_dir}/" "{dest_task_dir}/"')
    print()
    print("Open the executor in the worktree:")
    print(f"  cd {worktree_path}")
    print(f"  # You are on branch: {branch_name}")


def _create_worktree(branch_name: str, worktree_path: Path) -> bool:
    """Create the git worktree. Returns True on success."""
    if worktree_path.exists():
        print(f"Worktree directory already exists: {worktree_path}")
        return True
    try:
        subprocess.run(
            ["git", "worktree", "add", "-b", branch_name, str(worktree_path)],
            cwd=str(repo_root()),
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"Created worktree at {worktree_path} on branch {branch_name}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        msg = getattr(exc, "stderr", str(exc)).strip()
        print(f"Could not create worktree automatically: {msg or exc}")
        return False


def _sync_task_folder(task_dir: Path, dest_task_dir: Path) -> None:
    dest_task_dir.parent.mkdir(parents=True, exist_ok=True)
    if dest_task_dir.exists():
        shutil.rmtree(str(dest_task_dir))
    shutil.copytree(str(task_dir), str(dest_task_dir))
    print(f"Synced task folder to {dest_task_dir}")


def claim_task(args: argparse.Namespace) -> None:
    """Executor self-service claim: find a ready task, create a worktree, move to in_progress.

    Supports both workflow modes:
    - main-first: task folder is in the main checkout; a new branch is created.
    - branch-first: task folder lives on the pre-existing task branch; the worktree
      is added to that branch without -b.
    """
    # Step 1: Find the task. Try the main checkout first (main-first compat), then
    # scan local task branches (branch-first mode).
    task_dir = None
    try:
        task_dir, meta = find_task(args.task_id)
    except SystemExit:
        branch_result = _find_task_on_branch(args.task_id)
        if branch_result is None:
            raise SystemExit(
                f"Task {args.task_id} not found in the current checkout or any local "
                "task branch. Run `list-branches` to verify the branch exists."
            )
        branch_from_branch, meta = branch_result
    else:
        branch_from_branch = None

    current_status = str(meta.get("status") or "unknown")
    if current_status != "ready":
        raise SystemExit(
            f"Task {args.task_id} is not ready (current: {current_status}). "
            "Only ready tasks can be claimed."
        )

    blocked_by = meta.get("blocked_by", [])
    if isinstance(blocked_by, list) and blocked_by:
        raise SystemExit(
            f"Task {args.task_id} is blocked by: {', '.join(blocked_by)}. "
            "Resolve all blockers before claiming."
        )

    task_id = str(meta.get("id") or args.task_id)

    # Determine branch name: use pre-existing branch from metadata or branch scan,
    # or derive it from task title (main-first).
    branch_name = meta.get("branch") or branch_from_branch
    if not branch_name:
        branch_name, _ = _branch_and_worktree_path(task_id, meta)

    _, worktree_path = _branch_and_worktree_path(task_id, meta)

    # Guard: if a worktree is already checked out on this branch, it is already claimed.
    if _worktree_exists_for_branch(branch_name):
        raise SystemExit(
            f"Task {task_id} already has a worktree on branch {branch_name}. "
            "Use that worktree or remove it first."
        )

    # Determine the right worktree add form.
    branch_exists = _branch_exists_locally(branch_name)

    # Task folder sync is only needed in main-first mode (folder is in main checkout).
    root = repo_root()
    dest_task_dir = None
    if task_dir is not None:
        try:
            rel_task_path = task_dir.relative_to(root)
        except ValueError:
            raise SystemExit(f"Task directory {task_dir} is not inside repo root {root}")
        dest_task_dir = worktree_path / rel_task_path

    print(f"Task:       {task_id}")
    print(f"Branch:     {branch_name} ({'existing' if branch_exists else 'new'})")
    print(f"Worktree:   {worktree_path}")
    if dest_task_dir is not None:
        print(f"Task sync:  {task_dir}")
        print(f"         -> {dest_task_dir}")
    print()

    if args.print_only:
        _print_worktree_commands(branch_name, worktree_path, task_dir, dest_task_dir,
                                 branch_exists=branch_exists)
        if task_dir is not None:
            meta["branch"] = branch_name
            meta["status"] = "in_progress"
            meta["updated_at"] = today()
            write_text(task_dir / "metadata.yaml", dump_simple_yaml(meta))
            generate_board(print_result=False)
            print(f"Updated metadata.yaml: branch = {branch_name}, status = in_progress")
        else:
            print()
            print("After adding the worktree, update metadata in the worktree:")
            print(f"  cd {worktree_path}")
            print(f"  python .ai-workflow/scripts/ai_task.py move {task_id} in_progress")
        return

    # Create or attach to worktree.
    if branch_exists:
        ok = _add_existing_worktree(branch_name, worktree_path)
    else:
        ok = _create_worktree(branch_name, worktree_path)

    if not ok:
        raise SystemExit(
            "Worktree creation failed. Task has NOT been claimed. "
            "Resolve the error above and retry."
        )

    # Update metadata and sync task folder.
    if task_dir is not None:
        # main-first: metadata lives in main checkout; sync folder to worktree.
        meta["branch"] = branch_name
        meta["status"] = "in_progress"
        meta["updated_at"] = today()
        write_text(task_dir / "metadata.yaml", dump_simple_yaml(meta))
        generate_board(print_result=False)
        print(f"Updated metadata.yaml: branch = {branch_name}, status = in_progress")
        _sync_task_folder(task_dir, dest_task_dir)
    else:
        # branch-first: metadata lives in the worktree on the task branch.
        branch_slug = branch_name.split("/", 1)[-1]
        wt_task_dir = worktree_path / ".ai-workflow" / "tasks" / branch_slug
        wt_meta = parse_simple_yaml(wt_task_dir / "metadata.yaml")
        wt_meta["status"] = "in_progress"
        wt_meta["updated_at"] = today()
        write_text(wt_task_dir / "metadata.yaml", dump_simple_yaml(wt_meta))
        print(f"Updated metadata.yaml in worktree: status = in_progress")
        print(f"Commit the status change from the worktree:")
        print(f"  cd {worktree_path}")
        print(f"  git add .ai-workflow/tasks/{branch_slug}/metadata.yaml")
        print(f'  git commit -m "chore: {task_id} | claim task to in_progress"')

    print()
    print("Next steps:")
    print(f"  1. Open the worktree: {worktree_path}")
    print(f"  2. Verify branch:     git -C {worktree_path} branch --show-current")
    print(f"  3. Implement the task on branch {branch_name}")
    print()
    print("When done:")
    print(f"  python .ai-workflow/scripts/ai_task.py submit {task_id}")
    print()
    print("Cleanup after merge:")
    print(f"  git worktree remove {worktree_path}")
    if not branch_exists:
        print(f"  git branch -d {branch_name}")


def prepare_worktree(args: argparse.Namespace) -> None:
    """Backward-compatible prepare-worktree: prepares worktree without moving to in_progress."""
    task_dir, meta = find_task(args.task_id)
    current_status = str(meta.get("status") or task_dir.parent.name)

    if current_status != "ready":
        raise SystemExit(
            f"Task {args.task_id} is not in 'ready' status (current: {current_status}). "
            "Only ready tasks can be prepared for execution."
        )

    task_id = str(meta.get("id"))
    branch_name, worktree_path = _branch_and_worktree_path(task_id, meta)

    root = repo_root()
    try:
        rel_task_path = task_dir.relative_to(root)
    except ValueError:
        raise SystemExit(f"Task directory {task_dir} is not inside repo root {root}")

    dest_task_dir = worktree_path / rel_task_path

    print(f"Task:       {task_id}")
    print(f"Branch:     {branch_name}")
    print(f"Worktree:   {worktree_path}")
    print(f"Task sync:  {task_dir}")
    print(f"         -> {dest_task_dir}")
    print()

    if args.print_only:
        _print_worktree_commands(branch_name, worktree_path, task_dir, dest_task_dir)
        meta["branch"] = branch_name
        save_meta(task_dir, meta)
        generate_board(print_result=False)
        print(f"Updated metadata.yaml: branch = {branch_name}")
        return

    worktree_existed = worktree_path.exists()
    if not worktree_existed:
        ok = _create_worktree(branch_name, worktree_path)
        worktree_existed = ok

    meta["branch"] = branch_name
    save_meta(task_dir, meta)
    generate_board(print_result=False)
    print(f"Updated metadata.yaml: branch = {branch_name}")

    if worktree_existed:
        _sync_task_folder(task_dir, dest_task_dir)

    print()
    print("Next steps:")
    print(f"  1. Open the worktree: {worktree_path}")
    print(f"  2. Verify branch:     git -C {worktree_path} branch --show-current")
    print(f"  3. Start executor in the worktree directory on branch {branch_name}")
    print()
    print("Cleanup when done:")
    print(f"  git worktree remove {worktree_path}")
    print(f"  git branch -d {branch_name}  # after merging")
