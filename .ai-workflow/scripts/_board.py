"""Board generation and task listing."""
from __future__ import annotations

import argparse
import datetime as dt

from _core import (
    STATUSES,
    ensure_structure,
    normalize_meta,
    parse_simple_yaml,
    tasks_root,
    workflow_root,
    write_text,
)


def generate_board(print_result: bool = True) -> None:
    ensure_structure()
    lines = []
    lines.append("# AI Task Board")
    lines.append("")
    lines.append(f"Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    for status in STATUSES:
        title = status.replace("_", " ").title()
        lines.append(f"## {title}")
        lines.append("")
        rows = []
        status_dir = tasks_root() / status
        for task_dir in sorted(status_dir.iterdir()) if status_dir.exists() else []:
            if not task_dir.is_dir():
                continue
            meta = normalize_meta(parse_simple_yaml(task_dir / "metadata.yaml"))
            blocked_by = ", ".join(meta.get("blocked_by", [])) or "-"
            rows.append([
                str(meta.get("id", "?")),
                str(meta.get("title", task_dir.name)),
                str(meta.get("risk", "-")),
                ", ".join(meta.get("area", [])) if isinstance(meta.get("area"), list) else str(meta.get("area", "-")),
                str(meta.get("branch", "-") or "-"),
                str(meta.get("parent") or "-"),
                blocked_by,
            ])

        if rows:
            lines.append("| ID | Title | Risk | Area | Branch | Parent | Blocked By |")
            lines.append("|---|---|---|---|---|---|---|")
            for row in rows:
                escaped = [cell.replace("|", "\\|") for cell in row]
                lines.append("| " + " | ".join(escaped) + " |")
        else:
            lines.append("_Empty_")
        lines.append("")

    board_path = workflow_root() / "board.md"
    write_text(board_path, "\n".join(lines) + "\n")
    if print_result:
        print(f"Generated {board_path}")


def list_tasks(args: argparse.Namespace) -> None:
    ensure_structure()
    for status in STATUSES:
        status_dir = tasks_root() / status
        print(f"\n{status}")
        print("-" * len(status))
        found = False
        for task_dir in sorted(status_dir.iterdir()) if status_dir.exists() else []:
            if not task_dir.is_dir():
                continue
            meta = normalize_meta(parse_simple_yaml(task_dir / "metadata.yaml"))
            parent = meta.get("parent") or "-"
            blocked_by = ", ".join(meta.get("blocked_by", [])) or "-"
            print(
                f"{meta.get('id', '?')} | {meta.get('title', task_dir.name)} | "
                f"risk={meta.get('risk', '-')} | parent={parent} | blocked_by={blocked_by}"
            )
            found = True
        if not found:
            print("(empty)")
