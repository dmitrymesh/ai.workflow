"""Branch discovery commands for branch-first task workflow (AI-013).

Commands:
  list-branches          Scan task branches and print active task metadata.
  show-branch <TASK-ID>  Print metadata for a specific task branch.

Discovery is governed by workflow.discovery in config.yaml:
  scope:          local | remote | both  (default: local)
  remote:         git remote name        (default: origin)
  branch_prefix:  branch prefix          (default: ai/)
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from _core import parse_simple_yaml_str, repo_root, workflow_root


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _run_git(args: List[str], cwd: Optional[Path] = None) -> Tuple[bool, str]:
    """Run a git command. Returns (success, stdout_or_stderr)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=str(cwd or repo_root()),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, (result.stderr.strip() or result.stdout.strip())
    except FileNotFoundError:
        return False, "git is not available"


# ---------------------------------------------------------------------------
# Config parsing (indent-aware for nested workflow: block)
# ---------------------------------------------------------------------------

def _parse_workflow_config() -> Dict[str, Any]:
    """Parse the workflow: block from config.yaml.

    The minimal YAML parser in _core.py flattens nested keys, so this function
    uses indent-level tracking to parse the two-level workflow: hierarchy.
    """
    config_path = workflow_root() / "config.yaml"
    if not config_path.exists():
        return {}

    result: Dict[str, Any] = {}
    in_workflow = False
    current_section: Optional[str] = None

    for raw in config_path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())

        if indent == 0:
            in_workflow = (stripped == "workflow:")
            current_section = None
            continue

        if not in_workflow:
            continue

        if ":" not in stripped:
            continue

        key, _, val = stripped.partition(":")
        key = key.strip()
        val = val.strip()

        if indent == 2:
            current_section = key
            if val:
                result[key] = val.strip('"').strip("'")
            else:
                result[key] = {}
        elif indent == 4 and current_section is not None:
            if not isinstance(result.get(current_section), dict):
                result[current_section] = {}
            if val in ("null", "None", "~", ""):
                result[current_section][key] = None
            else:
                result[current_section][key] = val.strip('"').strip("'")

    return result


def _discovery_cfg() -> Dict[str, str]:
    """Return discovery config with defaults."""
    workflow = _parse_workflow_config()
    discovery = workflow.get("discovery", {})
    if not isinstance(discovery, dict):
        discovery = {}
    return {
        "scope": str(discovery.get("scope") or "local"),
        "remote": str(discovery.get("remote") or "origin"),
        "branch_prefix": str(discovery.get("branch_prefix") or "ai/"),
    }


# ---------------------------------------------------------------------------
# Branch enumeration
# ---------------------------------------------------------------------------

def _list_local_branches(prefix: str) -> List[str]:
    ok, out = _run_git(["branch", "--list", f"{prefix}*", "--format=%(refname:short)"])
    if not ok or not out:
        return []
    return [b.strip() for b in out.splitlines() if b.strip()]


def _list_remote_branches(prefix: str, remote: str) -> List[str]:
    ok, out = _run_git(
        ["branch", "-r", "--list", f"{remote}/{prefix}*", "--format=%(refname:short)"]
    )
    if not ok or not out:
        return []
    return [b.strip() for b in out.splitlines() if b.strip()]


def _merged_into_main() -> Tuple[set, set]:
    """Return (merged_local_set, merged_remote_set) — branch names merged into main."""
    ok_l, out_l = _run_git(["branch", "--merged", "main", "--format=%(refname:short)"])
    merged_local = {b.strip() for b in out_l.splitlines() if b.strip()} if ok_l else set()

    ok_r, out_r = _run_git(
        ["branch", "-r", "--merged", "main", "--format=%(refname:short)"]
    )
    merged_remote = {b.strip() for b in out_r.splitlines() if b.strip()} if ok_r else set()

    return merged_local, merged_remote


# ---------------------------------------------------------------------------
# Metadata reading from a branch
# ---------------------------------------------------------------------------

_TASK_ID_RE = re.compile(r"(AI-\d+)", re.IGNORECASE)


def _task_id_from_branch(branch: str) -> Optional[str]:
    """Extract task ID like 'AI-013' from 'ai/AI-013-slug' or 'origin/ai/AI-013-slug'."""
    m = _TASK_ID_RE.search(branch)
    return m.group(1).upper() if m else None


