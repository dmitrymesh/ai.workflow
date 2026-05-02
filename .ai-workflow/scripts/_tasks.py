"""Task creation, movement, and path lookup commands."""
from __future__ import annotations

import argparse
import shutil

from _board import generate_board
from _core import (
    STATUSES,
    allowed_transition,
    dump_simple_yaml,
    ensure_structure,
    find_task,
    next_task_id,
    render_template,
    slugify,
    tasks_root,
    today,
    write_text,
)


def create_task(args: argparse.Namespace) -> None:
    ensure_structure()
    task_id = next_task_id()
    title = args.title.strip()
    slug = slugify(title)
    status = "draft"
    area_items = [item.strip() for item in (args.area or "").split(",") if item.strip()]
    area_yaml = "[" + ", ".join(area_items) + "]"

    values = {
        "id": task_id,
        "title": title,
        "status": status,
        "risk": args.risk,
        "area": area_yaml,
        "created_at": today(),
        "updated_at": today(),
    }

    task_dir = tasks_root() / status / f"{task_id}-{slug}"
    if task_dir.exists():
        raise SystemExit(f"Task directory already exists: {task_dir}")

    task_dir.mkdir(parents=True)
    for template_name in [
        "metadata.yaml",
        "task.md",
        "report.md",
        "review.md",
        "decision.yaml",
        "validation.md",
    ]:
        write_text(task_dir / template_name, render_template(template_name, values))

    generate_board(print_result=False)
    print(f"Created {task_id}: {task_dir}")


def move_task(args: argparse.Namespace) -> None:
    if args.status not in STATUSES:
        raise SystemExit(f"Unknown status: {args.status}. Allowed: {', '.join(STATUSES)}")

    task_dir, meta = find_task(args.task_id)
    current_status = task_dir.parent.name
    target_status = args.status

    if not args.force and not allowed_transition(current_status, target_status):
        raise SystemExit(
            f"Transition {current_status} -> {target_status} is not allowed. "
            f"Use --force to override."
        )

    target_dir = tasks_root() / target_status / task_dir.name
    if target_dir.exists():
        raise SystemExit(f"Target directory already exists: {target_dir}")

    meta["status"] = target_status
    meta["updated_at"] = today()
    write_text(task_dir / "metadata.yaml", dump_simple_yaml(meta))

    target_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(task_dir), str(target_dir))

    generate_board(print_result=False)
    print(f"Moved {meta.get('id', args.task_id)}: {current_status} -> {target_status}")


def print_task_path(args: argparse.Namespace) -> None:
    task_dir, _ = find_task(args.task_id)
    print(task_dir)
