"""Font format conversion pipeline (TTF → BDF → PCF)."""

import io
import os
import subprocess
from contextlib import redirect_stderr
from typing import TYPE_CHECKING, Optional

from .utils import chars_to_unicode_list

if TYPE_CHECKING:
    from .logger import GenerationLogger


def generate_subset_font(
    source_font: str, chars: set[str], output_path: str, logger: Optional["GenerationLogger"] = None
) -> tuple[bool, int]:
    """Generate a subset font using fontTools.subset.

    Args:
        source_font: Path to source font file
        chars: Set of characters to include
        output_path: Path for output subset font
        logger: Optional GenerationLogger for verbose output

    Returns:
        Tuple of (success, num_glyphs): Success status and number of glyphs created
    """
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont

        unicode_list = ",".join(chars_to_unicode_list(chars))

        if logger:
            logger.log_command(
                "subset_font",
                f"fontTools.subset ({len(chars)} characters)",
                "started",
                input=os.path.basename(source_font),
            )

        # Capture stderr from fontTools (warnings about tables, etc.)
        stderr_capture = io.StringIO()
        with redirect_stderr(stderr_capture):
            # Create subset options
            options = subset.Options()

            # Parse unicode list into options
            subsetter = subset.Subsetter(options=options)
            subsetter.populate(unicodes=subset.parse_unicodes(unicode_list))

            # For TTC files, we need to specify font number
            font_number = 0 if source_font.lower().endswith(".ttc") else None

            # Load and subset font
            font = TTFont(source_font, fontNumber=font_number)
            subsetter.subset(font)

            # Save output
            font.save(output_path)

            # Count glyphs in the subset
            num_glyphs = len(font["glyf"].keys()) if "glyf" in font else 0
            font.close()

        # Get captured stderr
        stderr_output = stderr_capture.getvalue()

        # Warn if we got very few glyphs compared to requested
        if logger and num_glyphs < len(chars) * 0.5:
            logger.warn(
                f"Only {num_glyphs} glyphs in subset (expected ~{len(chars)}). "
                f"Source font may not contain requested characters."
            )

        if logger:
            size_kb = os.path.getsize(output_path) / 1024
            log_entry = {
                "output": os.path.basename(output_path),
                "size_kb": f"{size_kb:.1f}",
                "glyphs_produced": num_glyphs,
                "full_command": f"fontTools.subset {source_font} --unicodes={unicode_list[:50]}... --output-file={output_path}",
            }

            # In debug mode, capture stderr (fontTools warnings)
            if logger.debug and stderr_output:
                log_entry["stderr"] = stderr_output.strip()

            logger.log_command("subset_font", "fontTools.subset", "success", **log_entry)

        return True, num_glyphs

    except Exception as e:
        if logger:
            logger.error(f"Font subsetting failed: {str(e)}")
            logger.log_command(
                "subset_font",
                "fontTools.subset",
                "failed",
                full_command=f"fontTools.subset {source_font} (programmatic)",
                error=str(e),
            )
        return False, 0


