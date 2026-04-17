#!/usr/bin/env python3
"""Run the structured Obsidian second-brain setup workflow."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure ``setup_tasks`` is importable when running from the repo root.
SCRIPTS_DIR = Path(__file__).resolve().parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from setup_tasks.cli import build_options, parse_args
from setup_tasks.configure_clis import run as configure_clis
from setup_tasks.configure_skill_config import run as configure_skill_config
from setup_tasks.create_vault import run as create_vault
from setup_tasks.install_skills import run as install_skills
from setup_tasks.verify_setup import run as verify_setup
from setup_tasks.wizard import run_wizard

TASK_RUNNERS = {
    "install-skills": install_skills,
    "configure-skill-config": configure_skill_config,
    "create-vault": create_vault,
    "configure-clis": configure_clis,
    "verify-setup": verify_setup,
}


def main() -> int:
    """Execute the selected setup tasks in the requested order."""
    try:
        if len(sys.argv) == 1:
            return run_wizard(TASK_RUNNERS)

        arguments = parse_args()
        options = build_options(arguments)

        for task_index, task_name in enumerate(options.task_names, start=1):
            print(f"[{task_index}/{len(options.task_names)}] {task_name}")
            TASK_RUNNERS[task_name](options)
    except KeyboardInterrupt as error:
        print(error)
        return 130

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
