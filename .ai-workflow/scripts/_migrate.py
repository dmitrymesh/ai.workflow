"""Migrate legacy status-dir tasks to the stable flat task layout."""
from __future__ import annotations

import argparse
import shutil

from _board import generate_board
from _core import (
    _LEGACY_STATUS_DIRS,
    dump_simple_yaml,
    parse_simple_yaml,
    tasks_root,
    today,
    write_text,
)


def migrate(args: argparse.Namespace | None = None) -> None:
    """Move tasks from tasks/<status>/<id>/ to tasks/<id>/ (stable flat layout).

    Reads the legacy status directory name as the authoritative status and
    writes it into metadata.yaml before moving the folder.  Empty status
    directories are removed after all tasks inside them have been migrated.
    """
    root = tasks_root()
    if not root.exists():
        print("No tasks/ directory found.")
        return

    moved: int = 0
    skipped: int = 0

    for status_dir in sorted(root.iterdir()):
        if not status_dir.is_dir():
            continue
        if status_dir.name not in _LEGACY_STATUS_DIRS:
            continue

        for task_dir in sorted(status_dir.iterdir()):
            if not task_dir.is_dir():
                continue
            meta_path = task_dir / "metadata.yaml"
            if not meta_path.exists():
                print(f"  SKIP  {task_dir.name} (no metadata.yaml)")
                skipped += 1
                continue

            dest = root / task_dir.name
            if dest.exists():
                print(f"  SKIP  {task_dir.name} — flat path already exists")
                skipped += 1
                continue

            # Stamp metadata.status with the authoritative value from the folder path
            meta = parse_simple_yaml(meta_path)
            meta["status"] = status_dir.name
            meta["updated_at"] = today()
            write_text(meta_path, dump_simple_yaml(meta))

            shutil.move(str(task_dir), str(dest))
            print(f"  MOVED {status_dir.name}/{task_dir.name}  ->  {task_dir.name}")
            moved += 1

        # Remove now-empty legacy status directory
        try:
            status_dir.rmdir()
            print(f"  RMDIR {status_dir.name}/")
        except OSError:
            pass  # not empty — tasks were skipped or collided

    generate_board(print_result=False)
    print(f"\nMigration complete: {moved} moved, {skipped} skipped.")
