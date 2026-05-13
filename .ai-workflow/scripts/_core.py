"""
Core utilities: constants, path resolution, YAML, config, task lookup,
relationship helpers.  No imports from other workflow modules.
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


STATUSES = [
    "draft",
    "ready",
    "in_progress",
    "ready_for_review",
    "changes_requested",
    "done",
    "rejected",
]

# Legacy status directory names used before the stable-path migration.
# all_task_dirs() still reads tasks inside these dirs for backward compat.
_LEGACY_STATUS_DIRS = {
    "draft", "ready", "in_progress", "ready_for_review",
    "changes_requested", "ready_for_human", "done", "rejected",
}

DEFAULT_TRANSITIONS: Dict[str, List[str]] = {
    "draft": ["ready", "rejected"],
    "ready": ["in_progress", "rejected"],
    "in_progress": ["ready_for_review", "rejected"],
    "ready_for_review": ["changes_requested", "done", "rejected"],
    "changes_requested": ["ready_for_review", "rejected"],
    "done": ["changes_requested"],
    "rejected": [],
}

RELATIONSHIP_LIST_FIELDS = ["children", "blocks", "blocked_by", "related"]
RELATIONSHIP_KINDS = ["parent", "child", "blocks", "blocked-by", "related"]


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

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
    (wf / "tasks").mkdir(parents=True, exist_ok=True)
    for sub in ["templates", "skills", "scripts", "profiles"]:
        (wf / sub).mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Minimal YAML parser / dumper
# ---------------------------------------------------------------------------

def parse_simple_yaml_str(text: str) -> Dict[str, Any]:
    """
    Minimal YAML parser for this workflow's simple metadata files.

    Supports:
    - key: value
    - key: null / true / false
    - key: [a, b]
    - quoted strings
    - simple list blocks (  - item)

    For advanced YAML, install PyYAML and replace this function.
    """
    data: Dict[str, Any] = {}
    current_key: Optional[str] = None
    current_list: Optional[List[str]] = None

    for raw in text.splitlines():
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


def parse_simple_yaml(path: Path) -> Dict[str, Any]:
    """Read a YAML metadata file and parse it with parse_simple_yaml_str."""
    if not path.exists():
        return {}
    return parse_simple_yaml_str(path.read_text(encoding="utf-8"))


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


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Task discovery
# ---------------------------------------------------------------------------

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
    """Return all task directories.

    Supports two layouts:
    - Stable (new): tasks/<task-id>-<slug>/  (metadata.yaml present directly)
    - Legacy (old): tasks/<status>/<task-id>-<slug>/  (status encoded in dir name)

    Both layouts may coexist during migration.  Run `migrate` to move all tasks
    to the stable layout.
    """
    result = []
    root = tasks_root()
    if not root.exists():
        return result
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name in _LEGACY_STATUS_DIRS:
            # Legacy layout: iterate task folders inside this status dir
            for task_dir in sorted(child.iterdir()):
                if task_dir.is_dir() and (task_dir / "metadata.yaml").exists():
                    result.append(task_dir)
        elif (child / "metadata.yaml").exists():
            # Stable layout: task folder directly in tasks/
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


def allowed_transition(current: str, target: str) -> bool:
    if current == target:
        return True
    if target == "rejected" and current not in ("done", "rejected"):
        return True
    return target in DEFAULT_TRANSITIONS.get(current, [])


# ---------------------------------------------------------------------------
# Relationship utilities
# ---------------------------------------------------------------------------

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
