"""Focused tests for claim_task in branch-first and main-first modes (AI-019).

All git subprocess calls are mocked — no real repo is required.
"""
from __future__ import annotations

import argparse
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

sys.path.insert(0, str(Path(__file__).parent))

from _worktree import (
    _add_existing_worktree,
    _branch_exists_locally,
    _find_task_on_branch,
    _worktree_exists_for_branch,
    claim_task,
)

_ROOT = Path("/fake/repo")
_WT = Path("/fake/repo.worktrees/AI-001-fix-something")
_BRANCH = "ai/AI-001-fix-something"

_META_READY = {
    "id": "AI-001",
    "title": "Fix something",
    "status": "ready",
    "risk": "low",
    "branch": None,
    "blocked_by": [],
    "parent": None,
    "children": [],
    "blocks": [],
    "related": [],
    "created_at": "2026-01-01",
    "updated_at": "2026-01-01",
}

_META_READY_WITH_BRANCH = dict(_META_READY, branch=_BRANCH)


# ---------------------------------------------------------------------------
# _branch_exists_locally
# ---------------------------------------------------------------------------

class TestBranchExistsLocally(unittest.TestCase):
    def test_returns_true_when_branch_exists(self) -> None:
        mock_result = MagicMock(returncode=0)
        with patch("_worktree.subprocess.run", return_value=mock_result), \
             patch("_worktree.repo_root", return_value=_ROOT):
            self.assertTrue(_branch_exists_locally(_BRANCH))

    def test_returns_false_when_branch_missing(self) -> None:
        mock_result = MagicMock(returncode=1)
        with patch("_worktree.subprocess.run", return_value=mock_result), \
             patch("_worktree.repo_root", return_value=_ROOT):
            self.assertFalse(_branch_exists_locally(_BRANCH))


# ---------------------------------------------------------------------------
# _worktree_exists_for_branch
# ---------------------------------------------------------------------------

_PORCELAIN_WITH_WT = (
    "worktree /fake/repo\n"
    "HEAD abc\n"
    "branch refs/heads/main\n"
    "\n"
    f"worktree {_WT}\n"
    "HEAD def\n"
    f"branch refs/heads/{_BRANCH}\n"
)

_PORCELAIN_NO_WT = (
    "worktree /fake/repo\n"
    "HEAD abc\n"
    "branch refs/heads/main\n"
)


class TestWorktreeExistsForBranch(unittest.TestCase):
    def test_true_when_worktree_checked_out(self) -> None:
        mock_result = MagicMock(returncode=0, stdout=_PORCELAIN_WITH_WT)
        with patch("_worktree.subprocess.run", return_value=mock_result), \
             patch("_worktree.repo_root", return_value=_ROOT):
            self.assertTrue(_worktree_exists_for_branch(_BRANCH))

    def test_false_when_no_worktree(self) -> None:
        mock_result = MagicMock(returncode=0, stdout=_PORCELAIN_NO_WT)
        with patch("_worktree.subprocess.run", return_value=mock_result), \
             patch("_worktree.repo_root", return_value=_ROOT):
            self.assertFalse(_worktree_exists_for_branch(_BRANCH))

    def test_false_when_git_fails(self) -> None:
        mock_result = MagicMock(returncode=1, stdout="")
        with patch("_worktree.subprocess.run", return_value=mock_result), \
             patch("_worktree.repo_root", return_value=_ROOT):
            self.assertFalse(_worktree_exists_for_branch(_BRANCH))


# ---------------------------------------------------------------------------
# _add_existing_worktree
# ---------------------------------------------------------------------------

