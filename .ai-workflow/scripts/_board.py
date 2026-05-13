"""Board generation and task listing."""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from _core import (
    STATUSES,
    all_task_dirs,
    ensure_structure,
    normalize_meta,
    parse_simple_yaml,
    workflow_root,
    write_text,
)
from _discovery import _parse_workflow_config


def _collect_by_status() -> Dict[str, List[Tuple[Path, dict]]]:
    tasks_by_status: Dict[str, List[Tuple[Path, dict]]] = {s: [] for s in STATUSES}
    for task_dir in all_task_dirs():
        meta = normalize_meta(parse_simple_yaml(task_dir / "metadata.yaml"))
        status = str(meta.get("status") or "draft")
        if status not in tasks_by_status:
            tasks_by_status[status] = []
        tasks_by_status[status].append((task_dir, meta))
    return tasks_by_status


def generate_board(print_result: bool = True) -> None:
    ensure_structure()
    tasks_by_status = _collect_by_status()

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
        for task_dir, meta in sorted(tasks_by_status.get(status, []), key=lambda x: x[0].name):
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
    workflow = _parse_workflow_config()
    if workflow.get("mode") == "branch_first":
        print(
            "Warning: workflow.mode is branch_first — active tasks live in task branches "
            "and will not appear here.\n"
            "Use: python .ai-workflow/scripts/ai_task.py list-branches",
            file=sys.stderr,
        )
    tasks_by_status = _collect_by_status()
    for status in STATUSES:
        print(f"\n{status}")
        print("-" * len(status))
        tasks = sorted(tasks_by_status.get(status, []), key=lambda x: x[0].name)
        if not tasks:
            print("(empty)")
            continue
        for task_dir, meta in tasks:
            parent = meta.get("parent") or "-"
            blocked_by = ", ".join(meta.get("blocked_by", [])) or "-"
            print(
                f"{meta.get('id', '?')} | {meta.get('title', task_dir.name)} | "
                f"risk={meta.get('risk', '-')} | parent={parent} | blocked_by={blocked_by}"
            )
