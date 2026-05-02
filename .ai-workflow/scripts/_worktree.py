"""Git worktree preparation command."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from _board import generate_board
from _core import find_task, repo_root, save_meta, slugify


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


def prepare_worktree(args: argparse.Namespace) -> None:
    """Prepare a task-specific git worktree for execution."""
    task_dir, meta = find_task(args.task_id)
    current_status = task_dir.parent.name

    if current_status != "ready":
        raise SystemExit(
            f"Task {args.task_id} is not in 'ready' status (current: {current_status}). "
            "Only ready tasks can be prepared for execution."
        )

    task_id = str(meta.get("id"))

    # Derive slug from the folder name (strip task-id prefix)
    folder_name = task_dir.name
    prefix = task_id + "-"
    slug = folder_name[len(prefix):] if folder_name.startswith(prefix) else slugify(str(meta.get("title", "")))

    # Branch naming: ai/<task-id>-<slug>
    branch_name = f"ai/{task_id}-{slug}"

    # Worktree path: sibling directory to the repo root
    root = repo_root()
    repo_name = root.name
    worktrees_base = root.parent / f"{repo_name}.worktrees"
    worktree_path = worktrees_base / f"{task_id}-{slug}"

    # Compute relative task path from repo root for syncing
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
        # Still update metadata so the branch is recorded
        meta["branch"] = branch_name
        save_meta(task_dir, meta)
        generate_board(print_result=False)
        print(f"Updated metadata.yaml: branch = {branch_name}")
        return

    # Try to create the worktree
    worktree_existed = worktree_path.exists()
    if worktree_existed:
        print(f"Worktree directory already exists: {worktree_path}")
        print("Skipping git worktree add.")
    else:
        try:
            subprocess.run(
                ["git", "worktree", "add", "-b", branch_name, str(worktree_path)],
                cwd=str(root),
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"Created worktree at {worktree_path} on branch {branch_name}")
            worktree_existed = True
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            msg = getattr(exc, "stderr", str(exc)).strip()
            print(f"Could not create worktree automatically: {msg or exc}")
            print()
            print("Run these commands manually:")
            _print_worktree_commands(branch_name, worktree_path, task_dir, dest_task_dir)

    # Write the branch assignment to metadata.yaml BEFORE copying into the
    # worktree so the executor receives a task folder with branch already set.
    meta["branch"] = branch_name
    save_meta(task_dir, meta)
    generate_board(print_result=False)
    print(f"Updated metadata.yaml: branch = {branch_name}")

    if worktree_existed:
        # Sync task folder into worktree (explicit copy, no commit needed)
        dest_task_dir.parent.mkdir(parents=True, exist_ok=True)
        if dest_task_dir.exists():
            shutil.rmtree(str(dest_task_dir))
        shutil.copytree(str(task_dir), str(dest_task_dir))
        print(f"Synced task folder to {dest_task_dir}")

    print()
    print("Next steps:")
    print(f"  1. Open the worktree: {worktree_path}")
    print(f"  2. Verify branch:     git -C {worktree_path} branch --show-current")
    print(f"  3. Start executor in the worktree directory on branch {branch_name}")
    print()
    print("Cleanup when done:")
    print(f"  git worktree remove {worktree_path}")
    print(f"  git branch -d {branch_name}  # after merging")
