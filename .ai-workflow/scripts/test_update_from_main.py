"""Focused tests for update-from-main command (AI-026).

Covers target selection, safety checks, and outcome reporting.
All git subprocess calls are mocked so no real git repo is required.
"""
from __future__ import annotations

import argparse
import io
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

sys.path.insert(0, str(Path(__file__).parent))

from _update_from_main import (
    _ACTIVE_STATUSES,
    _UpdateResult,
    _commits_main_ahead,
    _find_worktree_for_branch,
    _is_worktree_dirty,
    _merge_main,
    _process_branch,
    _worktree_add,
    _worktree_path_for_branch,
    _worktree_remove,
    update_from_main,
)

# Convenience: a fake root path used across tests
_ROOT = Path("/fake/repo")
_WT = Path("/fake/repo.worktrees/AI-001-task")

# Porcelain output for a worktree on branch ai/AI-001-task
_PORCELAIN_WITH_WT = (
    "worktree /fake/repo\n"
    "HEAD abc\n"
    "branch refs/heads/main\n"
    "\n"
    f"worktree {_WT}\n"
    "HEAD def\n"
    "branch refs/heads/ai/AI-001-task\n"
)

_PORCELAIN_NO_WT = (
    "worktree /fake/repo\n"
    "HEAD abc\n"
    "branch refs/heads/main\n"
)


# ---------------------------------------------------------------------------
# _find_worktree_for_branch
# ---------------------------------------------------------------------------

class TestFindWorktreeForBranch(unittest.TestCase):
    def test_returns_path_when_branch_has_worktree(self) -> None:
        with patch("_update_from_main._run_git", return_value=(True, _PORCELAIN_WITH_WT)):
            result = _find_worktree_for_branch("ai/AI-001-task", _ROOT)
        self.assertEqual(result, _WT)

    def test_returns_none_when_branch_has_no_worktree(self) -> None:
        with patch("_update_from_main._run_git", return_value=(True, _PORCELAIN_NO_WT)):
            result = _find_worktree_for_branch("ai/AI-001-task", _ROOT)
        self.assertIsNone(result)

    def test_returns_none_when_git_fails(self) -> None:
        with patch("_update_from_main._run_git", return_value=(False, "")):
            result = _find_worktree_for_branch("ai/AI-001-task", _ROOT)
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# _is_worktree_dirty
# ---------------------------------------------------------------------------

class TestIsWorktreeDirty(unittest.TestCase):
    def test_dirty_when_status_non_empty(self) -> None:
        with patch("_update_from_main._run_git", return_value=(True, " M somefile.py")):
            self.assertTrue(_is_worktree_dirty(_WT))

    def test_clean_when_status_empty(self) -> None:
        with patch("_update_from_main._run_git", return_value=(True, "")):
            self.assertFalse(_is_worktree_dirty(_WT))

    def test_dirty_when_git_fails(self) -> None:
        with patch("_update_from_main._run_git", return_value=(False, "")):
            self.assertTrue(_is_worktree_dirty(_WT))


# ---------------------------------------------------------------------------
# _commits_main_ahead
# ---------------------------------------------------------------------------

class TestCommitsMainAhead(unittest.TestCase):
    def test_returns_count(self) -> None:
        with patch("_update_from_main._run_git", return_value=(True, "3")):
            self.assertEqual(_commits_main_ahead("ai/AI-001-task", _ROOT), 3)

    def test_returns_zero_when_up_to_date(self) -> None:
        with patch("_update_from_main._run_git", return_value=(True, "0")):
            self.assertEqual(_commits_main_ahead("ai/AI-001-task", _ROOT), 0)

    def test_returns_minus_one_on_git_failure(self) -> None:
        with patch("_update_from_main._run_git", return_value=(False, "error")):
            self.assertEqual(_commits_main_ahead("ai/AI-001-task", _ROOT), -1)


