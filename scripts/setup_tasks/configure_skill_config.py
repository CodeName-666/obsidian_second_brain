"""Write the installed skill configuration for one concrete vault root."""

from __future__ import annotations

from setup_tasks.models import SetupOptions
from setup_tasks.shared import build_vault_roots, get_target_skill_path, load_base_config, write_json_file


def run(options: SetupOptions) -> None:
    """Configure the installed skill copies to point at the selected vault root."""
    base_config = load_base_config()
    configured_vault_roots = build_vault_roots(options.vault_root_path)

    for home_path in options.home_paths:
        for tool_name in options.tool_names:
            target_skill_path = get_target_skill_path(home_path, tool_name)

            if not target_skill_path.is_dir():
                raise FileNotFoundError(
                    "Cannot configure the installed skill before it exists: "
                    f"{target_skill_path}"
                )

            target_config_path = target_skill_path / "scripts" / "config.json"
            configured_config = dict(base_config)
            configured_config["vault_roots"] = configured_vault_roots
            write_json_file(target_config_path, configured_config)
            print(f"Configured {tool_name}:{target_config_path}")

