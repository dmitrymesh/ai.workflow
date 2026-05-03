"""
Safe installation / upgrade plan for the Portable AI Task Protocol.

Usage:
  python .ai-workflow/scripts/ai_task.py install-plan <target-path>
  python .ai-workflow/scripts/ai_task.py install-plan <target-path> --apply
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import List, Tuple

from _core import repo_root

# Collision category constants
_CREATE = "CREATE"
_UPDATE = "UPDATE"
_UNCHANGED = "UNCHANGED"
_MERGE = "MERGE-REQUIRED"
_SKIP = "SKIP"

# Files that are always project-owned and never installed.
_PROJECT_OWNED = {"README.md"}

# Top-level files (relative to repo root) that are integration points:
# created from template if absent, never overwritten without human review.
_INTEGRATION_POINTS = {"AGENTS.md", "CLAUDE.md"}


def _iter_protocol_files(source: Path) -> List[Path]:
    """All .ai-workflow/ files that belong to the protocol (not project-specific)."""
    ai_wf = source / ".ai-workflow"
    result = []
    for p in sorted(ai_wf.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(ai_wf)
        parts = rel.parts
        # Skip tasks/ (project data), board.md (generated), __pycache__
        if parts[0] == "tasks":
            continue
        if rel == Path("board.md"):
            continue
        if any(part == "__pycache__" for part in parts):
            continue
        result.append(p)
    return result


def _iter_command_files(source: Path) -> List[Path]:
    commands_dir = source / ".claude" / "commands"
    if not commands_dir.exists():
        return []
    return sorted(f for f in commands_dir.iterdir() if f.is_file())


def _action(src: Path, dst: Path) -> str:
    if not dst.exists():
        return _CREATE
    try:
        if src.read_bytes() == dst.read_bytes():
            return _UNCHANGED
    except Exception:
        pass
    return _UPDATE


PlanItem = Tuple[str, Path, str]  # (category, rel_path, action)


def _build_plan(source: Path, target: Path) -> List[PlanItem]:
    items: List[PlanItem] = []

    # Protocol-owned: .ai-workflow/ files
    for src_file in _iter_protocol_files(source):
        rel = src_file.relative_to(source)
        dst = target / rel
        items.append(("PROTOCOL", rel, _action(src_file, dst)))

    # Integration points: AGENTS.md, CLAUDE.md
    for name in ["AGENTS.md", "CLAUDE.md"]:
        src_file = source / name
        if not src_file.exists():
            continue
        dst = target / name
        action = _CREATE if not dst.exists() else _MERGE
        items.append(("INTEGRATION", Path(name), action))

    # Commands
    for cmd_file in _iter_command_files(source):
        rel = cmd_file.relative_to(source)
        dst = target / rel
        action = _CREATE if not dst.exists() else _MERGE
        items.append(("COMMANDS", rel, action))

    # Project-owned: always skip
    items.append(("PROJECT", Path("README.md"), _SKIP))

    return items


def _print_plan(items: List[PlanItem], source: Path, target: Path) -> None:
    marker = {
        _CREATE: "+", _UPDATE: "~", _UNCHANGED: " ", _MERGE: "!", _SKIP: "-",
    }
    print("Install plan")
    print(f"  Source : {source}")
    print(f"  Target : {target}")
    print()

    for _cat, rel, action in items:
        m = marker[action]
        print(f"  [{m}] {action:<15}  {rel}")

    counts = {a: sum(1 for _, _, x in items if x == a)
              for a in (_CREATE, _UPDATE, _MERGE, _UNCHANGED, _SKIP)}
    print()
    print("  Summary:")
    print(f"    [+] CREATE         : {counts[_CREATE]}")
    print(f"    [~] UPDATE         : {counts[_UPDATE]}")
    print(f"    [!] MERGE-REQUIRED : {counts[_MERGE]}")
    print(f"    [ ] UNCHANGED      : {counts[_UNCHANGED]}")
    print(f"    [-] SKIP           : {counts[_SKIP]}")
    print()


def _merge_snippet_agents(existing: Path) -> None:
    print("--- Merge: AGENTS.md ---")
    print(f"  Existing file : {existing}")
    print("  Action        : append the following block (adapt to your project style)")
    print()
    print("  # --- append to AGENTS.md ---")
    print("  ## Portable AI Task Protocol")
    print("  #")
    print("  # > Adapter entrypoint for Codex-compatible / generic agent environments.")
    print("  # > For other tools, use a tool-specific adapter (e.g. CLAUDE.md) or read")
    print("  # > .ai-workflow/README.md directly.")
    print("  #")
    print("  # This repository uses the Portable AI Task Protocol.")
    print("  # Before managing, executing, or reviewing AI tasks:")
    print("  #")
    print("  # 1. Read `.ai-workflow/README.md`.")
    print("  # 2. Read `.ai-workflow/config.yaml` -- it defines which role this tool is assigned to.")
    print("  # 3. Read the role skill for your assigned role:")
    print("  #    - `.ai-workflow/skills/manager.md`")
    print("  #    - `.ai-workflow/skills/executor.md`")
    print("  #    - `.ai-workflow/skills/reviewer.md`")
    print("  # 4. Read the target task folder.")
    print("  #")
    print("  # General rules:")
    print("  # - Do not move tasks from `draft` to `ready` -- only a human may approve.")
    print("  # - Do not mark tasks as `done`.")
    print("  # - Do not expand task scope.")
    print("  # - Write `not run` when validation was not executed.")
    print("  # --- end append ---")
    print()


def _merge_snippet_claude(existing: Path) -> None:
    print("--- Merge: CLAUDE.md ---")
    print(f"  Existing file : {existing}")
    print("  Action        : append the following block (adapt to your project style)")
    print()
    print("  # --- append to CLAUDE.md ---")
    print("  ## AI Task Protocol")
    print("  #")
    print("  # > Claude Code adapter entrypoint. By default, Claude Code is assigned the executor role.")
    print("  # > Check `.ai-workflow/config.yaml` (`agents.executor.default_tool`) to confirm")
    print("  # > or change the role assignment.")
    print("  #")
    print("  # This repository uses `.ai-workflow/` for AI task execution.")
    print("  # Before executing a task:")
    print("  #")
    print("  # 1. Read `.ai-workflow/skills/executor.md`.")
    print("  # 2. Read the target task folder.")
    print("  # 3. Follow `task.md` exactly.")
    print("  #")
    print("  # Execution rules:")
    print("  # - Do not redesign the task.")
    print("  # - Do not expand scope.")
    print("  # - Before editing, list the files you plan to modify.")
    print("  # - Write `report.md` and `validation.md`.")
    print("  # - Move task to `ready_for_review` when complete.")
    print("  # - Never move a task to `done`.")
    print("  # --- end append ---")
    print()


def _merge_snippet_command(rel: Path, existing: Path) -> None:
    print(f"--- Merge: {rel} ---")
    print(f"  Existing file: {existing}")
    print("  Action: review both versions and keep the one that matches your workflow,")
    print("  or merge content manually. The protocol version is at:")
    print(f"    {repo_root() / rel}")
    print()


def _print_merge_snippets(items: List[PlanItem], target: Path) -> None:
    merge_items = [(cat, rel, a) for cat, rel, a in items if a == _MERGE]
    if not merge_items:
        return
    print("Merge instructions (review and apply manually):")
    print()
    for cat, rel, _ in merge_items:
        existing = target / rel
        if rel.name == "AGENTS.md":
            _merge_snippet_agents(existing)
        elif rel.name == "CLAUDE.md":
            _merge_snippet_claude(existing)
        else:
            _merge_snippet_command(rel, existing)


def _apply_plan(items: List[PlanItem], source: Path, target: Path) -> None:
    applied = 0
    skipped_merge = 0
    for cat, rel, action in items:
        if action in (_SKIP, _UNCHANGED, _MERGE):
            if action == _MERGE:
                skipped_merge += 1
            continue
        src_file = source / rel
        dst_file = target / rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src_file), str(dst_file))
        verb = "Created" if action == _CREATE else "Updated"
        print(f"  {verb}: {rel}")
        applied += 1
    print()
    print(f"Applied {applied} file(s).")
    if skipped_merge > 0:
        print(f"Skipped {skipped_merge} merge-required file(s) — review snippets above.")


def install_plan(args: argparse.Namespace) -> None:
    source = repo_root()
    target = Path(args.target).resolve()

    if not target.exists():
        raise SystemExit(f"Target path does not exist: {target}")
    if not target.is_dir():
        raise SystemExit(f"Target path is not a directory: {target}")

    if target == source:
        raise SystemExit("Source and target are the same directory.")

    items = _build_plan(source, target)

    _print_plan(items, source, target)
    _print_merge_snippets(items, target)

    if args.apply:
        print("Applying plan...")
        _apply_plan(items, source, target)
    else:
        actionable = sum(1 for _, _, a in items if a in (_CREATE, _UPDATE))
        merge_needed = sum(1 for _, _, a in items if a == _MERGE)
        if actionable:
            print(f"Run with --apply to create/update {actionable} protocol-owned file(s).")
        if merge_needed:
            print(f"{merge_needed} file(s) require manual merge (see snippets above).")