# ---------------------------------------------------------------------------
# _merge_main
# ---------------------------------------------------------------------------

class TestMergeMain(unittest.TestCase):
    def test_success(self) -> None:
        mock_result = MagicMock(returncode=0, stdout="Already up to date.", stderr="")
        with patch("_update_from_main.subprocess.run", return_value=mock_result):
            ok, msg = _merge_main(_WT)
        self.assertTrue(ok)
        self.assertIn("Already up to date", msg)

    def test_conflict(self) -> None:
        mock_result = MagicMock(returncode=1, stdout="CONFLICT (content)", stderr="Automatic merge failed")
        with patch("_update_from_main.subprocess.run", return_value=mock_result):
            ok, msg = _merge_main(_WT)
        self.assertFalse(ok)
        self.assertIn("CONFLICT", msg)

    def test_git_not_found(self) -> None:
        with patch("_update_from_main.subprocess.run", side_effect=FileNotFoundError()):
            ok, msg = _merge_main(_WT)
        self.assertFalse(ok)
        self.assertIn("not available", msg)


# ---------------------------------------------------------------------------
# _process_branch — target selection and safety checks
# ---------------------------------------------------------------------------

class TestProcessBranch(unittest.TestCase):

    def _run(self, branch, task_id, apply, *, merged=False, worktree=_WT,
             ahead=2, dirty=False, merge_ok=True):
        """Run _process_branch with controllable sub-results."""
        merged_set = ({branch} if merged else set(), set())
        with patch("_update_from_main._merged_into_main", return_value=merged_set), \
             patch("_update_from_main._find_worktree_for_branch",
                   return_value=worktree), \
             patch("_update_from_main._commits_main_ahead", return_value=ahead), \
             patch("_update_from_main._is_worktree_dirty", return_value=dirty), \
             patch("_update_from_main._merge_main",
                   return_value=(merge_ok, "ok" if merge_ok else "CONFLICT details")):
            return _process_branch(branch, task_id, _ROOT, apply)

    def test_skips_merged_branch(self) -> None:
        r = self._run("ai/AI-001-task", "AI-001", apply=True, merged=True)
        self.assertEqual(r.outcome, "skipped_merged")

    def test_skips_branch_without_worktree(self) -> None:
        r = self._run("ai/AI-001-task", "AI-001", apply=True, worktree=None)
        self.assertEqual(r.outcome, "skipped_no_worktree")

    def test_already_current_when_zero_ahead(self) -> None:
        r = self._run("ai/AI-001-task", "AI-001", apply=True, ahead=0)
        self.assertEqual(r.outcome, "already_current")

    def test_error_when_rev_list_fails(self) -> None:
        r = self._run("ai/AI-001-task", "AI-001", apply=True, ahead=-1)
        self.assertEqual(r.outcome, "error")

    def test_skips_dirty_worktree(self) -> None:
        r = self._run("ai/AI-001-task", "AI-001", apply=True, dirty=True)
        self.assertEqual(r.outcome, "skipped_dirty")

    def test_dry_run_when_not_apply(self) -> None:
        r = self._run("ai/AI-001-task", "AI-001", apply=False)
        self.assertEqual(r.outcome, "dry_run")
        self.assertIn("--apply", r.detail)

    def test_updated_on_successful_merge(self) -> None:
        r = self._run("ai/AI-001-task", "AI-001", apply=True, merge_ok=True)
        self.assertEqual(r.outcome, "updated")

    def test_conflict_on_failed_merge(self) -> None:
        r = self._run("ai/AI-001-task", "AI-001", apply=True, merge_ok=False)
        self.assertEqual(r.outcome, "conflict")
        self.assertIn("resolve manually", r.detail)

    def test_dirty_check_before_dry_run(self) -> None:
        """Dirty worktrees are skipped even without --apply."""
        r = self._run("ai/AI-001-task", "AI-001", apply=False, dirty=True)
        self.assertEqual(r.outcome, "skipped_dirty")


