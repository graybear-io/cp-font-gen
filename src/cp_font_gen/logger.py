"""Logging infrastructure for font generation pipeline."""

from datetime import datetime
from typing import Any

import click


class GenerationLogger:
    """Centralized logging for font generation with verbose and debug modes."""

    def __init__(self, verbose: bool = False, debug: bool = False):
        """Initialize the logger.

        Args:
            verbose: Show detailed progress information
            debug: Show everything including debug info (implies verbose)
        """
        self.verbose = verbose or debug
        self.debug = debug
        self.log_entries: list[dict[str, Any]] = []
        self.warnings: list[str] = []
        self.errors: list[str] = []

    def log_command(self, step: str, command: str, status: str, **kwargs):
        """Log a command execution.

        Args:
            step: Name of the step (e.g., "subset_font", "convert_to_bdf")
            command: Command or description of what was executed
            status: Status of execution ("started", "success", "failed")
            **kwargs: Additional metadata to log
        """
        entry = {"step": step, "command": command, "status": status, **kwargs}
        self.log_entries.append(entry)

        if self.verbose:
            if status == "started":
                click.echo(f"  [{step}] {command}")
            elif status == "success":
                msg = f"  ✓ [{step}] {command}"
                if "output" in kwargs:
                    msg += f" → {kwargs['output']}"
                if "size_kb" in kwargs:
                    msg += f" ({kwargs['size_kb']} KB)"
                if "glyphs_produced" in kwargs:
                    msg += f" ({kwargs['glyphs_produced']} glyphs)"
                click.echo(click.style(msg, fg="green"))
            elif status == "failed":
                msg = f"  ✗ [{step}] {command}"
                click.echo(click.style(msg, fg="red"), err=True)
                if "error" in kwargs:
                    click.echo(f"      Error: {kwargs['error']}", err=True)

    def info(self, message: str, indent: int = 2):
        """Log an info message (only shown in verbose mode).

        Args:
            message: Message to log
            indent: Number of spaces to indent
        """
        if self.verbose:
            click.echo(" " * indent + message)

    def warn(self, message: str):
        """Log a warning message.

        Args:
            message: Warning message
        """
        self.warnings.append(message)
        if self.verbose:
            click.echo(click.style(f"  WARNING: {message}", fg="yellow"))

    def error(self, message: str):
        """Log an error message (always shown).

        Args:
            message: Error message
        """
        self.errors.append(message)
        click.echo(click.style(f"  ERROR: {message}", fg="red"), err=True)

    def success(self, message: str):
        """Log a success message.

        Args:
            message: Success message
        """
        if self.verbose:
            click.echo(click.style(f"  ✓ {message}", fg="green"))

    def section(self, title: str):
        """Print a section header (verbose mode only).

        Args:
            title: Section title
        """
        if self.verbose:
            click.echo(f"\n{title}")

    def get_debug_info(
        self, tool_version: str, character_coverage: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Get debug info for manifest.

        Args:
            tool_version: Version of cp-font-gen
            character_coverage: Optional character coverage stats

        Returns:
            Dictionary with debug information
        """
        debug_info: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tool_version": tool_version,
            "execution_log": self.log_entries,
            "warnings": self.warnings,
            "errors": self.errors,
        }

        if character_coverage:
            debug_info["character_coverage"] = character_coverage

        return debug_info
