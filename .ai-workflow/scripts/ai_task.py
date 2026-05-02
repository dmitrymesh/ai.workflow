#!/usr/bin/env python3
"""
Portable AI Task Protocol CLI.

Usage:
  python .ai-workflow/scripts/ai_task.py init --profile unity
  python .ai-workflow/scripts/ai_task.py create "Add RewardPreviewService" --risk low --area gameplay,tests
  python .ai-workflow/scripts/ai_task.py move AI-001 ready
  python .ai-workflow/scripts/ai_task.py list
  python .ai-workflow/scripts/ai_task.py board
  python .ai-workflow/scripts/ai_task.py validate
  python .ai-workflow/scripts/ai_task.py path AI-001
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


STATUSES = [
    "draft",
    "ready",
    "in_progress",
    "ready_for_review",
    "changes_requested",
    "ready_for_human",
    "done",
    "rejected",
]

DEFAULT_TRANSITIONS = {
    "draft": ["ready", "rejected"],
    "ready": ["in_progress", "rejected"],
    "in_progress": ["ready_for_review", "rejected"],
    "ready_for_review": ["changes_requested", "ready_for_human", "rejected"],
    "changes_requested": ["in_progress", "rejected"],
    "ready_for_human": ["done", "changes_requested", "rejected"],
    "done": [],
    "rejected": [],
}


def repo_root() -> Path:
    current = Path.cwd()
    for path in [current, *current.parents]:
        if (path / ".ai-workflow").exists():
            return path
    return current


def workflow_root() -> Path:
    return repo_root() / ".ai-workflow"


def tasks_root() -> Path:
    return workflow_root() / "tasks"


def today() -> str:
    return dt.date.today().isoformat()


def slugify(title: str) -> str:
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9а-яё]+", "-", slug, flags=re.IGNORECASE)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:70] or "task"


def ensure_structure() -> None:
    wf = workflow_root()
    for status in STATUSES:
        (wf / "tasks" / status).mkdir(parents=True, exist_ok=True)
    for sub in ["templates", "skills", "scripts", "profiles"]:
        (wf / sub).mkdir(parents=True, exist_ok=True)


def read_text(path: Path, default: str = "") -> str:
    if not path.exists():
        return default
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_template(name: str, values: Dict[str, Any]) -> str:
    template_path = workflow_root() / "templates" / name
    text = read_text(template_path)
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def parse_simple_yaml(path: Path) -> Dict[str, Any]:
    """
    Minimal YAML parser for this workflow's simple metadata files.

    Supports:
    - key: value
    - key: null
    - key: [a, b]
    - quoted strings
    - simple nested blocks are treated as raw strings where possible

    For advanced YAML, install PyYAML and replace this function.
    """
    data: Dict[str, Any] = {}
    if not path.exists():
        return data

    lines = path.read_text(encoding="utf-8").splitlines()
    current_key = None
    current_list: Optional[List[str]] = None

    for raw in lines:
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue

        if line.startswith("  - ") and current_key:
            if current_list is None:
                current_list = []
                data[current_key] = current_list
            current_list.append(line[4:].strip().strip('"').strip("'"))
            continue

        if ":" not in line:
            continue

        current_list = None
        current_key = None
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value == "":
            current_key = key
            data[key] = {}
            continue

        if value in ("null", "None", "~"):
            data[key] = None
        elif value.lower() == "true":
            data[key] = True
        elif value.lower() == "false":
            data[key] = False
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if not inner:
                data[key] = []
            else:
                data[key] = [item.strip().strip('"').strip("'") for item in inner.split(",")]
        else:
            data[key] = value.strip('"').strip("'")

    return data


def dump_simple_yaml(data: Dict[str, Any]) -> str:
    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            else:
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
        elif value is None:
            lines.append(f"{key}: null")
        elif isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        else:
            text = str(value).replace('"', '\\"')
            lines.append(f'{key}: "{text}"')
    return "\n".join(lines) + "\n"


def load_config() -> Dict[str, Any]:
    config_path = workflow_root() / "config.yaml"
    config = parse_simple_yaml(config_path)
    # The minimal parser does not fully parse transitions, so keep defaults here.
    config.setdefault("profile", "generic")
    return config


def update_config_profile(profile: str) -> None:
    config_path = workflow_root() / "config.yaml"
    text = read_text(config_path)
    if not text:
        text = f"profile: {profile}\n"
    elif re.search(r"^profile:\s*.*$", text, flags=re.MULTILINE):
        text = re.sub(r"^profile:\s*.*$", f"profile: {profile}", text, flags=re.MULTILINE)
    else:
        text = f"profile: {profile}\n" + text
    write_text(config_path, text)


def next_task_id() -> str:
    max_num = 0
    for task_dir in all_task_dirs():
        meta = parse_simple_yaml(task_dir / "metadata.yaml")
        task_id = str(meta.get("id") or task_dir.name.split("-", 2)[0])
        match = re.match(r"AI-(\d+)", task_id)
        if match:
            max_num = max(max_num, int(match.group(1)))
    return f"AI-{max_num + 1:03d}"


def all_task_dirs() -> List[Path]:
    result = []
    root = tasks_root()
    if not root.exists():
        return result
    for status in STATUSES:
        status_dir = root / status
        if status_dir.exists():
            for child in sorted(status_dir.iterdir()):
                if child.is_dir():
                    result.append(child)
    return result


def find_task(task_id: str) -> Tuple[Path, Dict[str, Any]]:
    task_id = task_id.strip()
    matches = []
    for task_dir in all_task_dirs():
        meta = parse_simple_yaml(task_dir / "metadata.yaml")
        meta_id = str(meta.get("id") or "")
        if meta_id == task_id or task_dir.name.startswith(task_id):
            matches.append((task_dir, meta))

    if not matches:
        raise SystemExit(f"Task not found: {task_id}")
    if len(matches) > 1:
        paths = "\n".join(str(p) for p, _ in matches)
        raise SystemExit(f"Task ID is ambiguous: {task_id}\n{paths}")
    return matches[0]


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


def allowed_transition(current: str, target: str) -> bool:
    if current == target:
        return True
    if target == "rejected" and current not in ("done", "rejected"):
        return True
    return target in DEFAULT_TRANSITIONS.get(current, [])


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
            meta = parse_simple_yaml(task_dir / "metadata.yaml")
            print(f"{meta.get('id', '?')} | {meta.get('title', task_dir.name)} | risk={meta.get('risk', '-')}")
            found = True
        if not found:
            print("(empty)")


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
            meta = parse_simple_yaml(task_dir / "metadata.yaml")
            rows.append([
                str(meta.get("id", "?")),
                str(meta.get("title", task_dir.name)),
                str(meta.get("risk", "-")),
                ", ".join(meta.get("area", [])) if isinstance(meta.get("area"), list) else str(meta.get("area", "-")),
                str(meta.get("branch", "-") or "-"),
            ])

        if rows:
            lines.append("| ID | Title | Risk | Area | Branch |")
            lines.append("|---|---|---|---|---|")
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


def validate(args: Optional[argparse.Namespace] = None) -> None:
    ensure_structure()
    errors = []
    ids = {}

    for task_dir in all_task_dirs():
        status_dir = task_dir.parent.name
        meta_path = task_dir / "metadata.yaml"
        if not meta_path.exists():
            errors.append(f"Missing metadata.yaml: {task_dir}")
            continue

        meta = parse_simple_yaml(meta_path)
        task_id = meta.get("id")
        if not task_id:
            errors.append(f"Missing id in metadata.yaml: {task_dir}")
        else:
            if task_id in ids:
                errors.append(f"Duplicate task id {task_id}: {ids[task_id]} and {task_dir}")
            ids[task_id] = task_dir

        meta_status = meta.get("status")
        if meta_status != status_dir:
            errors.append(f"Status mismatch for {task_id}: folder={status_dir}, metadata={meta_status}")

        for required in ["task.md", "report.md", "review.md", "decision.yaml", "validation.md"]:
            if not (task_dir / required).exists():
                errors.append(f"Missing {required}: {task_dir}")

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("Validation passed.")


def print_task_path(args: argparse.Namespace) -> None:
    task_dir, _ = find_task(args.task_id)
    print(task_dir)


def init(args: argparse.Namespace) -> None:
    ensure_structure()
    if args.profile:
        update_config_profile(args.profile)
    generate_board(print_result=False)
    print(f"Initialized .ai-workflow with profile={args.profile or load_config().get('profile', 'generic')}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Portable AI Task Protocol CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize workflow structure")
    p_init.add_argument("--profile", default="generic", choices=["generic", "unity"])
    p_init.set_defaults(func=init)

    p_create = sub.add_parser("create", help="Create a new draft task")
    p_create.add_argument("title")
    p_create.add_argument("--risk", default="medium", choices=["low", "medium", "high"])
    p_create.add_argument("--area", default="")
    p_create.set_defaults(func=create_task)

    p_move = sub.add_parser("move", help="Move a task to another status")
    p_move.add_argument("task_id")
    p_move.add_argument("status", choices=STATUSES)
    p_move.add_argument("--force", action="store_true")
    p_move.set_defaults(func=move_task)

    p_list = sub.add_parser("list", help="List tasks by status")
    p_list.set_defaults(func=list_tasks)

    p_board = sub.add_parser("board", help="Regenerate board.md")
    p_board.set_defaults(func=lambda args: generate_board(print_result=True))

    p_validate = sub.add_parser("validate", help="Validate workflow state")
    p_validate.set_defaults(func=validate)

    p_path = sub.add_parser("path", help="Print task folder path")
    p_path.add_argument("task_id")
    p_path.set_defaults(func=print_task_path)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