_LEGACY_STATUS_DIRS = {
    "draft", "ready", "in_progress", "ready_for_review",
    "changes_requested", "ready_for_human", "done", "rejected",
}


def _ls_task_folder_paths(branch: str) -> List[str]:
    """Return repo-relative paths for all task folders on the given branch.

    Handles both layouts:
    - Flat:   .ai-workflow/tasks/AI-009-slug
    - Legacy: .ai-workflow/tasks/done/AI-008-slug

    git ls-tree --name-only returns full repo-relative paths, which we use
    directly so callers never need to reconstruct the path.
    """
    ok, out = _run_git(["ls-tree", "--name-only", branch, ".ai-workflow/tasks/"])
    if not ok or not out:
        return []

    paths: List[str] = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        folder = Path(line).name
        if folder in _LEGACY_STATUS_DIRS:
            sub_ok, sub_out = _run_git(
                ["ls-tree", "--name-only", branch, f".ai-workflow/tasks/{folder}/"]
            )
            if sub_ok and sub_out:
                for sub_line in sub_out.splitlines():
                    sub_line = sub_line.strip()
                    if sub_line:
                        paths.append(sub_line)  # full path e.g. .ai-workflow/tasks/done/AI-008-...
        else:
            paths.append(line)  # full path e.g. .ai-workflow/tasks/AI-009-...
    return paths


def _read_task_meta_from_branch(
    branch: str, task_id: str
) -> Optional[Dict[str, Any]]:
    """Find and parse metadata.yaml for task_id on the given branch.

    Handles both the flat and legacy status-subdirectory layouts.
    Returns None if no matching folder or metadata.yaml is found — callers
    report this cleanly rather than crashing.
    """
    folder_paths = _ls_task_folder_paths(branch)
    for folder_path in folder_paths:
        folder_name = Path(folder_path).name
        if folder_name.upper().startswith(task_id.upper()):
            meta_path = f"{folder_path}/metadata.yaml"
            ok, content = _run_git(["show", f"{branch}:{meta_path}"])
            if ok and content:
                return parse_simple_yaml_str(content)
    return None


# ---------------------------------------------------------------------------
# Discovery engine
# ---------------------------------------------------------------------------

class BranchInfo:
    """Holds discovered metadata for one task branch."""

    def __init__(
        self,
        branch: str,
        task_id: Optional[str],
        is_remote_only: bool,
        is_merged: bool,
        meta: Optional[Dict[str, Any]],
    ) -> None:
        self.branch = branch
        self.task_id = task_id or "?"
        self.is_remote_only = is_remote_only
        self.is_merged = is_merged
        self.meta = meta

    @property
    def status(self) -> str:
        return str(self.meta.get("status") or "?") if self.meta else "?"

    @property
    def title(self) -> str:
        return str(self.meta.get("title") or self.branch) if self.meta else self.branch

    @property
    def blocked_by(self) -> List[str]:
        if not self.meta:
            return []
        v = self.meta.get("blocked_by", [])
        return v if isinstance(v, list) else []

    @property
    def parent(self) -> Optional[str]:
        return self.meta.get("parent") if self.meta else None

    @property
    def pr(self) -> Optional[str]:
        return self.meta.get("pr") if self.meta else None


