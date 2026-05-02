"""
history command: read-only inspection of done task history.

Usage (via ai_task.py):
  python .ai-workflow/scripts/ai_task.py history
  python .ai-workflow/scripts/ai_task.py history --area workflow
  python .ai-workflow/scripts/ai_task.py history --keyword install
  python .ai-workflow/scripts/ai_task.py history --show AI-005
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional

from _core import load_meta, read_text, tasks_root


def _done_task_dirs() -> List[Path]:
    done = tasks_root() / "done"
    if not done.exists():
        return []
    return sorted(d for d in done.iterdir() if d.is_dir())


def history(args: argparse.Namespace) -> None:
    area_filter: Optional[str] = getattr(args, "area", None)
    keyword: Optional[str] = getattr(args, "keyword", None)
    show_id: Optional[str] = getattr(args, "show", None)

    dirs = _done_task_dirs()

    if show_id:
        show_id = show_id.strip().upper()
        for d in dirs:
            meta = load_meta(d)
            if (
                str(meta.get("id", "")).upper() == show_id
                or d.name.upper().startswith(show_id)
            ):
                area = meta.get("area", [])
                area_str = ", ".join(area) if isinstance(area, list) else str(area)
                print(f"# {meta.get('id', '?')} — {meta.get('title', d.name)}")
                print(f"Area:      {area_str}")
                print(f"Completed: {meta.get('updated_at', '?')}")
                print()
                report = read_text(d / "report.md")
                print(report if report else "(no report.md found)")
                return
        print(f"No done task found: {show_id}")
        return

    col_id = 10
    col_title = 48
    col_area = 28
    header = f"{'ID':<{col_id}} {'Title':<{col_title}} {'Area':<{col_area}} Date"
    print(header)
    print("-" * (col_id + 1 + col_title + 1 + col_area + 1 + 10))

    found = 0
    for d in dirs:
        meta = load_meta(d)
        task_id = str(meta.get("id", "?"))
        title = str(meta.get("title", d.name))
        area = meta.get("area", [])
        area_list = area if isinstance(area, list) else [str(area)]
        area_str = ", ".join(area_list)
        date = str(meta.get("updated_at", "?"))

        if area_filter and area_filter.lower() not in [a.lower() for a in area_list]:
            continue
        if keyword and keyword.lower() not in title.lower():
            continue

        if len(title) > col_title:
            title = title[: col_title - 1] + "..."
        if len(area_str) > col_area:
            area_str = area_str[: col_area - 1] + "..."

        print(f"{task_id:<{col_id}} {title:<{col_title}} {area_str:<{col_area}} {date}")
        found += 1

    if found == 0:
        print("(no matching done tasks)")
    else:
        print(f"\n{found} task(s).")
        print("To read a task report: python .ai-workflow/scripts/ai_task.py history --show <TASK-ID>")
