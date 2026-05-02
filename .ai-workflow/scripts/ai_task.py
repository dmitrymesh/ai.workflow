#!/usr/bin/env python3
"""
Portable AI Task Protocol CLI.

Usage:
  python .ai-workflow/scripts/ai_task.py init --profile unity
  python .ai-workflow/scripts/ai_task.py create "Add RewardPreviewService" --risk low --area gameplay,tests
  python .ai-workflow/scripts/ai_task.py move AI-001 ready
  python .ai-workflow/scripts/ai_task.py list
  python .ai-workflow/scripts/ai_task.py board
  python .ai-workflow/scripts/ai_task.py validate
  python .ai-workflow/scripts/ai_task.py path AI-001
  python .ai-workflow/scripts/ai_task.py show AI-001
  python .ai-workflow/scripts/ai_task.py link AI-002 parent AI-001
  python .ai-workflow/scripts/ai_task.py unlink AI-002 parent
  python .ai-workflow/scripts/ai_task.py prepare-worktree AI-001
  python .ai-workflow/scripts/ai_task.py prepare-worktree AI-001 --print-only
  python .ai-workflow/scripts/ai_task.py install-plan /path/to/myproject
  python .ai-workflow/scripts/ai_task.py install-plan /path/to/myproject --apply

Module layout (all under .ai-workflow/scripts/):
  _core.py          constants, path utils, YAML, config, task discovery, relationship utils
  _board.py         generate_board, list_tasks
  _validate.py      validate
  _tasks.py         create_task, move_task, print_task_path
  _relationships.py link_tasks, unlink_tasks, show_task
  _worktree.py      prepare_worktree
  _install.py       install_plan
  ai_task.py        init, build_parser, main  (this file — CLI entrypoint only)
"""

from __future__ import annotations

import argparse

from _board import generate_board, list_tasks
from _core import RELATIONSHIP_KINDS, STATUSES, ensure_structure, load_config, update_config_profile
from _install import install_plan
from _relationships import link_tasks, show_task, unlink_tasks
from _tasks import create_task, move_task, print_task_path
from _validate import validate
from _worktree import prepare_worktree


def init(args: argparse.Namespace) -> None:
    ensure_structure()
    if args.profile:
        update_config_profile(args.profile)
    generate_board(print_result=False)
    print(f"Initialized .ai-workflow with profile={args.profile or load_config().get('profile', 'generic')}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Portable AI Task Protocol CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize workflow structure")
    p_init.add_argument("--profile", default="generic", choices=["generic", "unity"])
    p_init.set_defaults(func=init)

    p_create = sub.add_parser("create", help="Create a new draft task")
    p_create.add_argument("title")
    p_create.add_argument("--risk", default="medium", choices=["low", "medium", "high"])
    p_create.add_argument("--area", default="")
    p_create.set_defaults(func=create_task)

    p_move = sub.add_parser("move", help="Move a task to another status")
    p_move.add_argument("task_id")
    p_move.add_argument("status", choices=STATUSES)
    p_move.add_argument("--force", action="store_true")
    p_move.set_defaults(func=move_task)

    p_list = sub.add_parser("list", help="List tasks by status")
    p_list.set_defaults(func=list_tasks)

    p_board = sub.add_parser("board", help="Regenerate board.md")
    p_board.set_defaults(func=lambda args: generate_board(print_result=True))

    p_validate = sub.add_parser("validate", help="Validate workflow state")
    p_validate.set_defaults(func=validate)

    p_path = sub.add_parser("path", help="Print task folder path")
    p_path.add_argument("task_id")
    p_path.set_defaults(func=print_task_path)

    p_link = sub.add_parser(
        "link",
        help="Add a relationship between two tasks (kind: parent|child|blocks|blocked-by|related)",
    )
    p_link.add_argument("task_id")
    p_link.add_argument("kind", choices=RELATIONSHIP_KINDS)
    p_link.add_argument("other_id")
    p_link.set_defaults(func=link_tasks)

    p_unlink = sub.add_parser(
        "unlink",
        help="Remove a relationship (omit other_id only when kind=parent)",
    )
    p_unlink.add_argument("task_id")
    p_unlink.add_argument("kind", choices=RELATIONSHIP_KINDS)
    p_unlink.add_argument("other_id", nargs="?")
    p_unlink.set_defaults(func=unlink_tasks)

    p_show = sub.add_parser("show", help="Show task details including relationships")
    p_show.add_argument("task_id")
    p_show.set_defaults(func=show_task)

    p_prepare = sub.add_parser(
        "prepare-worktree",
        help=(
            "Prepare a task-specific git worktree for execution. "
            "Verifies the task is 'ready', computes branch/worktree names, "
            "creates the worktree, syncs the approved task folder, and records "
            "the branch in metadata.yaml."
        ),
    )
    p_prepare.add_argument("task_id")
    p_prepare.add_argument(
        "--print-only",
        action="store_true",
        help="Print the git commands instead of running them",
    )
    p_prepare.set_defaults(func=prepare_worktree)

    p_install = sub.add_parser(
        "install-plan",
        help=(
            "Show a safe installation/upgrade plan for copying the protocol into a target project. "
            "Use --apply to create/update protocol-owned files. "
            "Integration points (AGENTS.md, CLAUDE.md, .claude/commands/*) are never auto-overwritten."
        ),
    )
    p_install.add_argument("target", help="Path to the target project directory")
    p_install.add_argument(
        "--apply",
        action="store_true",
        help="Create/update protocol-owned files in the target (never overwrites integration points)",
    )
    p_install.set_defaults(func=install_plan)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
