"""Tests for prune-worktrees command (AI-024)."""
from __future__ import annotations

import argparse
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch

sys.path.insert(0, str(Path(__file__).parent))

from _prune import _WorktreeEntry, _is_dirty, _list_worktrees, prune_worktrees

_ROOT = Path("/fake/repo")
_WT_MERGED = Path("/fake/repo.worktrees/AI-008-slug")
_WT_ACTIVE = Path("/fake/repo.worktrees/AI-099-active")

# Porcelain output helpers
_PORCELAIN_MAIN_ONLY = (
    "worktree /fake/repo\n"
    "HEAD abc123\n"
    "branch refs/heads/main\n"
    "\n"
)

_PORCELAIN_WITH_MERGED = (
    "worktree /fake/repo\n"
    "HEAD abc123\n"
    "branch refs/heads/main\n"
    "\n"
    "worktree /fake/repo.worktrees/AI-008-slug\n"
    "HEAD def456\n"
    "branch refs/heads/ai/AI-008-slug\n"
    "\n"
    "worktree /fake/repo.worktrees/AI-099-active\n"
    "HEAD ghi789\n"
    "branch refs/heads/ai/AI-099-active\n"
    "\n"
)

_PORCELAIN_DETACHED = (
    "worktree /fake/repo\n"
    "HEAD abc123\n"
    "branch refs/heads/main\n"
    "\n"
    "worktree /fake/repo.worktrees/detached\n"
    "HEAD aaa\n"
    "detached\n"
    "\n"
)

_MERGED_LOCAL = {"ai/AI-008-slug", "main"}
_EMPTY_MERGED = (set(), set())
_SOME_MERGED = ({"ai/AI-008-slug", "main"}, set())


def _make_args(apply=False):
    return argparse.Namespace(apply=apply)


# ---------------------------------------------------------------------------
# _list_worktrees
# ---------------------------------------------------------------------------

class TestListWorktrees(unittest.TestCase):

    def test_parses_main_only(self) -> None:
        with patch("_prune._run_git", return_value=(True, _PORCELAIN_MAIN_ONLY)):
            entries = _list_worktrees(_ROOT)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].branch, "main")

    def test_parses_multiple_worktrees(self) -> None:
        with patch("_prune._run_git", return_value=(True, _PORCELAIN_WITH_MERGED)):
            entries = _list_worktrees(_ROOT)
        self.assertEqual(len(entries), 3)
        branches = [e.branch for e in entries]
        self.assertIn("ai/AI-008-slug", branches)
        self.assertIn("ai/AI-099-active", branches)

    def test_normalises_refs_heads_prefix(self) -> None:
        with patch("_prune._run_git", return_value=(True, _PORCELAIN_WITH_MERGED)):
            entries = _list_worktrees(_ROOT)
        for entry in entries:
            if entry.branch:
                self.assertFalse(entry.branch.startswith("refs/"),
                                 f"Branch not normalised: {entry.branch}")

    def test_detached_head_branch_is_none(self) -> None:
        with patch("_prune._run_git", return_value=(True, _PORCELAIN_DETACHED)):
            entries = _list_worktrees(_ROOT)
        detached = [e for e in entries if e.path == Path("/fake/repo.worktrees/detached")]
        self.assertEqual(len(detached), 1)
        self.assertIsNone(detached[0].branch)

    def test_returns_empty_on_git_failure(self) -> None:
        with patch("_prune._run_git", return_value=(False, "")):
            entries = _list_worktrees(_ROOT)
        self.assertEqual(entries, [])


# ---------------------------------------------------------------------------
# _is_dirty
# ---------------------------------------------------------------------------

class TestIsDirty(unittest.TestCase):

    def test_dirty_when_status_non_empty(self) -> None:
        with patch("_prune._run_git", return_value=(True, " M file.py")):
            self.assertTrue(_is_dirty(_WT_MERGED))

    def test_clean_when_status_empty(self) -> None:
        with patch("_prune._run_git", return_value=(True, "")):
            self.assertFalse(_is_dirty(_WT_MERGED))

    def test_dirty_when_git_fails(self) -> None:
        with patch("_prune._run_git", return_value=(False, "")):
            self.assertTrue(_is_dirty(_WT_MERGED))


