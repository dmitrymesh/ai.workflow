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
    find_task_optional,
    next_task_id,
    normalize_meta,
    remove_if_present,
    render_template,
    save_meta,
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


def _unblock_dependent_tasks(completed_id: str, meta: dict) -> list:
    """Remove completed_id from blocked_by on every task it was blocking.

    Clears meta["blocks"] in place so the completed task's blocks list is empty.
    Returns the list of task IDs that were unblocked.
    """
    unblocked = []
    for dep_id in list(meta.get("blocks", [])):
        found = find_task_optional(dep_id)
        if not found:
            raise SystemExit(
                f"Cascade error: {completed_id}.blocks references missing task '{dep_id}'"
            )
        dep_dir, dep_meta = found
        normalize_meta(dep_meta)
        if remove_if_present(dep_meta["blocked_by"], completed_id):
            save_meta(dep_dir, dep_meta)
            unblocked.append(dep_id)
    meta["blocks"] = []
    return unblocked


def _cascade_parent_done(task_id: str) -> list:
    """If task_id's parent now has all children done, mark it done and recurse upward.

    Returns the list of parent task IDs that were auto-completed (in cascade order).
    """
    auto_done = []
    found = find_task_optional(task_id)
    if not found:
        raise SystemExit(f"Cascade error: completed task '{task_id}' not found after approval")
    _, task_meta = found
    normalize_meta(task_meta)
    parent_id = task_meta.get("parent")
    if not parent_id:
        return auto_done

    parent_found = find_task_optional(parent_id)
    if not parent_found:
        raise SystemExit(
            f"Cascade error: {task_id}.parent references missing task '{parent_id}'"
        )
    parent_dir, parent_meta = parent_found
    normalize_meta(parent_meta)

    if str(parent_meta.get("status") or "") == "done":
        return auto_done  # idempotent: already done

    children = parent_meta.get("children", [])
    if not children:
        return auto_done  # no children recorded: do not auto-close

    for sibling_id in children:
        sib_found = find_task_optional(sibling_id)
        if not sib_found:
            raise SystemExit(
                f"Cascade error: {parent_id}.children references missing task '{sibling_id}'"
            )
        _, sib_meta = sib_found
        if str(sib_meta.get("status") or "") != "done":
            return auto_done  # at least one sibling not done

    parent_meta["status"] = "done"
    _unblock_dependent_tasks(parent_id, parent_meta)  # clears parent_meta["blocks"]
    save_meta(parent_dir, parent_meta)
    auto_done.append(parent_id)
    auto_done.extend(_cascade_parent_done(parent_id))
    return auto_done


def review_task(args: argparse.Namespace) -> None:
    """Reviewer action: approve (-> done) or request changes (-> changes_requested)."""
    task_dir, meta = find_task(args.task_id)
    current_status = str(meta.get("status") or task_dir.parent.name)
    task_id = str(meta.get("id") or args.task_id)

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

    unblocked: list = []
    if args.approve:
        normalize_meta(meta)
        unblocked = _unblock_dependent_tasks(task_id, meta)

    write_text(task_dir / "metadata.yaml", dump_simple_yaml(meta))

    auto_done: list = []
    if args.approve:
        auto_done = _cascade_parent_done(task_id)

    generate_board(print_result=False)
    print(f"Reviewed {task_id}: {current_status} -> {target}")
    for dep_id in unblocked:
        print(f"  Unblocked: {dep_id}")
    for parent_id in auto_done:
        print(f"  Auto-completed parent: {parent_id}")


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
