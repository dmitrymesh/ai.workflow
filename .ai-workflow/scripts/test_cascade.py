"""Focused tests for review completion cascade (AI-016).

Covers:
  - blocked task becoming unblocked when blocker is approved
  - parent auto-closing when its final child is approved
  - ancestor cascade across two parent levels
  - parent remaining open when a sibling is not yet done
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _core import dump_simple_yaml, find_task, normalize_meta, today, write_text
from _tasks import review_task

_STUBS = ["task.md", "report.md", "review.md", "decision.yaml", "validation.md"]


def _make_task(tasks_dir: Path, task_id: str, title: str, status: str, **kwargs) -> Path:
    slug = title.lower().replace(" ", "-")
    task_dir = tasks_dir / f"{task_id}-{slug}"
    task_dir.mkdir(parents=True, exist_ok=True)
    meta: dict = {
        "id": task_id,
        "title": title,
        "status": status,
        "risk": "low",
        "parent": kwargs.get("parent"),
        "children": kwargs.get("children", []),
        "blocks": kwargs.get("blocks", []),
        "blocked_by": kwargs.get("blocked_by", []),
        "related": [],
        "created_at": "2026-01-01",
        "updated_at": "2026-01-01",
    }
    write_text(task_dir / "metadata.yaml", dump_simple_yaml(meta))
    for stub in _STUBS:
        (task_dir / stub).write_text("", encoding="utf-8")
    return task_dir


def _approve(task_id: str) -> None:
    args = argparse.Namespace(task_id=task_id, approve=True, changes_requested=False)
    review_task(args)


def _get_meta(task_id: str) -> dict:
    _, meta = find_task(task_id)
    normalize_meta(meta)
    return meta


class _WorkflowBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.mkdtemp()
        self._orig_cwd = os.getcwd()
        os.chdir(self._tmpdir)
        wf = Path(self._tmpdir) / ".ai-workflow"
        self.tasks_dir = wf / "tasks"
        self.tasks_dir.mkdir(parents=True)
        for sub in ["templates", "skills", "scripts", "profiles"]:
            (wf / sub).mkdir(parents=True)

    def tearDown(self) -> None:
        os.chdir(self._orig_cwd)
        shutil.rmtree(self._tmpdir)


class TestUnblockDownstream(_WorkflowBase):
    def test_blocked_task_unblocked_on_approval(self) -> None:
        """Approving A removes A from B.blocked_by and clears A.blocks."""
        _make_task(self.tasks_dir, "AI-A", "task-a", "ready_for_review", blocks=["AI-B"])
        _make_task(self.tasks_dir, "AI-B", "task-b", "ready", blocked_by=["AI-A"])

        _approve("AI-A")

        a = _get_meta("AI-A")
        b = _get_meta("AI-B")
        self.assertEqual(a["status"], "done")
        self.assertEqual(a["blocks"], [])
        self.assertEqual(b["blocked_by"], [])

    def test_idempotent_unblock(self) -> None:
        """Approving A when B.blocked_by is already empty does not corrupt state."""
        _make_task(self.tasks_dir, "AI-A", "task-a", "ready_for_review", blocks=[])
        _make_task(self.tasks_dir, "AI-B", "task-b", "ready", blocked_by=[])

        _approve("AI-A")

        a = _get_meta("AI-A")
        b = _get_meta("AI-B")
        self.assertEqual(a["status"], "done")
        self.assertEqual(a["blocks"], [])
        self.assertEqual(b["blocked_by"], [])


class TestAutoCompletedParentUnblocks(_WorkflowBase):
    def test_auto_completed_parent_unblocks_downstream(self) -> None:
        """Auto-completing parent P (via final child C) must unblock D if P blocked D."""
        _make_task(self.tasks_dir, "AI-P", "parent", "in_progress",
                   children=["AI-C"], blocks=["AI-D"])
        _make_task(self.tasks_dir, "AI-C", "child", "ready_for_review", parent="AI-P")
        _make_task(self.tasks_dir, "AI-D", "downstream", "ready", blocked_by=["AI-P"])

        _approve("AI-C")

        p = _get_meta("AI-P")
        d = _get_meta("AI-D")
        self.assertEqual(p["status"], "done")
        self.assertEqual(p["blocks"], [])
        self.assertEqual(d["blocked_by"], [])


class TestParentAutoCompletion(_WorkflowBase):
    def test_parent_closes_when_final_child_approved(self) -> None:
        """When the last in-flight child is approved, parent becomes done."""
        _make_task(self.tasks_dir, "AI-P", "parent", "in_progress",
                   children=["AI-C1", "AI-C2"])
        _make_task(self.tasks_dir, "AI-C1", "child-one", "done", parent="AI-P")
        _make_task(self.tasks_dir, "AI-C2", "child-two", "ready_for_review", parent="AI-P")

        _approve("AI-C2")

        p = _get_meta("AI-P")
        self.assertEqual(p["status"], "done")

    def test_parent_stays_open_when_sibling_not_done(self) -> None:
        """Parent is NOT auto-closed while any sibling is still in progress."""
        _make_task(self.tasks_dir, "AI-P", "parent", "in_progress",
                   children=["AI-C1", "AI-C2"])
        _make_task(self.tasks_dir, "AI-C1", "child-one", "in_progress", parent="AI-P")
        _make_task(self.tasks_dir, "AI-C2", "child-two", "ready_for_review", parent="AI-P")

        _approve("AI-C2")

        p = _get_meta("AI-P")
        self.assertNotEqual(p["status"], "done")


class TestAncestorCascade(_WorkflowBase):
    def test_cascade_across_two_parent_levels(self) -> None:
        """Approving the sole grandchild closes both parent and grandparent."""
        _make_task(self.tasks_dir, "AI-G", "grandparent", "in_progress",
                   children=["AI-P"])
        _make_task(self.tasks_dir, "AI-P", "parent", "in_progress",
                   parent="AI-G", children=["AI-C"])
        _make_task(self.tasks_dir, "AI-C", "child", "ready_for_review", parent="AI-P")

        _approve("AI-C")

        p = _get_meta("AI-P")
        g = _get_meta("AI-G")
        self.assertEqual(p["status"], "done")
        self.assertEqual(g["status"], "done")


if __name__ == "__main__":
    unittest.main()