def fix_bdf_encodings(
    bdf_path: str, chars: set[str], logger: Optional["GenerationLogger"] = None
) -> bool:
    """Fix ENCODING values in BDF to match Unicode codepoints.

    Issue #1: fontTools.subset may create subset fonts with sequential
    glyph mappings (1, 2, 3...) instead of preserving Unicode codepoints
    (48, 49, 50... for '0', '1', '2'...). This fixes the BDF by replacing
    ENCODING values with the correct Unicode codepoints.

    Args:
        bdf_path: Path to BDF file to fix
        chars: Set of characters that should be in the font
        logger: Optional GenerationLogger for verbose output

    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert chars to sorted list of Unicode codepoints
        char_list = sorted(list(chars))
        codepoints = [ord(c) for c in char_list]

        # Read BDF file
        with open(bdf_path, "r") as f:
            lines = f.readlines()

        # Fix ENCODING values
        output_lines = []
        codepoint_idx = 0
        fixed_count = 0

        for line in lines:
            if line.startswith("ENCODING "):
                # Replace with correct Unicode codepoint
                if codepoint_idx < len(codepoints):
                    old_encoding = int(line.split()[1])
                    new_encoding = codepoints[codepoint_idx]

                    if old_encoding != new_encoding:
                        fixed_count += 1

                    output_lines.append(f"ENCODING {new_encoding}\n")
                    codepoint_idx += 1
                else:
                    # Out of range - keep original (shouldn't happen)
                    output_lines.append(line)
            else:
                output_lines.append(line)

        # Write fixed BDF
        with open(bdf_path, "w") as f:
            f.writelines(output_lines)

        return True

    except Exception as e:
        if logger:
            logger.error(f"Failed to fix BDF encodings: {str(e)}")
        return False


def convert_to_bdf(
    ttf_path: str, bdf_path: str, size: int, logger: Optional["GenerationLogger"] = None
) -> bool:
    """Convert TTF to BDF format using otf2bdf.

    Args:
        ttf_path: Path to TTF file
        bdf_path: Path for output BDF file
        size: Font size in points
        logger: Optional GenerationLogger for verbose output

    Returns:
        True if successful, False otherwise
    """
    cmd = ["otf2bdf", "-p", str(size), ttf_path, "-o", bdf_path]
    cmd_str = " ".join(cmd)

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        if logger:
            size_kb = os.path.getsize(bdf_path) / 1024
            log_entry = {
                "output": os.path.basename(bdf_path),
                "size_kb": f"{size_kb:.1f}",
                "full_command": cmd_str,
            }

            # In debug mode, capture stdout/stderr
            if logger.debug:
                if result.stdout:
                    log_entry["stdout"] = result.stdout.strip()
                if result.stderr:
                    log_entry["stderr"] = result.stderr.strip()

            logger.log_command(
                "convert_to_bdf",
                cmd_str,  # Log full command, not simplified
                "success",
                **log_entry,
            )

        return True

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "Unknown error"
        if logger:
            logger.error(f"otf2bdf failed: {error_msg}")
            log_entry = {
                "full_command": cmd_str,
                "error": error_msg,
                "exit_code": str(e.returncode),
            }

            # In debug mode, capture both stdout and stderr
            if logger.debug:
                if e.stdout:
                    log_entry["stdout"] = e.stdout.strip()
                if e.stderr:
                    log_entry["stderr"] = e.stderr.strip()

            logger.log_command("convert_to_bdf", cmd_str, "failed", **log_entry)
        return False

    except FileNotFoundError:
        if logger:
            logger.error("otf2bdf command not found. Install with: brew install otf2bdf")
            logger.log_command("convert_to_bdf", cmd_str, "failed", error="Command not found")
        return False


def convert_to_pcf(
    bdf_path: str, pcf_path: str, logger: Optional["GenerationLogger"] = None
) -> bool:
    """Convert BDF to PCF format using bdftopcf.

    Args:
        bdf_path: Path to BDF file
        pcf_path: Path for output PCF file
        logger: Optional GenerationLogger for verbose output

    Returns:
        True if successful, False otherwise
    """
    cmd = ["bdftopcf", bdf_path]
    cmd_str = " ".join(cmd)

    try:
        with open(pcf_path, "w") as pcf_file:
            result = subprocess.run(
                cmd, check=True, stdout=pcf_file, stderr=subprocess.PIPE, text=True
            )

        if logger:
            size_kb = os.path.getsize(pcf_path) / 1024
            log_entry = {
                "output": os.path.basename(pcf_path),
                "size_kb": f"{size_kb:.1f}",
                "full_command": cmd_str,
            }

            # In debug mode, capture stderr (stdout goes to file)
            if logger.debug and result.stderr:
                log_entry["stderr"] = result.stderr.strip()

            logger.log_command(
                "convert_to_pcf",
                cmd_str,  # Log full command, not simplified
                "success",
                **log_entry,
            )

        return True

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "Unknown error"
        if logger:
            logger.error(f"bdftopcf failed: {error_msg}")
            log_entry = {
                "full_command": cmd_str,
                "error": error_msg,
                "exit_code": str(e.returncode),
            }

            # In debug mode, capture stderr
            if logger.debug and e.stderr:
                log_entry["stderr"] = e.stderr.strip()

            logger.log_command("convert_to_pcf", cmd_str, "failed", **log_entry)
        return False

    except FileNotFoundError:
        if logger:
            logger.error("bdftopcf command not found. Install with: brew install bdftopcf")
            logger.log_command(
                "convert_to_pcf", cmd_str, "failed", full_command=cmd_str, error="Command not found"
            )
        return False
