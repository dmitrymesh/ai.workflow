"""Tests for review_task auto-commit behavior (AI-020).

Git subprocess calls are mocked; real temp dirs are used for file existence.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent))

from _tasks import _commit_review_artifacts, review_task

_TASK_ID = "AI-020"
_TASK_DIR = Path("/fake/repo/.ai-workflow/tasks/AI-020-slug")


def _make_args(task_id=_TASK_ID, approve=False, changes_requested=False, no_commit=False):
    return argparse.Namespace(
        task_id=task_id,
        approve=approve,
        changes_requested=changes_requested,
        no_commit=no_commit,
    )


def _meta(status="ready_for_review"):
    return {"id": _TASK_ID, "status": status, "updated_at": "2026-01-01", "blocks": []}


# ---------------------------------------------------------------------------
# _commit_review_artifacts
# ---------------------------------------------------------------------------

class TestCommitReviewArtifacts(unittest.TestCase):

    def _setup(self, files_exist=None):
        """Return (tmp_dir_ctx, root, task_dir) with real files created."""
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        task_dir = root / ".ai-workflow" / "tasks" / "AI-020-slug"
        task_dir.mkdir(parents=True)
        if files_exist is None:
            files_exist = ["metadata.yaml", "review.md", "decision.yaml"]
        for f in files_exist:
            (task_dir / f).write_text("content")
        return tmp, root, task_dir

    def _run(self, decision="done", files_exist=None, staged_returncode=0,
             add_fail=False):
        tmp, root, task_dir = self._setup(files_exist)
        staged_check = MagicMock(returncode=staged_returncode)
        success = MagicMock(returncode=0, stderr="", stdout="")
        fail = MagicMock(returncode=1, stderr="git error", stdout="")

        def _subprocess_run(cmd, **kwargs):
            if cmd[:2] == ["git", "diff"]:
                return staged_check
            if add_fail and cmd[1] == "add":
                return fail
            return success

        with tmp:
            with patch("_tasks.repo_root", return_value=root), \
                 patch("subprocess.run", side_effect=_subprocess_run) as mock_run:
                _commit_review_artifacts(task_dir, _TASK_ID, decision)
        return mock_run, task_dir

    def test_stages_known_task_folder_files_only(self) -> None:
        mock_run, task_dir = self._run(staged_returncode=1)
        add_calls = [c for c in mock_run.call_args_list
                     if c.args[0][:2] == ["git", "add"]]
        self.assertEqual(len(add_calls), 1)
        staged_paths = add_calls[0].args[0][2:]
        for p in staged_paths:
            self.assertIn("AI-020-slug", p, f"Staged path outside task folder: {p}")

    def test_commits_with_correct_message_approve(self) -> None:
        mock_run, _ = self._run(decision="done", staged_returncode=1)
        commit_calls = [c for c in mock_run.call_args_list
                        if c.args[0][:2] == ["git", "commit"]]
        self.assertEqual(len(commit_calls), 1)
        msg = commit_calls[0].args[0][-1]
        self.assertIn("review:", msg)
        self.assertIn(_TASK_ID, msg)
        self.assertIn("done", msg)

    def test_commits_with_correct_message_changes_requested(self) -> None:
        mock_run, _ = self._run(decision="changes_requested", staged_returncode=1)
        commit_calls = [c for c in mock_run.call_args_list
                        if c.args[0][:2] == ["git", "commit"]]
        self.assertEqual(len(commit_calls), 1)
        self.assertIn("changes_requested", commit_calls[0].args[0][-1])

    def test_skips_commit_when_nothing_staged(self) -> None:
        # staged_returncode=0 → git diff --cached --quiet exits 0 → nothing staged
        mock_run, _ = self._run(staged_returncode=0)
        commit_calls = [c for c in mock_run.call_args_list
                        if c.args[0][:2] == ["git", "commit"]]
        self.assertEqual(len(commit_calls), 0)

    def test_only_stages_existing_files(self) -> None:
        # Only metadata.yaml was written
        mock_run, _ = self._run(files_exist=["metadata.yaml"], staged_returncode=1)
        add_calls = [c for c in mock_run.call_args_list
                     if c.args[0][:2] == ["git", "add"]]
        staged = add_calls[0].args[0][2:]
        self.assertEqual(len(staged), 1)
        self.assertTrue(staged[0].endswith("metadata.yaml"))

    def test_git_add_failure_raises_with_manual_instructions(self) -> None:
        tmp, root, task_dir = self._setup()
        fail = MagicMock(returncode=1, stderr="not a repo", stdout="")

        def _fail_add(cmd, **kwargs):
            if cmd[1] == "add":
                return fail
            return MagicMock(returncode=0)

        with tmp:
            with patch("_tasks.repo_root", return_value=root), \
                 patch("subprocess.run", side_effect=_fail_add):
                with self.assertRaises(SystemExit) as cm:
                    _commit_review_artifacts(task_dir, _TASK_ID, "done")
        self.assertIn("NOT committed", str(cm.exception))
        self.assertIn("git add", str(cm.exception))

    def test_task_dir_outside_root_raises(self) -> None:
        with patch("_tasks.repo_root", return_value=Path("/other/path")):
            with self.assertRaises(SystemExit) as cm:
                _commit_review_artifacts(
                    Path("/fake/repo/.ai-workflow/tasks/AI-020-slug"), _TASK_ID, "done"
                )
        self.assertIn("not inside repo root", str(cm.exception))


# ---------------------------------------------------------------------------
# review_task — integration tests
# ---------------------------------------------------------------------------

class TestReviewTask(unittest.TestCase):

    def _run_review(self, approve=False, changes_requested=False, no_commit=False,
                    commit_raises=False):
        args = _make_args(approve=approve, changes_requested=changes_requested,
                          no_commit=no_commit)
        meta = _meta()
        commit_effect = SystemExit("git failed") if commit_raises else None

        with patch("_tasks.find_task", return_value=(_TASK_DIR, meta)), \
             patch("_tasks._unblock_dependent_tasks", return_value=[]), \
             patch("_tasks._cascade_parent_done", return_value=[]), \
             patch("_tasks.write_text"), \
             patch("_tasks.generate_board"), \
             patch("_tasks._commit_review_artifacts",
                   side_effect=commit_effect) as mock_commit:
            review_task(args)
        return mock_commit

    def test_approve_triggers_commit_by_default(self) -> None:
        mock_commit = self._run_review(approve=True)
        mock_commit.assert_called_once_with(_TASK_DIR, _TASK_ID, "done")

    def test_changes_requested_triggers_commit_by_default(self) -> None:
        mock_commit = self._run_review(changes_requested=True)
        mock_commit.assert_called_once_with(_TASK_DIR, _TASK_ID, "changes_requested")

    def test_no_commit_skips_commit(self) -> None:
        mock_commit = self._run_review(approve=True, no_commit=True)
        mock_commit.assert_not_called()

    def test_review_requires_approve_or_changes_requested(self) -> None:
        args = _make_args()
        meta = _meta()
        with patch("_tasks.find_task", return_value=(_TASK_DIR, meta)):
            with self.assertRaises(SystemExit):
                review_task(args)

    def test_review_fails_if_not_ready_for_review(self) -> None:
        args = _make_args(approve=True)
        meta = _meta(status="in_progress")
        with patch("_tasks.find_task", return_value=(_TASK_DIR, meta)):
            with self.assertRaises(SystemExit):
                review_task(args)


if __name__ == "__main__":
    unittest.main()
