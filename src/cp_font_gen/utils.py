"""Utility functions for character handling."""

from typing import Any

import click


def chars_to_unicode_list(chars: set[str]) -> list[str]:
    """Convert characters to unicode code point list.

    Args:
        chars: Set of characters

    Returns:
        List of unicode code points in format "U+XXXX"
    """
    return [f"U+{ord(c):04X}" for c in sorted(chars)]


def unicode_range_to_chars(unicode_range: str) -> set[str]:
    """Convert a unicode range string to a set of characters.

    Args:
        unicode_range: Range like "U+0030-0039" or single "U+00B0"

    Returns:
        Set of characters in the range
    """
    chars = set()

    # Remove U+ prefix
    range_str = unicode_range.replace("U+", "")

    if "-" in range_str:
        # Range like "0030-0039"
        start, end = range_str.split("-")
        start_code = int(start, 16)
        end_code = int(end, 16)
        for code in range(start_code, end_code + 1):
            chars.add(chr(code))
    else:
        # Single character like "00B0"
        code = int(range_str, 16)
        chars.add(chr(code))

    return chars


def check_character_coverage(
    source_font_path: str, requested_chars: set[str], logger: Any | None = None
) -> tuple[set[str], set[str], dict[str, Any]]:
    """Check which requested characters exist in the source font.

    Args:
        source_font_path: Path to the source font file
        requested_chars: Set of characters to check
        logger: Optional GenerationLogger instance

    Returns:
        Tuple of (found_chars, missing_chars, coverage_stats)
    """
    from fontTools.ttLib import TTFont

    try:
        # Determine font number for TTC files
        font_number = 0 if source_font_path.lower().endswith(".ttc") else None
        font = TTFont(source_font_path, fontNumber=font_number)

        # Get all available codepoints from all cmap tables
        available_codepoints = set()
        if "cmap" in font:
            for table in font["cmap"].tables:
                available_codepoints.update(table.cmap.keys())

        # Check which characters are available
        found = set()
        missing = set()

        for char in requested_chars:
            codepoint = ord(char)
            if codepoint in available_codepoints:
                found.add(char)
            else:
                missing.add(char)

        font.close()

        # Create coverage stats
        coverage_stats = {
            "requested": len(requested_chars),
            "found_in_source": len(found),
            "missing_count": len(missing),
            "missing": [f"U+{ord(c):04X}" for c in sorted(missing)] if missing else [],
        }

        # Log warnings if there are missing characters
        if missing and logger:
            logger.warn(
                f"{len(missing)} of {len(requested_chars)} requested characters "
                f"not found in source font"
            )

            if logger.debug and missing:
                click.echo("\n  Missing characters:")
                for char in sorted(missing)[:10]:  # Show first 10
                    click.echo(f"    ✗ U+{ord(char):04X} ({char})")
                if len(missing) > 10:
                    click.echo(f"    ... and {len(missing) - 10} more")
                click.echo()

        return found, missing, coverage_stats

    except Exception as e:
        if logger:
            logger.error(f"Failed to check character coverage: {str(e)}")
        # Return empty results on error
        return (
            set(),
            requested_chars,
            {
                "requested": len(requested_chars),
                "found_in_source": 0,
                "missing_count": len(requested_chars),
                "missing": [f"U+{ord(c):04X}" for c in sorted(requested_chars)],
                "error": str(e),
            },
        )
