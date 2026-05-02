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

RELATIONSHIP_LIST_FIELDS = ["children", "blocks", "blocked_by", "related"]
RELATIONSHIP_KINDS = ["parent", "child", "blocks", "blocked-by", "related"]


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


def normalize_meta(meta: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure relationship fields have the expected types after a round-trip."""
    for key in RELATIONSHIP_LIST_FIELDS:
        value = meta.get(key)
        if not isinstance(value, list):
            meta[key] = []
    parent = meta.get("parent")
    if not parent or parent in ("null", "None"):
        meta["parent"] = None
    return meta


def load_meta(task_dir: Path) -> Dict[str, Any]:
    return normalize_meta(parse_simple_yaml(task_dir / "metadata.yaml"))


def save_meta(task_dir: Path, meta: Dict[str, Any]) -> None:
    meta["updated_at"] = today()
    write_text(task_dir / "metadata.yaml", dump_simple_yaml(meta))


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


def find_task_optional(task_id: str) -> Optional[Tuple[Path, Dict[str, Any]]]:
    try:
        return find_task(task_id)
    except SystemExit:
        return None


def normalize_kind(kind: str) -> str:
    return kind.replace("_", "-").strip().lower()


def add_unique(items: List[str], value: str) -> bool:
    if value in items:
        return False
    items.append(value)
    return True


def remove_if_present(items: List[str], value: str) -> bool:
    if value in items:
        items.remove(value)
        return True
    return False


def detach_existing_parent(child_id: str, child_meta: Dict[str, Any]) -> None:
    """If child already has a parent, remove the reciprocal entry on that parent."""
    old_parent_id = child_meta.get("parent")
    if not old_parent_id:
        return
    found = find_task_optional(old_parent_id)
    if not found:
        return
    old_dir, old_meta = found
    normalize_meta(old_meta)
    if remove_if_present(old_meta["children"], child_id):
        save_meta(old_dir, old_meta)


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
    print(f"  status:     {task_dir.parent.name}")
    print(f"  risk:       {meta.get('risk', '-')}")
    print(f"  area:       {area_str}")
    print(f"  branch:     {meta.get('branch') or '-'}")
    print(f"  parent:     {meta.get('parent') or '-'}")
    print(f"  children:   {fmt_list(meta['children'])}")
    print(f"  blocks:     {fmt_list(meta['blocks'])}")
    print(f"  blocked_by: {fmt_list(meta['blocked_by'])}")
    print(f"  related:    {fmt_list(meta['related'])}")
    print(f"  path:       {task_dir}")


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


def validate(args: Optional[argparse.Namespace] = None) -> None:
    ensure_structure()
    errors = []
    ids: Dict[str, Path] = {}
    metas: Dict[str, Dict[str, Any]] = {}

    for task_dir in all_task_dirs():
        status_dir = task_dir.parent.name
        meta_path = task_dir / "metadata.yaml"
        if not meta_path.exists():
            errors.append(f"Missing metadata.yaml: {task_dir}")
            continue

        meta = parse_simple_yaml(meta_path)
        normalize_meta(meta)
        task_id = meta.get("id")
        if not task_id:
            errors.append(f"Missing id in metadata.yaml: {task_dir}")
        else:
            if task_id in ids:
                errors.append(f"Duplicate task id {task_id}: {ids[task_id]} and {task_dir}")
            ids[task_id] = task_dir
            metas[task_id] = meta

        meta_status = meta.get("status")
        if meta_status != status_dir:
            errors.append(f"Status mismatch for {task_id}: folder={status_dir}, metadata={meta_status}")

        for required in ["task.md", "report.md", "review.md", "decision.yaml", "validation.md"]:
            if not (task_dir / required).exists():
                errors.append(f"Missing {required}: {task_dir}")

    all_ids = set(ids.keys())
    for task_id, meta in metas.items():
        parent = meta.get("parent")
        if parent and parent not in all_ids:
            errors.append(
                f"Relationship error in {task_id}: parent references missing task '{parent}'"
            )
        if parent == task_id:
            errors.append(f"Relationship error in {task_id}: parent references itself")

        for kind in RELATIONSHIP_LIST_FIELDS:
            for ref in meta.get(kind, []):
                if ref == task_id:
                    errors.append(
                        f"Relationship error in {task_id}: {kind} contains itself"
                    )
                    continue
                if ref not in all_ids:
                    errors.append(
                        f"Relationship error in {task_id}: {kind} references missing task '{ref}'"
                    )

        if parent and parent in all_ids:
            parent_children = metas[parent].get("children", [])
            if task_id not in parent_children:
                errors.append(
                    f"Reciprocity error: {task_id}.parent={parent} but {parent}.children "
                    f"does not contain {task_id}"
                )

        for child in meta.get("children", []):
            if child in all_ids:
                child_parent = metas[child].get("parent")
                if child_parent != task_id:
                    errors.append(
                        f"Reciprocity error: {task_id}.children contains {child} but "
                        f"{child}.parent={child_parent or 'null'}"
                    )

        for blocked in meta.get("blocks", []):
            if blocked in all_ids:
                if task_id not in metas[blocked].get("blocked_by", []):
                    errors.append(
                        f"Reciprocity error: {task_id}.blocks contains {blocked} but "
                        f"{blocked}.blocked_by does not contain {task_id}"
                    )

        for blocker in meta.get("blocked_by", []):
            if blocker in all_ids:
                if task_id not in metas[blocker].get("blocks", []):
                    errors.append(
                        f"Reciprocity error: {task_id}.blocked_by contains {blocker} but "
                        f"{blocker}.blocks does not contain {task_id}"
                    )

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

    p_link = sub.add_parser(
        "link",
        help="Add a relationship between two tasks (kind: parent|child|blocks|blocked-by|related)",
    )
    p_link.add_argument("task_id")
    p_link.add_argument("kind", choices=RELATIONSHIP_KINDS)
    p_link.add_argument("other_id")
    p_link.set_defaults(func=link_tasks)

    p_unlink = sub.add_parser(
        "unlink",
        help="Remove a relationship (omit other_id only when kind=parent)",
    )
    p_unlink.add_argument("task_id")
    p_unlink.add_argument("kind", choices=RELATIONSHIP_KINDS)
    p_unlink.add_argument("other_id", nargs="?")
    p_unlink.set_defaults(func=unlink_tasks)

    p_show = sub.add_parser("show", help="Show task details including relationships")
    p_show.add_argument("task_id")
    p_show.set_defaults(func=show_task)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
