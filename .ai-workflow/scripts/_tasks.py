"""Task creation, movement, and path lookup commands."""
from __future__ import annotations

import argparse

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

    # Stable path: tasks/<id>-<slug>/  (status lives in metadata only)
    task_dir = tasks_root() / f"{task_id}-{slug}"
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
    """Update task status in metadata.yaml without moving the folder."""
    if args.status not in STATUSES:
        raise SystemExit(f"Unknown status: {args.status}. Allowed: {', '.join(STATUSES)}")

    task_dir, meta = find_task(args.task_id)
    # Authoritative status is in metadata; fall back to parent dir name for legacy tasks
    current_status = str(meta.get("status") or task_dir.parent.name)
    target_status = args.status

    if not args.force and not allowed_transition(current_status, target_status):
        raise SystemExit(
            f"Transition {current_status} -> {target_status} is not allowed. "
            f"Use --force to override."
        )

    meta["status"] = target_status
    meta["updated_at"] = today()
    write_text(task_dir / "metadata.yaml", dump_simple_yaml(meta))

    generate_board(print_result=False)
    print(f"Moved {meta.get('id', args.task_id)}: {current_status} -> {target_status}")


def submit_task(args: argparse.Namespace) -> None:
    """Executor submit: move task from in_progress or changes_requested to ready_for_review."""
    task_dir, meta = find_task(args.task_id)
    current_status = str(meta.get("status") or task_dir.parent.name)

    if current_status not in ("in_progress", "changes_requested"):
        raise SystemExit(
            f"submit requires task to be in_progress or changes_requested "
            f"(current: {current_status})"
        )

    meta["status"] = "ready_for_review"
    meta["updated_at"] = today()
    write_text(task_dir / "metadata.yaml", dump_simple_yaml(meta))
    generate_board(print_result=False)
    print(f"Submitted {meta.get('id', args.task_id)}: {current_status} -> ready_for_review")


def review_task(args: argparse.Namespace) -> None:
    """Reviewer action: approve (-> done) or request changes (-> changes_requested)."""
    task_dir, meta = find_task(args.task_id)
    current_status = str(meta.get("status") or task_dir.parent.name)

    if current_status != "ready_for_review":
        raise SystemExit(
            f"review requires task to be ready_for_review (current: {current_status})"
        )

    if args.approve:
        target = "done"
    elif args.changes_requested:
        target = "changes_requested"
    else:
        raise SystemExit("review requires --approve or --changes-requested")

    meta["status"] = target
    meta["updated_at"] = today()
    write_text(task_dir / "metadata.yaml", dump_simple_yaml(meta))
    generate_board(print_result=False)
    print(f"Reviewed {meta.get('id', args.task_id)}: {current_status} -> {target}")


def human_request_changes(args: argparse.Namespace) -> None:
    """Human pre-merge rejection: move done -> changes_requested with optional feedback."""
    task_dir, meta = find_task(args.task_id)
    current_status = str(meta.get("status") or task_dir.parent.name)

    if current_status != "done":
        raise SystemExit(
            f"human-request-changes requires task to be done (current: {current_status})"
        )

    meta["status"] = "changes_requested"
    meta["updated_at"] = today()
    write_text(task_dir / "metadata.yaml", dump_simple_yaml(meta))

    if getattr(args, "feedback", None):
        review_path = task_dir / "review.md"
        existing = review_path.read_text(encoding="utf-8") if review_path.exists() else ""
        feedback_block = f"\n\n## Human pre-merge request ({today()})\n\n{args.feedback}\n"
        write_text(review_path, existing + feedback_block)

    generate_board(print_result=False)
    print(f"Human request: {meta.get('id', args.task_id)}: {current_status} -> changes_requested")


def print_task_path(args: argparse.Namespace) -> None:
    task_dir, _ = find_task(args.task_id)
    print(task_dir)
