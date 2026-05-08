"""Focused regression tests for `show` command status output (AI-017).

Verifies that show_task reads status from metadata.yaml, not from
the parent folder name, so flat-layout tasks display the correct status.
"""
from __future__ import annotations

import argparse
import io
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))

from _core import dump_simple_yaml, today, write_text
from _relationships import show_task

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
        "blocks": [],
        "blocked_by": [],
        "related": [],
        "created_at": "2026-01-01",
        "updated_at": "2026-01-01",
    }
    write_text(task_dir / "metadata.yaml", dump_simple_yaml(meta))
    for stub in _STUBS:
        (task_dir / stub).write_text("", encoding="utf-8")
    return task_dir


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

    def _show_output(self, task_id: str) -> str:
        args = argparse.Namespace(task_id=task_id)
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            show_task(args)
            return mock_out.getvalue()


class TestShowStatusFromMetadata(_WorkflowBase):
    def test_show_reads_status_from_metadata_not_folder(self) -> None:
        """show must print the metadata.yaml status, not the parent folder name."""
        _make_task(self.tasks_dir, "AI-X", "task-x", "done")

        output = self._show_output("AI-X")

        self.assertIn("status:     done", output)
        self.assertNotIn("status:     tasks", output)

    def test_show_each_non_terminal_status(self) -> None:
        """show correctly reflects every non-terminal metadata status."""
        cases = [
            ("AI-S01", "task-s01", "draft"),
            ("AI-S02", "task-s02", "ready"),
            ("AI-S03", "task-s03", "in_progress"),
            ("AI-S04", "task-s04", "ready_for_review"),
            ("AI-S05", "task-s05", "changes_requested"),
        ]
        for task_id, title, status in cases:
            with self.subTest(status=status):
                _make_task(self.tasks_dir, task_id, title, status)
                output = self._show_output(task_id)
                self.assertIn(f"status:     {status}", output)

    def test_show_does_not_mutate_metadata(self) -> None:
        """show must not write to metadata.yaml."""
        task_dir = _make_task(self.tasks_dir, "AI-Y", "task-y", "ready_for_review")
        mtime_before = (task_dir / "metadata.yaml").stat().st_mtime

        self._show_output("AI-Y")

        mtime_after = (task_dir / "metadata.yaml").stat().st_mtime
        self.assertEqual(mtime_before, mtime_after)


if __name__ == "__main__":
    unittest.main()
