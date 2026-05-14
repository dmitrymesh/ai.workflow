"""Focused tests for the migrate command (no-op / flat-layout detection)."""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))

from _migrate import migrate


class _MigrateBase(unittest.TestCase):
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


class TestMigrateNoop(_MigrateBase):
    def test_noop_prints_flat_layout_message(self) -> None:
        """migrate in a repo with no legacy status dirs prints the already-flat message."""
        with patch("_migrate.generate_board"), patch("sys.stdout", new_callable=StringIO) as mock_out:
            migrate()
        output = mock_out.getvalue()
        self.assertIn("flat task layout", output)
        self.assertNotIn("moved", output)

    def test_noop_empty_tasks_dir(self) -> None:
        """migrate with a completely empty tasks/ dir also prints the already-flat message."""
        with patch("_migrate.generate_board"), patch("sys.stdout", new_callable=StringIO) as mock_out:
            migrate()
        self.assertIn("Nothing to migrate", mock_out.getvalue())


if __name__ == "__main__":
    unittest.main()
