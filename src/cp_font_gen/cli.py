"""Click CLI interface for cp-font-gen."""

import sys
from pathlib import Path

import click

from . import __version__
from .checker import check_command_exists, check_python_package, get_tool_requirements
from .config import collect_characters, load_config
from .generator import generate_font
from .tool_config import get_default_output_dir


@click.group()
@click.version_option(version=__version__)
def cli():
    """cp-font-gen: Generate minimal bitmap fonts for CircuitPython devices"""
    pass


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed version information")
def check(verbose):
    """Check if required tools are installed and show versions"""
    click.echo("Checking required tools...\n")

    tools = get_tool_requirements()
    all_good = True

    for category, tool_list in tools.items():
        click.echo(f"{category}:")
        for tool, install_cmd in tool_list:
            if category == "System Commands":
                exists, version = check_command_exists(tool)
            else:
                exists, version = check_python_package(tool)

            if exists:
                status = click.style("✓", fg="green", bold=True)
                if verbose and version:
                    click.echo(f"  {status} {tool:15} ({version})")
                else:
                    click.echo(f"  {status} {tool}")
            else:
                status = click.style("✗", fg="red", bold=True)
                click.echo(f"  {status} {tool:15} Install: {install_cmd}")
                all_good = False
        click.echo()

    if all_good:
        click.echo(click.style("All required tools are installed!", fg="green", bold=True))
        sys.exit(0)
    else:
        click.echo(click.style("Some required tools are missing. Please install them.", fg="red"))
        sys.exit(1)


@cli.command()
@click.option("--config", "-c", default="config.yaml", help="Path to configuration file")
@click.option("--dry-run", is_flag=True, help="Show what would be generated without generating")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed progress and debug information")
@click.option(
    "--debug",
    is_flag=True,
    help="Show everything including character coverage analysis and save debug info to manifest",
)
def generate(config, dry_run, verbose, debug):
    """Generate fonts from configuration file"""
    from .logger import GenerationLogger

    # Get config file path and its directory
    config_path = Path(config).resolve()
    config_dir = config_path.parent

    # Load configuration
    click.echo(f"Loading config from {config}...")
    try:
        cfg = load_config(str(config_path))
    except FileNotFoundError:
        click.echo(f"Error: Config file {config} not found", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error loading config: {e}", err=True)
        sys.exit(1)

    # Determine logging level
    # Priority: CLI flags > config file > default
    config_logging = cfg.get("logging", {})
    config_level = config_logging.get("level", "default").lower()

    # CLI flags override config
    if debug:
        actual_verbose = True
        actual_debug = True
    elif verbose:
        actual_verbose = True
        actual_debug = False
    else:
        # Use config file settings
        if config_level == "debug":
            actual_verbose = True
            actual_debug = True
        elif config_level == "verbose":
            actual_verbose = True
            actual_debug = False
        else:  # 'default' or any other value
            actual_verbose = False
            actual_debug = False

    # Create logger with determined settings
    logger = GenerationLogger(verbose=actual_verbose, debug=actual_debug)

    # Collect characters
    click.echo("Collecting characters...")
    chars = collect_characters(cfg, config_dir)
    preview = "".join(sorted(chars)[:50])
    if len(chars) > 50:
        preview += "..."
    click.echo(f"Found {len(chars)} unique characters: {preview}")

    if dry_run:
        click.echo("\n" + click.style("Dry run - would generate:", bold=True))
        click.echo(f"  Characters: {len(chars)}")
        click.echo(f"  Sizes: {cfg['sizes']}")
        click.echo(f"  Formats: {cfg['output']['formats']}")
        return

    # Create output directory
    # Get tool default output directory
    tool_default = get_default_output_dir()
    output_path = Path(cfg["output"]["directory"])

    # Resolve relative paths relative to tool default
    if not output_path.is_absolute():
        output_dir = (tool_default / output_path).resolve()
    else:
        output_dir = output_path

    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate fonts
    if not actual_verbose and not actual_debug:
        click.echo("\nGenerating fonts...")
        with click.progressbar(cfg["sizes"], label="Processing sizes") as sizes:
            generated_files = []
            for _ in sizes:
                pass
            # Actually generate (progressbar just for display)
            generated_files = generate_font(cfg, chars, output_dir, logger)
    else:
        # In verbose/debug mode, skip progress bar and show detailed output
        generated_files = generate_font(cfg, chars, output_dir, logger)

    # Show summary
    if generated_files:
        click.echo("\n" + click.style("✓ Font generation complete!", fg="green", bold=True))
        click.echo(f"  Generated {len(generated_files)} font files")
        click.echo(f"  Output directory: {output_dir}")
    else:
        click.echo("\n" + click.style("✗ Font generation failed!", fg="red", bold=True))
        click.echo("  No font files were generated")
        click.echo("  See errors above for details")

        # Show summary of warnings and errors
        if logger.warnings:
            click.echo(f"\n  Warnings: {len(logger.warnings)}")
        if logger.errors:
            click.echo(f"  Errors: {len(logger.errors)}")
            if not actual_verbose and not actual_debug:
                click.echo("\n  Run with --verbose or --debug for more details")

        sys.exit(1)


@cli.command()
@click.argument("text_file", type=click.Path(exists=True))
def extract(text_file):
    """Extract unique characters from a text file"""
    with open(text_file, encoding="utf-8") as f:
        chars = set(f.read())

    click.echo(f"Found {len(chars)} unique characters:")
    click.echo("".join(sorted(chars)))

    # Also show unicode ranges
    click.echo("\nUnicode code points:")
    for char in sorted(chars)[:20]:
        click.echo(f"  {char} -> U+{ord(char):04X}")
    if len(chars) > 20:
        click.echo(f"  ... and {len(chars) - 20} more")


@cli.command()
@click.option("--config", "-c", default="config.yaml", help="Path to configuration file")
def show(config):
    """Show what characters would be included from config"""
    try:
        config_path = Path(config).resolve()
        config_dir = config_path.parent

        cfg = load_config(str(config_path))
        chars = collect_characters(cfg, config_dir)

        click.echo(f"Configuration: {config}")
        click.echo(f"Character count: {len(chars)}")
        click.echo(f"Characters: {''.join(sorted(chars))}")
        click.echo(f"\nSizes: {cfg['sizes']}")
        click.echo(f"Formats: {cfg['output']['formats']}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