class TestAddExistingWorktree(unittest.TestCase):
    def test_success(self) -> None:
        mock_result = MagicMock(returncode=0)
        with patch("_worktree.subprocess.run", return_value=mock_result), \
             patch("_worktree.repo_root", return_value=_ROOT), \
             patch.object(Path, "exists", return_value=False):
            ok = _add_existing_worktree(_BRANCH, _WT)
        self.assertTrue(ok)

    def test_failure(self) -> None:
        exc = subprocess.CalledProcessError(1, "git", stderr="branch not found")
        with patch("_worktree.subprocess.run", side_effect=exc), \
             patch("_worktree.repo_root", return_value=_ROOT), \
             patch.object(Path, "exists", return_value=False):
            ok = _add_existing_worktree(_BRANCH, _WT)
        self.assertFalse(ok)

    def test_already_exists_returns_true(self) -> None:
        with patch.object(Path, "exists", return_value=True):
            ok = _add_existing_worktree(_BRANCH, _WT)
        self.assertTrue(ok)


# ---------------------------------------------------------------------------
# _find_task_on_branch
# ---------------------------------------------------------------------------

class TestFindTaskOnBranch(unittest.TestCase):
    def test_returns_branch_and_meta_when_found(self) -> None:
        with patch("_worktree._discovery_cfg",
                   return_value={"branch_prefix": "ai/"}), \
             patch("_worktree._list_local_branches",
                   return_value=[_BRANCH]), \
             patch("_worktree._task_id_from_branch",
                   return_value="AI-001"), \
             patch("_worktree._read_task_meta_from_branch",
                   return_value=_META_READY):
            result = _find_task_on_branch("AI-001")
        self.assertIsNotNone(result)
        branch, meta = result
        self.assertEqual(branch, _BRANCH)
        self.assertEqual(meta["status"], "ready")

    def test_returns_none_when_not_found(self) -> None:
        with patch("_worktree._discovery_cfg",
                   return_value={"branch_prefix": "ai/"}), \
             patch("_worktree._list_local_branches", return_value=[]), \
             patch("_worktree._task_id_from_branch", return_value=None):
            result = _find_task_on_branch("AI-099")
        self.assertIsNone(result)

    def test_returns_none_when_meta_unreadable(self) -> None:
        with patch("_worktree._discovery_cfg",
                   return_value={"branch_prefix": "ai/"}), \
             patch("_worktree._list_local_branches", return_value=[_BRANCH]), \
             patch("_worktree._task_id_from_branch", return_value="AI-001"), \
             patch("_worktree._read_task_meta_from_branch", return_value=None):
            result = _find_task_on_branch("AI-001")
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# claim_task integration tests
# ---------------------------------------------------------------------------

def _args(task_id="AI-001", print_only=False):
    return argparse.Namespace(task_id=task_id, print_only=print_only)