# ---------------------------------------------------------------------------
# update_from_main handler
# ---------------------------------------------------------------------------

_BRANCH_FIRST_CFG = {"mode": "branch_first"}
_MAIN_FIRST_CFG = {"mode": "main_first"}
_ACTIVE_META = {"status": "in_progress"}
_DONE_META = {"status": "done"}


class TestUpdateFromMainHandler(unittest.TestCase):
    """Integration-level tests for the CLI handler."""

    def _make_args(self, task_id=None, update_all=False, apply=False):
        return argparse.Namespace(task_id=task_id, update_all=update_all, apply=apply)

    def _run_handler(self, args):
        with patch("_update_from_main._run_git", side_effect=[
            (True, ".git"),
            (True, "abc123"),
        ]), \
             patch("_update_from_main._parse_workflow_config",
                   return_value=_BRANCH_FIRST_CFG), \
             patch("_update_from_main.repo_root", return_value=_ROOT), \
             patch("_update_from_main._find_branch_for_task",
                   return_value="ai/AI-001-task"), \
             patch("_update_from_main._process_branch",
                   return_value=_UpdateResult("ai/AI-001-task", "AI-001",
                                              "dry_run", "2 commits pending")), \
             patch("sys.stdout", new_callable=io.StringIO):
            update_from_main(args)

    def test_requires_task_id_or_all(self) -> None:
        args = self._make_args()
        with self.assertRaises(SystemExit), \
             patch("_update_from_main._run_git", return_value=(True, "")), \
             patch("_update_from_main._parse_workflow_config",
                   return_value=_BRANCH_FIRST_CFG):
            update_from_main(args)

    def test_task_id_and_all_mutually_exclusive(self) -> None:
        args = self._make_args(task_id="AI-001", update_all=True)
        with self.assertRaises(SystemExit), \
             patch("_update_from_main._run_git", return_value=(True, "")), \
             patch("_update_from_main._parse_workflow_config",
                   return_value=_BRANCH_FIRST_CFG):
            update_from_main(args)

    def test_single_task_runs_process_branch(self) -> None:
        args = self._make_args(task_id="AI-001")
        with patch("_update_from_main._run_git", side_effect=[
            (True, ".git"), (True, "abc123"),
        ]), \
             patch("_update_from_main._parse_workflow_config",
                   return_value=_BRANCH_FIRST_CFG), \
             patch("_update_from_main.repo_root", return_value=_ROOT), \
             patch("_update_from_main._find_branch_for_task",
                   return_value="ai/AI-001-task") as mock_find, \
             patch("_update_from_main._process_branch",
                   return_value=_UpdateResult("ai/AI-001-task", "AI-001",
                                              "dry_run", "detail")) as mock_proc, \
             patch("sys.stdout", new_callable=io.StringIO):
            update_from_main(args)
        mock_find.assert_called_once_with("AI-001")
        mock_proc.assert_called_once()

    def test_all_scans_local_branches(self) -> None:
        branches = ["ai/AI-001-task", "ai/AI-002-other"]
        args = self._make_args(update_all=True)
        with patch("_update_from_main._run_git", side_effect=[
            (True, ".git"), (True, "abc123"),
        ]), \
             patch("_update_from_main._parse_workflow_config",
                   return_value=_BRANCH_FIRST_CFG), \
             patch("_update_from_main.repo_root", return_value=_ROOT), \
             patch("_update_from_main._list_local_branches",
                   return_value=branches), \
             patch("_update_from_main._read_task_meta_from_branch",
                   return_value=_ACTIVE_META), \
             patch("_update_from_main._process_branch",
                   side_effect=[
                       _UpdateResult("ai/AI-001-task", "AI-001", "dry_run", ""),
                       _UpdateResult("ai/AI-002-other", "AI-002", "skipped_merged", ""),
                   ]) as mock_proc, \
             patch("sys.stdout", new_callable=io.StringIO):
            update_from_main(args)
        self.assertEqual(mock_proc.call_count, 2)

    def test_all_skips_inactive_branches(self) -> None:
        """Branches with done/rejected status are skipped without calling _process_branch."""
        branches = ["ai/AI-001-task", "ai/AI-002-done"]
        args = self._make_args(update_all=True)
        with patch("_update_from_main._run_git", side_effect=[
            (True, ".git"), (True, "abc123"),
        ]), \
             patch("_update_from_main._parse_workflow_config",
                   return_value=_BRANCH_FIRST_CFG), \
             patch("_update_from_main.repo_root", return_value=_ROOT), \
             patch("_update_from_main._list_local_branches",
                   return_value=branches), \
             patch("_update_from_main._read_task_meta_from_branch",
                   side_effect=[_ACTIVE_META, _DONE_META]) as mock_meta, \
             patch("_update_from_main._process_branch",
                   return_value=_UpdateResult("ai/AI-001-task", "AI-001",
                                              "dry_run", "")) as mock_proc, \
             patch("sys.stdout", new_callable=io.StringIO):
            update_from_main(args)
        self.assertEqual(mock_proc.call_count, 1)
        # helper must be called with both branch and task_id
        mock_meta.assert_any_call("ai/AI-001-task", "AI-001")

    def test_main_first_mode_rejected(self) -> None:
        """update-from-main must exit with an error in main_first workflow mode."""
        args = self._make_args(task_id="AI-001")
        with self.assertRaises(SystemExit) as cm, \
             patch("_update_from_main._run_git", side_effect=[
                 (True, ".git"), (True, "abc123"),
             ]), \
             patch("_update_from_main._parse_workflow_config",
                   return_value=_MAIN_FIRST_CFG):
            update_from_main(args)
        self.assertNotEqual(cm.exception.code, 0)

    def test_empty_config_rejected(self) -> None:
        """No workflow.mode in config must also be rejected (default is main_first)."""
        args = self._make_args(task_id="AI-001")
        with self.assertRaises(SystemExit) as cm, \
             patch("_update_from_main._run_git", side_effect=[
                 (True, ".git"), (True, "abc123"),
             ]), \
             patch("_update_from_main._parse_workflow_config", return_value={}):
            update_from_main(args)
        self.assertNotEqual(cm.exception.code, 0)

    def test_exits_nonzero_on_conflict(self) -> None:
        args = self._make_args(task_id="AI-001", apply=True)
        with patch("_update_from_main._run_git", side_effect=[
            (True, ".git"), (True, "abc123"),
        ]), \
             patch("_update_from_main._parse_workflow_config",
                   return_value=_BRANCH_FIRST_CFG), \
             patch("_update_from_main.repo_root", return_value=_ROOT), \
             patch("_update_from_main._find_branch_for_task",
                   return_value="ai/AI-001-task"), \
             patch("_update_from_main._process_branch",
                   return_value=_UpdateResult("ai/AI-001-task", "AI-001",
                                              "conflict", "resolve manually")), \
             patch("sys.stdout", new_callable=io.StringIO):
            with self.assertRaises(SystemExit) as cm:
                update_from_main(args)
        self.assertEqual(cm.exception.code, 1)


