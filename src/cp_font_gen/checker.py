"""Tool validation and version checking."""

import subprocess
from importlib.metadata import version as get_version


def check_command_exists(cmd: str) -> tuple[bool, str | None]:
    """Check if a command exists and get its version.

    Args:
        cmd: Command name to check

    Returns:
        Tuple of (exists, version_string)
    """
    try:
        # Check if command exists
        result = subprocess.run(["which", cmd], capture_output=True, text=True)
        if result.returncode != 0:
            return False, None

        # Try to get version
        version = None
        try:
            version_result = subprocess.run(
                [cmd, "--version"], capture_output=True, text=True, timeout=2
            )
            version = version_result.stdout.strip().split("\n")[0]
        except Exception:
            pass

        return True, version
    except Exception:
        return False, None


def check_python_package(package: str) -> tuple[bool, str | None]:
    """Check if a Python package is installed and get its version.

    Args:
        package: Package name to check

    Returns:
        Tuple of (exists, version_string)
    """
    try:
        # Try to import the package to verify it exists
        if package == "fonttools":
            import fontTools  # noqa: F401
        elif package == "pyyaml":
            import yaml  # noqa: F401
        elif package == "click":
            import click  # noqa: F401
        else:
            return False, None

        # Get version via importlib.metadata
        try:
            pkg_version = get_version(package)
            return True, pkg_version
        except Exception:
            return True, None
    except ImportError:
        return False, None


def get_tool_requirements():
    """Get list of required tools and packages.

    Returns:
        Dict of tool categories and their requirements
    """
    return {
        "System Commands": [
            ("otf2bdf", "brew install otf2bdf or apt-get install otf2bdf"),
            ("bdftopcf", "brew install bdftopcf"),
        ],
        "Python Packages": [
            ("fonttools", "uv pip install fonttools"),
            ("pyyaml", "uv pip install pyyaml"),
            ("click", "uv pip install click"),
        ],
    }
