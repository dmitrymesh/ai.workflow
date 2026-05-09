#!/usr/bin/env python3
"""
Portable AI Task Protocol CLI.

Usage:
  python .ai-workflow/scripts/ai_task.py init --profile unity
  python .ai-workflow/scripts/ai_task.py create "Add RewardPreviewService" --risk low --area gameplay,tests
  python .ai-workflow/scripts/ai_task.py move AI-001 ready
  python .ai-workflow/scripts/ai_task.py claim AI-001
  python .ai-workflow/scripts/ai_task.py claim AI-001 --print-only
  python .ai-workflow/scripts/ai_task.py submit AI-001
  python .ai-workflow/scripts/ai_task.py review AI-001 --approve
  python .ai-workflow/scripts/ai_task.py review AI-001 --changes-requested
  python .ai-workflow/scripts/ai_task.py human-request-changes AI-001
  python .ai-workflow/scripts/ai_task.py human-request-changes AI-001 --feedback "Needs more tests"
  python .ai-workflow/scripts/ai_task.py migrate
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
  python .ai-workflow/scripts/ai_task.py roles
  python .ai-workflow/scripts/ai_task.py history
  python .ai-workflow/scripts/ai_task.py history --area workflow
  python .ai-workflow/scripts/ai_task.py history --keyword install
  python .ai-workflow/scripts/ai_task.py history --show AI-005
  python .ai-workflow/scripts/ai_task.py list-branches
  python .ai-workflow/scripts/ai_task.py show-branch AI-001
  python .ai-workflow/scripts/ai_task.py approve AI-001
  python .ai-workflow/scripts/ai_task.py approve AI-001 --print-only

Module layout (all under .ai-workflow/scripts/):
  _core.py          constants, path utils, YAML, config, task discovery, relationship utils
  _board.py         generate_board, list_tasks
  _validate.py      validate
  _tasks.py         create_task, move_task, submit_task, review_task, human_request_changes, print_task_path
  _relationships.py link_tasks, unlink_tasks, show_task
  _worktree.py      prepare_worktree, claim_task
  _migrate.py       migrate
  _install.py       install_plan
  _history.py       history
  _discovery.py     list_branches, show_branch  (branch-first task discovery)
  _approve.py       approve_task  (human-facing approve: draft -> ready on task branch)
  ai_task.py        init, build_parser, main  (this file — CLI entrypoint only)
"""

from __future__ import annotations

import argparse

from pathlib import Path

from _approve import approve_task
from _board import generate_board, list_tasks
from _core import RELATIONSHIP_KINDS, STATUSES, ensure_structure, load_config, update_config_profile, workflow_root
from _discovery import list_branches, show_branch
from _history import history
from _install import install_plan
from _migrate import migrate
from _relationships import link_tasks, show_task, unlink_tasks
from _tasks import create_task, human_request_changes, move_task, print_task_path, review_task, submit_task
from _validate import validate
from _worktree import claim_task, prepare_worktree


def _parse_agents_from_config(config_path: Path) -> dict:
    """Parse the agents block from config.yaml (handles nested YAML the simple parser skips)."""
    if not config_path.exists():
        return {}
    agents: dict = {}
    in_agents = False
    current_role: str | None = None
    for raw in config_path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0:
            in_agents = stripped == "agents:"
            current_role = None
            continue
        if not in_agents:
            continue
        if ":" not in stripped:
            continue
        key, _, val = stripped.partition(":")
        key = key.strip()
        val = val.strip()
        if indent == 2:
            current_role = key
            agents[current_role] = {}
        elif indent == 4 and current_role is not None:
            agents[current_role][key] = val
    return agents


