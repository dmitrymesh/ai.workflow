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
    repo_root,
    save_meta,
    slugify,
    tasks_root,
    today,
    write_text,
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


def _print_worktree_commands(
    branch_name: str,
    worktree_path: Path,
    task_dir: Path,
    dest_task_dir: Path,
) -> None:
    print("Step 1 — create the worktree:")
    print(f"  git worktree add -b {branch_name} {worktree_path}")
    print()
    print("Step 2 — sync the approved task folder into the worktree:")
    if sys.platform == "win32":
        print(f'  xcopy /E /I /Y "{task_dir}" "{dest_task_dir}\\"')
    else:
        print(f'  cp -r "{task_dir}/" "{dest_task_dir}/"')
    print()
    print("Step 3 — open the executor in the worktree:")
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
    """Executor self-service claim: find a ready task, create a worktree, move to in_progress."""
    task_dir, meta = find_task(args.task_id)
    current_status = str(meta.get("status") or task_dir.parent.name)

    if current_status != "ready":
        raise SystemExit(
            f"Task {args.task_id} is not ready (current: {current_status}). "
            "Only ready tasks can be claimed."
        )

    if meta.get("branch"):
        raise SystemExit(
            f"Task {args.task_id} is already claimed on branch {meta['branch']}. "
            "Use that branch/worktree or clear the branch field to reclaim."
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
        meta["status"] = "in_progress"
        meta["updated_at"] = today()
        write_text(task_dir / "metadata.yaml", dump_simple_yaml(meta))
        generate_board(print_result=False)
        print(f"Updated metadata.yaml: branch = {branch_name}, status = in_progress")
        return

    ok = _create_worktree(branch_name, worktree_path)

    meta["branch"] = branch_name
    meta["status"] = "in_progress"
    meta["updated_at"] = today()
    write_text(task_dir / "metadata.yaml", dump_simple_yaml(meta))
    generate_board(print_result=False)
    print(f"Updated metadata.yaml: branch = {branch_name}, status = in_progress")

    if ok:
        _sync_task_folder(task_dir, dest_task_dir)

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