def discover_all_branches() -> List[BranchInfo]:
    """Discover task branches per workflow.discovery config."""
    cfg = _discovery_cfg()
    scope = cfg["scope"]
    remote = cfg["remote"]
    prefix = cfg["branch_prefix"]

    local_names: List[str] = []
    remote_names: List[str] = []

    if scope in ("local", "both"):
        local_names = _list_local_branches(prefix)
    if scope in ("remote", "both"):
        remote_names = _list_remote_branches(prefix, remote)

    merged_local, merged_remote = _merged_into_main()

    seen_task_ids: set = set()
    entries: List[BranchInfo] = []

    for branch in local_names:
        task_id = _task_id_from_branch(branch)
        if task_id:
            seen_task_ids.add(task_id.upper())
        is_merged = branch in merged_local
        meta = _read_task_meta_from_branch(branch, task_id) if task_id else None
        entries.append(
            BranchInfo(branch, task_id, is_remote_only=False, is_merged=is_merged, meta=meta)
        )

    for branch in remote_names:
        task_id = _task_id_from_branch(branch)
        if task_id and task_id.upper() in seen_task_ids:
            continue  # prefer local copy
        is_merged = branch in merged_remote
        meta = _read_task_meta_from_branch(branch, task_id) if task_id else None
        entries.append(
            BranchInfo(branch, task_id, is_remote_only=True, is_merged=is_merged, meta=meta)
        )

    return entries


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _print_branch_group(label: str, entries: List[BranchInfo]) -> None:
    print(f"\n{label}")
    print("-" * max(len(label), 4))
    if not entries:
        print("  (none)")
        return
    for e in entries:
        remote_tag = " [remote-only]" if e.is_remote_only else ""
        if e.meta is None:
            print(f"  {e.branch}{remote_tag}")
            print("    (no valid task metadata — skipped)")
            continue
        blocked = ", ".join(e.blocked_by) if e.blocked_by else "-"
        parent = e.parent or "-"
        pr = e.pr or "-"
        print(f"  {e.branch}{remote_tag}")
        print(f"    id={e.task_id}  status={e.status}  title={e.title}")
        print(f"    parent={parent}  blocked_by={blocked}  pr={pr}")


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def list_branches(args: argparse.Namespace) -> None:
    """list-branches: scan task branches and print active task metadata."""
    ok, _ = _run_git(["rev-parse", "--git-dir"])
    if not ok:
        print("Error: git is not available or this is not a git repository.")
        return

    entries = discover_all_branches()
    cfg = _discovery_cfg()

    if not entries:
        print(
            f"No task branches found "
            f"(scope={cfg['scope']}, prefix={cfg['branch_prefix']})."
        )
        return

    active = [e for e in entries if not e.is_merged]
    merged = [e for e in entries if e.is_merged]

    print("Task branches (branch-first discovery)")
    print("=" * 60)
    print(f"scope={cfg['scope']}  prefix={cfg['branch_prefix']}")

    _print_branch_group("Active (unmerged)", active)
    if merged:
        _print_branch_group("Merged into main", merged)


def show_branch(args: argparse.Namespace) -> None:
    """show-branch AI-NNN: show task metadata from the task branch."""
    ok, _ = _run_git(["rev-parse", "--git-dir"])
    if not ok:
        print("Error: git is not available or this is not a git repository.")
        return

    task_id = args.task_id.strip().upper()
    cfg = _discovery_cfg()
    prefix = cfg["branch_prefix"]
    remote = cfg["remote"]
    scope = cfg["scope"]

    branch: Optional[str] = None

    if scope in ("local", "both"):
        for b in _list_local_branches(prefix):
            if _task_id_from_branch(b) == task_id:
                branch = b
                break

    if branch is None and scope in ("remote", "both"):
        for b in _list_remote_branches(prefix, remote):
            if _task_id_from_branch(b) == task_id:
                branch = b
                break

    if branch is None:
        print(
            f"No task branch found for {task_id} "
            f"(scope={scope}, prefix={prefix})."
        )
        return

    merged_local, merged_remote = _merged_into_main()
    is_merged = branch in merged_local or branch in merged_remote

    meta = _read_task_meta_from_branch(branch, task_id)

    print(f"Branch:          {branch}")
    print(f"Merged into main: {'yes' if is_merged else 'no'}")

    if meta is None:
        print("Task metadata:   not found (missing or invalid metadata.yaml)")
        return

    blocked_by = meta.get("blocked_by", [])
    blocked = ", ".join(blocked_by) if isinstance(blocked_by, list) and blocked_by else "-"
    area = meta.get("area", [])
    area_str = ", ".join(area) if isinstance(area, list) else str(area or "-")
    parent = meta.get("parent") or "-"
    pr = meta.get("pr") or "-"

    print(f"Task ID:         {meta.get('id', task_id)}")
    print(f"Title:           {meta.get('title', '?')}")
    print(f"Status:          {meta.get('status', '?')}")
    print(f"Risk:            {meta.get('risk', '-')}")
    print(f"Area:            {area_str}")
    print(f"Parent:          {parent}")
    print(f"Blocked by:      {blocked}")
    print(f"PR:              {pr}")
    if meta.get("branch"):
        print(f"Task branch:     {meta['branch']}")