# ---------------------------------------------------------------------------
# _worktree_path_for_branch
# ---------------------------------------------------------------------------

class TestWorktreePathForBranch(unittest.TestCase):
    def test_strips_prefix_and_formats_path(self) -> None:
        root = Path("/fake/myrepo")
        result = _worktree_path_for_branch("ai/AI-029-some-slug", root)
        self.assertEqual(result, Path("/fake/myrepo.worktrees/AI-029-some-slug"))

    def test_works_without_ai_prefix(self) -> None:
        root = Path("/fake/myrepo")
        result = _worktree_path_for_branch("AI-029-some-slug", root)
        self.assertEqual(result, Path("/fake/myrepo.worktrees/AI-029-some-slug"))


# ---------------------------------------------------------------------------
# _process_branch — no-worktree path (allow_no_worktree=True)
# ---------------------------------------------------------------------------

class TestProcessBranchNoWorktree(unittest.TestCase):

    _TEMP_PATH = Path("/fake/repo.worktrees/AI-001-task")

    def _run(self, apply, *, merged=False, ahead=2, add_ok=True, merge_ok=True,
             remove_ok=True):
        merged_set = ({"ai/AI-001-task"} if merged else set(), set())
        with patch("_update_from_main._merged_into_main", return_value=merged_set), \
             patch("_update_from_main._find_worktree_for_branch", return_value=None), \
             patch("_update_from_main._commits_main_ahead", return_value=ahead), \
             patch("_update_from_main._worktree_path_for_branch",
                   return_value=self._TEMP_PATH), \
             patch("_update_from_main._worktree_add",
                   return_value=(add_ok, "" if add_ok else "add failed")), \
             patch("_update_from_main._merge_main",
                   return_value=(merge_ok, "ok" if merge_ok else "CONFLICT details")), \
             patch("_update_from_main._worktree_remove",
                   return_value=(remove_ok, "")):
            return _process_branch("ai/AI-001-task", "AI-001", _ROOT, apply,
                                   allow_no_worktree=True)

    def test_skips_merged_branch(self) -> None:
        r = self._run(apply=True, merged=True)
        self.assertEqual(r.outcome, "skipped_merged")

    def test_already_current_when_zero_ahead(self) -> None:
        r = self._run(apply=True, ahead=0)
        self.assertEqual(r.outcome, "already_current")

    def test_error_when_rev_list_fails(self) -> None:
        r = self._run(apply=True, ahead=-1)
        self.assertEqual(r.outcome, "error")

    def test_dry_run_reports_temp_worktree(self) -> None:
        r = self._run(apply=False)
        self.assertEqual(r.outcome, "dry_run_no_worktree")
        self.assertIn("temporary worktree", r.detail)
        self.assertIn("--apply", r.detail)

    def test_apply_successful_cleans_up_worktree(self) -> None:
        r = self._run(apply=True, merge_ok=True)
        self.assertEqual(r.outcome, "updated")
        self.assertIn("cleaned up", r.detail)

    def test_apply_conflict_leaves_worktree_with_path(self) -> None:
        r = self._run(apply=True, merge_ok=False)
        self.assertEqual(r.outcome, "conflict")
        self.assertIn(str(self._TEMP_PATH), r.detail)
        self.assertIn("manual resolution", r.detail)

    def test_apply_worktree_add_failure_returns_error(self) -> None:
        r = self._run(apply=True, add_ok=False)
        self.assertEqual(r.outcome, "error")
        self.assertIn("temporary worktree", r.detail)

    def test_apply_successful_cleanup_failure_warns(self) -> None:
        r = self._run(apply=True, merge_ok=True, remove_ok=False)
        self.assertEqual(r.outcome, "updated")
        self.assertIn("WARNING", r.detail)
        self.assertIn(str(self._TEMP_PATH), r.detail)
        self.assertNotIn("cleaned up", r.detail)

    def test_default_allow_no_worktree_false_still_skips(self) -> None:
        """Without allow_no_worktree, no-worktree branches are still skipped."""
        merged_set = (set(), set())
        with patch("_update_from_main._merged_into_main", return_value=merged_set), \
             patch("_update_from_main._find_worktree_for_branch", return_value=None):
            r = _process_branch("ai/AI-001-task", "AI-001", _ROOT, False)
        self.assertEqual(r.outcome, "skipped_no_worktree")


