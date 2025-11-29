"""Main font generation orchestration."""

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from .converter import convert_to_bdf, convert_to_pcf, fix_bdf_encodings, generate_subset_font
from .utils import check_character_coverage

if TYPE_CHECKING:
    from .logger import GenerationLogger


def generate_metadata(
    config: dict[str, Any],
    chars: set[str],
    generated_files: list[str],
    output_directory: str,
    debug_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate metadata about the generated fonts.

    Args:
        config: Configuration dictionary
        chars: Set of characters included
        generated_files: List of generated filenames (not full paths)
        output_directory: Directory where files are located
        debug_info: Optional debug information from logger

    Returns:
        Metadata dictionary
    """
    metadata = {
        "version": "1.0",
        "source_font": config["source_font"],
        "character_count": len(chars),
        "characters": "".join(sorted(chars)),
        "unicode_ranges": [f"U+{ord(c):04X}" for c in sorted(chars)],
        "sizes": config["sizes"],
        "output_directory": output_directory,
        "generated_files": generated_files,
        "formats": config["output"]["formats"],
    }

    # Add debug info if provided (debug mode)
    if debug_info:
        metadata["debug_info"] = debug_info

    return metadata


def generate_font(
    config: dict[str, Any],
    chars: set[str],
    output_dir: Path,
    logger: Optional["GenerationLogger"] = None,
) -> list[str]:
    """Generate fonts for all configured sizes.

    Args:
        config: Configuration dictionary
        chars: Set of characters to include
        output_dir: Output directory path (base output directory)
        logger: Optional GenerationLogger for verbose output

    Returns:
        List of generated file paths
    """
    from . import __version__

    generated_files = []
    font_family = config["output"].get("font_family", "custom")

    # Create font-family specific subdirectory
    font_output_dir = output_dir / font_family
    font_output_dir.mkdir(parents=True, exist_ok=True)

    # Check character coverage if in debug mode
    coverage_stats = None
    if logger and logger.debug:
        logger.section("Checking character coverage")
        found, missing, coverage_stats = check_character_coverage(
            config["source_font"], chars, logger
        )

    if logger:
        logger.section(f"\nGenerating fonts for {len(config['sizes'])} size(s)")

    for size in config["sizes"]:
        if logger:
            logger.info(f"\nProcessing size {size}pt:", indent=0)

        # Step 1: Subset the font
        subset_ttf = font_output_dir / f"{font_family}-{size}pt-subset.ttf"
        success, num_glyphs = generate_subset_font(
            config["source_font"], chars, str(subset_ttf), logger
        )
        if not success:
            if logger:
                logger.warn(f"Skipping size {size}pt due to subsetting failure")
            continue

        # Step 2: Convert to BDF (always needed as intermediate for PCF)
        bdf_path = font_output_dir / f"{font_family}-{size}pt.bdf"
        keep_bdf = "bdf" in config["output"]["formats"]
        need_pcf = "pcf" in config["output"]["formats"]

        if not convert_to_bdf(str(subset_ttf), str(bdf_path), size, logger):
            subset_ttf.unlink()
            if logger:
                logger.warn(f"Skipping size {size}pt due to BDF conversion failure")
            continue

        # Fix BDF encodings (Issue #1: ensure Unicode codepoints are correct)
        if not fix_bdf_encodings(str(bdf_path), chars, logger):
            subset_ttf.unlink()
            bdf_path.unlink()
            if logger:
                logger.warn(f"Skipping size {size}pt due to BDF encoding fix failure")
            continue

        if keep_bdf:
            generated_files.append(bdf_path.name)

        # Step 3: Convert to PCF if requested
        if need_pcf:
            pcf_path = font_output_dir / f"{font_family}-{size}pt.pcf"
            if convert_to_pcf(str(bdf_path), str(pcf_path), logger):
                generated_files.append(pcf_path.name)

        # Clean up intermediate files
        subset_ttf.unlink()
        if not keep_bdf:
            bdf_path.unlink()

    # Generate metadata if requested
    if config["output"].get("metadata", True):
        metadata_path = font_output_dir / f"{font_family}-manifest.json"

        # Include debug info if in debug mode
        debug_info = None
        if logger and logger.debug:
            debug_info = logger.get_debug_info(__version__, coverage_stats)

        metadata = generate_metadata(
            config, chars, generated_files, str(font_output_dir), debug_info
        )
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        if logger and logger.verbose:
            logger.success(f"Wrote manifest to {metadata_path.name}")

    return generated_files
