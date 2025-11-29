"""Tool-wide configuration management."""

import os
from pathlib import Path
from typing import Any

import yaml


def get_tool_config_path() -> Path:
    """Get the path to the tool-wide config file.

    Returns:
        Path to ~/.config/cp-font-gen/config.yaml
    """
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        config_dir = Path(config_home) / "cp-font-gen"
    else:
        config_dir = Path.home() / ".config" / "cp-font-gen"

    return config_dir / "config.yaml"


def load_tool_config() -> dict[str, Any] | None:
    """Load tool-wide configuration if it exists.

    Returns:
        Tool configuration dict, or None if not found
    """
    config_path = get_tool_config_path()

    if not config_path.exists():
        return None

    try:
        with open(config_path) as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def get_default_output_dir() -> Path:
    """Get the default output directory for generated fonts.

    Checks tool config first, falls back to current working directory.

    Returns:
        Default output directory as Path
    """
    tool_config = load_tool_config()

    if tool_config and "output_directory" in tool_config:
        output_dir = Path(tool_config["output_directory"])
        # Expand ~ if present
        return output_dir.expanduser()

    # Default to current working directory
    return Path.cwd()