def print_roles(args: argparse.Namespace) -> None:
    config_path = workflow_root() / "config.yaml"
    agents = _parse_agents_from_config(config_path)
    if not agents:
        print("No roles configured in .ai-workflow/config.yaml")
        return
    print(f"{'Role':<12} {'Tool':<20} Skill")
    print("-" * 60)
    for role, spec in agents.items():
        tool = spec.get("default_tool", "(not set)") if isinstance(spec, dict) else str(spec)
        skill = spec.get("skill", "(not set)") if isinstance(spec, dict) else "(not set)"
        print(f"{role:<12} {tool:<20} {skill}")


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

    p_move = sub.add_parser("move", help="Move a task to another status (low-level; prefer claim/submit/review)")
    p_move.add_argument("task_id")
    p_move.add_argument("status", choices=STATUSES)
    p_move.add_argument("--force", action="store_true")
    p_move.set_defaults(func=move_task)

    p_claim = sub.add_parser(
        "claim",
        help=(
            "Executor self-service claim: find a ready task, create a worktree on a new "
            "branch, sync the task folder, and move the task to in_progress."
        ),
    )
    p_claim.add_argument("task_id")
    p_claim.add_argument(
        "--print-only",
        action="store_true",
        help="Print the git commands instead of running them",
    )
    p_claim.set_defaults(func=claim_task)

    p_submit = sub.add_parser(
        "submit",
        help="Executor submit: record implementation complete, move in_progress/changes_requested -> ready_for_review",
    )
    p_submit.add_argument("task_id")
    p_submit.set_defaults(func=submit_task)

    p_review = sub.add_parser(
        "review",
        help="Reviewer decision: --approve moves ready_for_review -> done; --changes-requested moves to changes_requested",
    )
    p_review.add_argument("task_id")
    p_review.add_argument("--approve", action="store_true")
    p_review.add_argument("--changes-requested", action="store_true", dest="changes_requested")
    p_review.set_defaults(func=review_task)

    p_hrc = sub.add_parser(
        "human-request-changes",
        help="Human pre-merge: move done -> changes_requested with optional durable feedback in review.md",
    )
    p_hrc.add_argument("task_id")
    p_hrc.add_argument("--feedback", default=None, help="Feedback to append to review.md")
    p_hrc.set_defaults(func=human_request_changes)

    p_migrate = sub.add_parser(
        "migrate",
        help="Migrate tasks from the legacy status-by-directory layout to the stable flat layout",
    )
    p_migrate.set_defaults(func=migrate)

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
            "Prepare a task-specific git worktree without claiming. "
            "Legacy command: prefer 'claim' for the standard executor workflow. "
            "Does NOT move the task to in_progress."
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

    p_roles = sub.add_parser(
        "roles",
        help="Print configured role assignments (role, default_tool, skill path) from config.yaml",
    )
    p_roles.set_defaults(func=print_roles)

    p_history = sub.add_parser(
        "history",
        help=(
            "List completed (done) tasks. Filter by area or keyword, or read a "
            "specific task's report with --show."
        ),
    )
    p_history.add_argument("--area", default=None, help="Filter by area tag (e.g. workflow)")
    p_history.add_argument("--keyword", default=None, help="Filter titles by keyword")
    p_history.add_argument("--show", metavar="TASK_ID", default=None, help="Print report for a done task")
    p_history.set_defaults(func=history)

    p_list_branches = sub.add_parser(
        "list-branches",
        help=(
            "Branch-first discovery: scan task branches and print active task metadata. "
            "Scope is governed by workflow.discovery in config.yaml (default: local)."
        ),
    )
    p_list_branches.set_defaults(func=list_branches)

    p_show_branch = sub.add_parser(
        "show-branch",
        help=(
            "Branch-first discovery: show task metadata from a task branch without "
            "switching to it. Reads metadata.yaml directly from the branch."
        ),
    )
    p_show_branch.add_argument("task_id", help="Task ID to look up (e.g. AI-013)")
    p_show_branch.set_defaults(func=show_branch)

    p_approve = sub.add_parser(
        "approve",
        help=(
            "Human approve: move a draft task to ready on the task branch, "
            "from the main/control-plane checkout. Use --print-only to preview commands."
        ),
    )
    p_approve.add_argument("task_id", help="Task ID to approve (e.g. AI-021)")
    p_approve.add_argument(
        "--print-only",
        action="store_true",
        help="Print the git commands instead of running them",
    )
    p_approve.set_defaults(func=approve_task)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
