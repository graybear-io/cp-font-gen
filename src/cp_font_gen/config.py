"""Configuration loading and character collection."""

from pathlib import Path
from typing import Any

import yaml

from .utils import unicode_range_to_chars


def load_config(config_path: str) -> dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to YAML config file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    with open(config_path) as f:
        return yaml.safe_load(f)


def collect_characters(config: dict[str, Any], config_dir: Path = None) -> set[str]:
    """Collect all unique characters from various sources.

    Args:
        config: Configuration dictionary
        config_dir: Directory containing the config file (for resolving relative paths)

    Returns:
        Set of unique characters
    """
    chars = set()
    char_config = config.get("characters", {})

    # Add inline characters
    if "inline" in char_config:
        chars.update(char_config["inline"])

    # Load from file
    if "file" in char_config:
        file_path = Path(char_config["file"])

        # Resolve relative paths relative to config directory
        if config_dir and not file_path.is_absolute():
            file_path = (config_dir / file_path).resolve()

        if file_path.exists():
            with open(file_path, encoding="utf-8") as f:
                chars.update(f.read())

    # Add unicode ranges
    if "unicode_ranges" in char_config:
        for unicode_range in char_config["unicode_ranges"]:
            chars.update(unicode_range_to_chars(unicode_range))

    # Deduplicate if configured
    if config.get("deduplicate_chars", True):
        chars = set(chars)

    # Strip whitespace if configured
    if config.get("strip_whitespace", False):
        chars = {c for c in chars if not c.isspace()}

    return chars
