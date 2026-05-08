"""Task relationship commands: link, unlink, show."""
from __future__ import annotations

import argparse
from typing import List

from _board import generate_board
from _core import (
    RELATIONSHIP_KINDS,
    add_unique,
    detach_existing_parent,
    find_task,
    find_task_optional,
    normalize_kind,
    normalize_meta,
    remove_if_present,
    save_meta,
)


def link_tasks(args: argparse.Namespace) -> None:
    kind = normalize_kind(args.kind)
    if kind not in RELATIONSHIP_KINDS:
        raise SystemExit(
            f"Unknown kind: {args.kind}. Allowed: {', '.join(RELATIONSHIP_KINDS)}"
        )

    task_dir, meta = find_task(args.task_id)
    other_dir, other_meta = find_task(args.other_id)
    normalize_meta(meta)
    normalize_meta(other_meta)

    task_id = str(meta.get("id"))
    other_id = str(other_meta.get("id"))

    if task_id == other_id:
        raise SystemExit("Cannot link a task to itself.")

    if kind == "parent":
        # task.parent = other; other.children += task
        if meta.get("parent") == other_id:
            print(f"{task_id} already has parent {other_id}.")
            return
        detach_existing_parent(task_id, meta)
        meta["parent"] = other_id
        add_unique(other_meta["children"], task_id)
    elif kind == "child":
        # task.children += other; other.parent = task
        if other_meta.get("parent") == task_id:
            print(f"{other_id} already has parent {task_id}.")
            return
        detach_existing_parent(other_id, other_meta)
        other_meta["parent"] = task_id
        add_unique(meta["children"], other_id)
    elif kind == "blocks":
        add_unique(meta["blocks"], other_id)
        add_unique(other_meta["blocked_by"], task_id)
    elif kind == "blocked-by":
        add_unique(meta["blocked_by"], other_id)
        add_unique(other_meta["blocks"], task_id)
    elif kind == "related":
        add_unique(meta["related"], other_id)
        add_unique(other_meta["related"], task_id)

    save_meta(task_dir, meta)
    save_meta(other_dir, other_meta)
    generate_board(print_result=False)
    print(f"Linked {task_id} {kind} {other_id}")


def unlink_tasks(args: argparse.Namespace) -> None:
    kind = normalize_kind(args.kind)
    if kind not in RELATIONSHIP_KINDS:
        raise SystemExit(
            f"Unknown kind: {args.kind}. Allowed: {', '.join(RELATIONSHIP_KINDS)}"
        )

    task_dir, meta = find_task(args.task_id)
    normalize_meta(meta)
    task_id = str(meta.get("id"))

    if kind == "parent":
        if not meta.get("parent"):
            print(f"{task_id} has no parent.")
            return
        old_parent_id = meta["parent"]
        meta["parent"] = None
        save_meta(task_dir, meta)
        found = find_task_optional(old_parent_id)
        if found:
            old_dir, old_meta = found
            normalize_meta(old_meta)
            if remove_if_present(old_meta["children"], task_id):
                save_meta(old_dir, old_meta)
        generate_board(print_result=False)
        print(f"Unlinked {task_id} parent (was {old_parent_id})")
        return

    if not args.other_id:
        raise SystemExit(f"unlink {kind} requires <other_id>")

    found = find_task_optional(args.other_id)
    other_dir = other_meta = None
    if found:
        other_dir, other_meta = found
        normalize_meta(other_meta)
    other_id = str(other_meta.get("id")) if other_meta else args.other_id

    if kind == "child":
        remove_if_present(meta["children"], other_id)
        if other_meta and other_meta.get("parent") == task_id:
            other_meta["parent"] = None
    elif kind == "blocks":
        remove_if_present(meta["blocks"], other_id)
        if other_meta:
            remove_if_present(other_meta["blocked_by"], task_id)
    elif kind == "blocked-by":
        remove_if_present(meta["blocked_by"], other_id)
        if other_meta:
            remove_if_present(other_meta["blocks"], task_id)
    elif kind == "related":
        remove_if_present(meta["related"], other_id)
        if other_meta:
            remove_if_present(other_meta["related"], task_id)

    save_meta(task_dir, meta)
    if other_dir is not None and other_meta is not None:
        save_meta(other_dir, other_meta)
    generate_board(print_result=False)
    print(f"Unlinked {task_id} {kind} {other_id}")


def show_task(args: argparse.Namespace) -> None:
    task_dir, meta = find_task(args.task_id)
    normalize_meta(meta)

    def fmt_list(values: List[str]) -> str:
        return ", ".join(values) if values else "-"

    area = meta.get("area")
    if isinstance(area, list):
        area_str = ", ".join(area) if area else "-"
    else:
        area_str = str(area) if area else "-"

    print(f"{meta.get('id', '?')}: {meta.get('title', task_dir.name)}")
    print(f"  status:     {meta.get('status') or task_dir.parent.name}")
    print(f"  risk:       {meta.get('risk', '-')}")
    print(f"  area:       {area_str}")
    print(f"  branch:     {meta.get('branch') or '-'}")
    print(f"  parent:     {meta.get('parent') or '-'}")
    print(f"  children:   {fmt_list(meta['children'])}")
    print(f"  blocks:     {fmt_list(meta['blocks'])}")
    print(f"  blocked_by: {fmt_list(meta['blocked_by'])}")
    print(f"  related:    {fmt_list(meta['related'])}")
    print(f"  path:       {task_dir}")
