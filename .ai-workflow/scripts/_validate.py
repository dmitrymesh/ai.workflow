"""Workflow state validation."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, Optional

from _core import (
    RELATIONSHIP_LIST_FIELDS,
    STATUSES,
    _LEGACY_STATUS_DIRS,
    all_task_dirs,
    ensure_structure,
    normalize_meta,
    parse_simple_yaml,
)


def validate(args: Optional[argparse.Namespace] = None) -> None:
    ensure_structure()
    errors = []
    ids: Dict[str, Path] = {}
    metas: Dict[str, Dict[str, Any]] = {}

    for task_dir in all_task_dirs():
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
        if meta_status not in STATUSES:
            errors.append(f"Invalid status '{meta_status}' in {task_dir}")

        # For legacy layout tasks, also check folder/status consistency
        parent_name = task_dir.parent.name
        if parent_name in _LEGACY_STATUS_DIRS and parent_name != meta_status:
            errors.append(
                f"Status mismatch for {task_id}: "
                f"folder={parent_name}, metadata={meta_status} "
                f"(run 'migrate' to move to stable layout)"
            )

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