class _ClaimBase(unittest.TestCase):
    """Base with a temp filesystem for worktree metadata writes."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp()
        self._orig_cwd = os.getcwd()
        os.chdir(self._tmp)
        wf = Path(self._tmp) / ".ai-workflow"
        self.tasks_dir = wf / "tasks"
        self.tasks_dir.mkdir(parents=True)
        for sub in ["templates", "skills", "scripts", "profiles"]:
            (wf / sub).mkdir(parents=True)

    def tearDown(self) -> None:
        os.chdir(self._orig_cwd)
        shutil.rmtree(self._tmp)


class TestClaimMainFirst(_ClaimBase):
    """Main-first: task folder in main checkout, branch does not exist yet."""

    def _run_claim(self, apply=True):
        task_dir = self.tasks_dir / "AI-001-fix-something"
        task_dir.mkdir()
        from _core import dump_simple_yaml, write_text
        write_text(task_dir / "metadata.yaml", dump_simple_yaml(_META_READY))

        wt_path = Path(self._tmp + ".worktrees/AI-001-fix-something")

        with patch("_worktree.find_task",
                   return_value=(task_dir, dict(_META_READY))), \
             patch("_worktree._worktree_exists_for_branch", return_value=False), \
             patch("_worktree._branch_exists_locally", return_value=False), \
             patch("_worktree._branch_and_worktree_path",
                   return_value=(_BRANCH, wt_path)), \
             patch("_worktree.repo_root", return_value=Path(self._tmp)), \
             patch("_worktree._create_worktree", return_value=True), \
             patch("_worktree._sync_task_folder"), \
             patch("_worktree.generate_board"), \
             patch("sys.stdout", new_callable=io.StringIO):
            claim_task(_args())

        meta = __import__("_core").parse_simple_yaml(task_dir / "metadata.yaml")
        return meta

    def test_sets_status_to_in_progress(self) -> None:
        meta = self._run_claim()
        self.assertEqual(meta["status"], "in_progress")

    def test_uses_create_worktree_not_add_existing(self) -> None:
        task_dir = self.tasks_dir / "AI-001-fix-something"
        task_dir.mkdir()
        from _core import dump_simple_yaml, write_text
        write_text(task_dir / "metadata.yaml", dump_simple_yaml(_META_READY))
        wt_path = Path(self._tmp + ".worktrees/AI-001-fix-something")

        with patch("_worktree.find_task",
                   return_value=(task_dir, dict(_META_READY))), \
             patch("_worktree._worktree_exists_for_branch", return_value=False), \
             patch("_worktree._branch_exists_locally", return_value=False), \
             patch("_worktree._branch_and_worktree_path",
                   return_value=(_BRANCH, wt_path)), \
             patch("_worktree.repo_root", return_value=Path(self._tmp)), \
             patch("_worktree._create_worktree", return_value=True) as mock_create, \
             patch("_worktree._add_existing_worktree") as mock_add, \
             patch("_worktree._sync_task_folder"), \
             patch("_worktree.generate_board"), \
             patch("sys.stdout", new_callable=io.StringIO):
            claim_task(_args())

        mock_create.assert_called_once()
        mock_add.assert_not_called()


class TestClaimBranchFirst(_ClaimBase):
    """Branch-first: task not in main checkout, branch already exists."""

    def _make_worktree_task_dir(self, wt_path: Path) -> Path:
        slug = _BRANCH.split("/", 1)[-1]
        wt_task_dir = wt_path / ".ai-workflow" / "tasks" / slug
        wt_task_dir.mkdir(parents=True)
        from _core import dump_simple_yaml, write_text
        write_text(wt_task_dir / "metadata.yaml",
                   dump_simple_yaml(_META_READY_WITH_BRANCH))
        return wt_task_dir

    def test_uses_add_existing_not_create(self) -> None:
        wt_path = Path(self._tmp) / "worktrees" / "AI-001-fix-something"
        wt_path.mkdir(parents=True)
        self._make_worktree_task_dir(wt_path)

        with patch("_worktree.find_task", side_effect=SystemExit("not found")), \
             patch("_worktree._find_task_on_branch",
                   return_value=(_BRANCH, dict(_META_READY_WITH_BRANCH))), \
             patch("_worktree._worktree_exists_for_branch", return_value=False), \
             patch("_worktree._branch_exists_locally", return_value=True), \
             patch("_worktree._branch_and_worktree_path",
                   return_value=(_BRANCH, wt_path)), \
             patch("_worktree.repo_root", return_value=Path(self._tmp)), \
             patch("_worktree._add_existing_worktree", return_value=True) as mock_add, \
             patch("_worktree._create_worktree") as mock_create, \
             patch("_worktree.generate_board"), \
             patch("sys.stdout", new_callable=io.StringIO):
            claim_task(_args())

        mock_add.assert_called_once()
        mock_create.assert_not_called()

    def test_sets_status_in_worktree_metadata(self) -> None:
        wt_path = Path(self._tmp) / "worktrees" / "AI-001-fix-something"
        wt_path.mkdir(parents=True)
        wt_task_dir = self._make_worktree_task_dir(wt_path)

        with patch("_worktree.find_task", side_effect=SystemExit("not found")), \
             patch("_worktree._find_task_on_branch",
                   return_value=(_BRANCH, dict(_META_READY_WITH_BRANCH))), \
             patch("_worktree._worktree_exists_for_branch", return_value=False), \
             patch("_worktree._branch_exists_locally", return_value=True), \
             patch("_worktree._branch_and_worktree_path",
                   return_value=(_BRANCH, wt_path)), \
             patch("_worktree.repo_root", return_value=Path(self._tmp)), \
             patch("_worktree._add_existing_worktree", return_value=True), \
             patch("_worktree.generate_board"), \
             patch("sys.stdout", new_callable=io.StringIO):
            claim_task(_args())

        meta = __import__("_core").parse_simple_yaml(wt_task_dir / "metadata.yaml")
        self.assertEqual(meta["status"], "in_progress")


class TestClaimGuards(_ClaimBase):
    """Guards: wrong status, blocked, already-claimed worktree, not found."""

    def test_rejects_non_ready_status(self) -> None:
        meta = dict(_META_READY, status="in_progress")
        with patch("_worktree.find_task", return_value=(Path("/fake"), meta)), \
             self.assertRaises(SystemExit) as cm:
            claim_task(_args())
        self.assertIn("not ready", str(cm.exception))

    def test_rejects_blocked_task(self) -> None:
        meta = dict(_META_READY, blocked_by=["AI-000"])
        with patch("_worktree.find_task", return_value=(Path("/fake"), meta)), \
             self.assertRaises(SystemExit) as cm:
            claim_task(_args())
        self.assertIn("blocked", str(cm.exception))

    def test_rejects_when_worktree_already_exists(self) -> None:
        with patch("_worktree.find_task",
                   return_value=(Path("/fake"), dict(_META_READY))), \
             patch("_worktree._branch_and_worktree_path",
                   return_value=(_BRANCH, _WT)), \
             patch("_worktree._worktree_exists_for_branch", return_value=True), \
             self.assertRaises(SystemExit) as cm:
            claim_task(_args())
        self.assertIn("already has a worktree", str(cm.exception))

    def test_rejects_when_task_not_found_anywhere(self) -> None:
        with patch("_worktree.find_task", side_effect=SystemExit("not found")), \
             patch("_worktree._find_task_on_branch", return_value=None), \
             self.assertRaises(SystemExit) as cm:
            claim_task(_args())
        self.assertIn("not found", str(cm.exception))


class TestClaimPrintOnly(_ClaimBase):
    """--print-only shows the right git command based on branch existence."""

    def test_print_only_existing_branch_no_dash_b(self) -> None:
        with patch("_worktree.find_task", side_effect=SystemExit("not found")), \
             patch("_worktree._find_task_on_branch",
                   return_value=(_BRANCH, dict(_META_READY_WITH_BRANCH))), \
             patch("_worktree._worktree_exists_for_branch", return_value=False), \
             patch("_worktree._branch_exists_locally", return_value=True), \
             patch("_worktree._branch_and_worktree_path",
                   return_value=(_BRANCH, _WT)), \
             patch("_worktree.repo_root", return_value=_ROOT), \
             patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            claim_task(_args(print_only=True))
        output = mock_out.getvalue()
        self.assertIn("git worktree add", output)
        self.assertNotIn("-b", output)

    def test_print_only_new_branch_has_dash_b(self) -> None:
        task_dir = self.tasks_dir / "AI-001-fix-something"
        task_dir.mkdir()
        from _core import dump_simple_yaml, write_text
        write_text(task_dir / "metadata.yaml", dump_simple_yaml(_META_READY))

        with patch("_worktree.find_task",
                   return_value=(task_dir, dict(_META_READY))), \
             patch("_worktree._worktree_exists_for_branch", return_value=False), \
             patch("_worktree._branch_exists_locally", return_value=False), \
             patch("_worktree._branch_and_worktree_path",
                   return_value=(_BRANCH, _WT)), \
             patch("_worktree.repo_root", return_value=Path(self._tmp)), \
             patch("_worktree.generate_board"), \
             patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            claim_task(_args(print_only=True))
        output = mock_out.getvalue()
        self.assertIn("-b", output)


if __name__ == "__main__":
    unittest.main()