# ---------------------------------------------------------------------------
# prune_worktrees — dry-run
# ---------------------------------------------------------------------------

class TestPruneWorktreesDryRun(unittest.TestCase):

    def _run(self, porcelain=_PORCELAIN_WITH_MERGED, merged=_SOME_MERGED):
        args = _make_args(apply=False)
        with patch("_prune._run_git", return_value=(True, "")), \
             patch("_prune.repo_root", return_value=_ROOT), \
             patch("_prune._merged_into_main", return_value=merged), \
             patch("_prune._list_worktrees", return_value=[
                 _WorktreeEntry(_ROOT, "main"),
                 _WorktreeEntry(_WT_MERGED, "ai/AI-008-slug"),
                 _WorktreeEntry(_WT_ACTIVE, "ai/AI-099-active"),
             ]), \
             patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            prune_worktrees(args)
        return mock_out.getvalue()

    def test_lists_merged_candidates(self) -> None:
        out = self._run()
        self.assertIn("AI-008-slug", out)

    def test_does_not_list_active_unmerged(self) -> None:
        out = self._run()
        self.assertNotIn("AI-099-active", out)

    def test_does_not_list_main_checkout(self) -> None:
        out = self._run()
        self.assertNotIn(str(_ROOT) + "  [main]", out)

    def test_no_candidates_message(self) -> None:
        out = self._run(merged=_EMPTY_MERGED)
        self.assertIn("No merged", out)

    def test_instructs_to_use_apply(self) -> None:
        out = self._run()
        self.assertIn("--apply", out)


# ---------------------------------------------------------------------------
# prune_worktrees — apply mode
# ---------------------------------------------------------------------------

class TestPruneWorktreesApply(unittest.TestCase):

    def _run(self, dirty=False, remove_ok=True):
        args = _make_args(apply=True)
        remove_result = (remove_ok, "" if remove_ok else "error removing")
        with patch("_prune._run_git", return_value=(True, "")), \
             patch("_prune.repo_root", return_value=_ROOT), \
             patch("_prune._merged_into_main", return_value=_SOME_MERGED), \
             patch("_prune._list_worktrees", return_value=[
                 _WorktreeEntry(_ROOT, "main"),
                 _WorktreeEntry(_WT_MERGED, "ai/AI-008-slug"),
             ]), \
             patch("_prune._is_dirty", return_value=dirty), \
             patch("_prune._remove_worktree", return_value=remove_result) as mock_rm, \
             patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            try:
                prune_worktrees(args)
            except SystemExit:
                pass
        return mock_rm, mock_out.getvalue()

    def test_removes_clean_merged_worktree(self) -> None:
        mock_rm, out = self._run(dirty=False, remove_ok=True)
        mock_rm.assert_called_once_with(_WT_MERGED, _ROOT)
        self.assertIn("Removed", out)

    def test_skips_dirty_worktree(self) -> None:
        mock_rm, out = self._run(dirty=True)
        mock_rm.assert_not_called()
        self.assertIn("SKIP", out)

    def test_removal_failure_reported(self) -> None:
        _, out = self._run(dirty=False, remove_ok=False)
        self.assertIn("FAILED", out)

    def test_removal_failure_exits_nonzero(self) -> None:
        args = _make_args(apply=True)
        with patch("_prune._run_git", return_value=(True, "")), \
             patch("_prune.repo_root", return_value=_ROOT), \
             patch("_prune._merged_into_main", return_value=_SOME_MERGED), \
             patch("_prune._list_worktrees", return_value=[
                 _WorktreeEntry(_ROOT, "main"),
                 _WorktreeEntry(_WT_MERGED, "ai/AI-008-slug"),
             ]), \
             patch("_prune._is_dirty", return_value=False), \
             patch("_prune._remove_worktree", return_value=(False, "err")), \
             patch("sys.stdout", new_callable=io.StringIO):
            with self.assertRaises(SystemExit) as cm:
                prune_worktrees(args)
        self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