# ---------------------------------------------------------------------------
# update_from_main handler — include_no_worktree flag
# ---------------------------------------------------------------------------

_BRANCH_FIRST_CFG = {"mode": "branch_first"}
_NO_WORKTREE_RESULT = _UpdateResult("ai/AI-002-nwt", "AI-002", "dry_run_no_worktree",
                                    "2 commits — temp worktree would be created")
_DRY_RUN_RESULT = _UpdateResult("ai/AI-001-task", "AI-001", "dry_run", "2 commits pending")


class TestUpdateFromMainNoWorktreeFlag(unittest.TestCase):
    """Tests that --include-no-worktree is threaded through to _process_branch."""

    def _make_args(self, task_id=None, update_all=False, apply=False,
                   include_no_worktree=False):
        return argparse.Namespace(task_id=task_id, update_all=update_all, apply=apply,
                                  include_no_worktree=include_no_worktree)

    def test_all_without_flag_passes_false(self) -> None:
        """--all without --include-no-worktree calls _process_branch with allow_no_worktree=False."""
        branches = ["ai/AI-001-task"]
        args = self._make_args(update_all=True)
        with patch("_update_from_main._run_git", side_effect=[
            (True, ".git"), (True, "abc123"),
        ]), \
             patch("_update_from_main._parse_workflow_config",
                   return_value=_BRANCH_FIRST_CFG), \
             patch("_update_from_main.repo_root", return_value=_ROOT), \
             patch("_update_from_main._list_local_branches", return_value=branches), \
             patch("_update_from_main._read_task_meta_from_branch",
                   return_value={"status": "in_progress"}), \
             patch("_update_from_main._process_branch",
                   return_value=_DRY_RUN_RESULT) as mock_proc, \
             patch("sys.stdout", new_callable=io.StringIO):
            update_from_main(args)
        mock_proc.assert_called_once_with(
            "ai/AI-001-task", "AI-001", _ROOT, False, allow_no_worktree=False
        )

    def test_all_with_flag_passes_true(self) -> None:
        """--all --include-no-worktree calls _process_branch with allow_no_worktree=True."""
        branches = ["ai/AI-002-nwt"]
        args = self._make_args(update_all=True, include_no_worktree=True)
        with patch("_update_from_main._run_git", side_effect=[
            (True, ".git"), (True, "abc123"),
        ]), \
             patch("_update_from_main._parse_workflow_config",
                   return_value=_BRANCH_FIRST_CFG), \
             patch("_update_from_main.repo_root", return_value=_ROOT), \
             patch("_update_from_main._list_local_branches", return_value=branches), \
             patch("_update_from_main._read_task_meta_from_branch",
                   return_value={"status": "ready"}), \
             patch("_update_from_main._process_branch",
                   return_value=_NO_WORKTREE_RESULT) as mock_proc, \
             patch("sys.stdout", new_callable=io.StringIO):
            update_from_main(args)
        mock_proc.assert_called_once_with(
            "ai/AI-002-nwt", "AI-002", _ROOT, False, allow_no_worktree=True
        )

    def test_single_task_always_passes_true(self) -> None:
        """Single-task mode always uses allow_no_worktree=True."""
        args = self._make_args(task_id="AI-001")
        with patch("_update_from_main._run_git", side_effect=[
            (True, ".git"), (True, "abc123"),
        ]), \
             patch("_update_from_main._parse_workflow_config",
                   return_value=_BRANCH_FIRST_CFG), \
             patch("_update_from_main.repo_root", return_value=_ROOT), \
             patch("_update_from_main._find_branch_for_task",
                   return_value="ai/AI-001-task"), \
             patch("_update_from_main._process_branch",
                   return_value=_DRY_RUN_RESULT) as mock_proc, \
             patch("sys.stdout", new_callable=io.StringIO):
            update_from_main(args)
        mock_proc.assert_called_once_with(
            "ai/AI-001-task", "AI-001", _ROOT, False, allow_no_worktree=True
        )


if __name__ == "__main__":
    unittest.main()
