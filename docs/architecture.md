# Verbose and Debug Mode Design

## Problem
Currently, the tool fails silently when:
- Characters don't exist in the source font
- External tools (otf2bdf, bdftopcf) fail
- Subsetting produces minimal output

Users have no way to debug what went wrong without diving into code.

## Proposed Solutions

### 1. Verbose Mode (`--verbose` or `-v`)

Add a verbose flag to the `generate` command that provides detailed progress information.

#### CLI Changes
```python
@cli.command()
@click.option('--config', '-c', default='config.yaml')
@click.option('--dry-run', is_flag=True)
@click.option('--verbose', '-v', is_flag=True, help='Show detailed progress and debug information')
def generate(config, dry_run, verbose):
    ...
```

#### What to Log
- **Character collection phase:**
  - Which characters were requested
  - Which characters were found in the source font
  - Which characters are MISSING (with warning)

- **Subsetting phase:**
  - Source font path and type
  - Number of glyphs in subset vs requested
  - Output file path and size

- **Conversion phase:**
  - Exact command being run (e.g., `otf2bdf -p 24 /path/to/font.ttf -o output.bdf`)
  - Success/failure status
  - Error output if command fails

- **File operations:**
  - Which intermediate files are created
  - Which files are cleaned up

#### Example Output
```
Loading config from examples/icons/config.yaml...
  Source font: /System/Library/Fonts/Helvetica.ttc

Collecting characters...
  Requested 24 characters from unicode ranges
  Checking source font coverage...
    ✓ U+2022 (•) - found
    ✗ U+2190 (←) - NOT FOUND in source font
    ✗ U+2191 (↑) - NOT FOUND in source font
    ...
  WARNING: 23 of 24 requested characters not found in source font

Generating fonts...
  Size 24pt:
    [1/3] Creating subset font...
          Command: fontTools.subset (programmatic)
          Output: /path/to/icons-24pt-subset.ttf (1.2 KB, 2 glyphs)
          WARNING: Only 2 glyphs in subset (expected ~24)

    [2/3] Converting TTF to BDF...
          Command: otf2bdf -p 24 icons-24pt-subset.ttf -o icons-24pt.bdf
          ✗ FAILED: no glyphs generated from 'icons-24pt-subset.ttf'

    Skipping size 24pt due to conversion failure

✗ Font generation failed
  Generated 0 font files
  See errors above for details
```

---

### 2. Debug Manifest Mode (`--debug-manifest`)

Add execution details directly to the manifest file for post-mortem debugging.

#### Manifest Enhancement
```json
{
  "version": "1.0",
  "source_font": "/System/Library/Fonts/Helvetica.ttc",
  "character_count": 24,
  "characters": "...",
  "generated_files": [],

  "debug_info": {
    "timestamp": "2025-11-27T23:03:45Z",
    "tool_version": "0.1.0",

    "character_coverage": {
      "requested": 24,
      "found_in_source": 1,
      "missing": ["U+2190", "U+2191", "U+2192", ...]
    },

    "execution_log": [
      {
        "step": "subset_font",
        "size": 24,
        "command": "fontTools.subset (programmatic)",
        "input": "/System/Library/Fonts/Helvetica.ttc",
        "output": "icons-24pt-subset.ttf",
        "glyphs_produced": 2,
        "status": "success",
        "warnings": ["Only 2 glyphs found out of 24 requested"]
      },
      {
        "step": "convert_to_bdf",
        "size": 24,
        "command": "otf2bdf -p 24 icons-24pt-subset.ttf -o icons-24pt.bdf",
        "status": "failed",
        "error": "no glyphs generated from 'icons-24pt-subset.ttf'"
      }
    ],

    "warnings": [
      "23 characters not found in source font",
      "Conversion failed for size 24pt"
    ],

    "errors": [
      "otf2bdf failed: no glyphs generated"
    ]
  }
}
```

#### Benefits
- Permanent record of what happened
- Can be examined after the fact
- Useful for bug reports
- Can be parsed programmatically

---

### 3. Combined Approach (Recommended)

Implement both modes with three levels of verbosity:

1. **Default**: Minimal output (current behavior, but with errors shown)
2. **`--verbose`**: Show progress and warnings in real-time
3. **`--debug`**: Show everything + save debug manifest

#### Implementation Strategy

```python
# Add logging infrastructure
import logging
from typing import Optional, Dict, Any, List

class GenerationLogger:
    """Centralized logging for font generation"""

    def __init__(self, verbose: bool = False, debug: bool = False):
        self.verbose = verbose
        self.debug = debug
        self.log_entries: List[Dict[str, Any]] = []
        self.warnings: List[str] = []
        self.errors: List[str] = []

    def log_command(self, step: str, command: str, status: str, **kwargs):
        """Log a command execution"""
        entry = {
            "step": step,
            "command": command,
            "status": status,
            **kwargs
        }
        self.log_entries.append(entry)

        if self.verbose or self.debug:
            if status == "success":
                click.echo(f"  ✓ {step}: {command}")
            else:
                click.echo(f"  ✗ {step}: {command}", err=True)
                if "error" in kwargs:
                    click.echo(f"    Error: {kwargs['error']}", err=True)

    def warn(self, message: str):
        """Log a warning"""
        self.warnings.append(message)
        if self.verbose or self.debug:
            click.echo(click.style(f"  WARNING: {message}", fg='yellow'))

    def error(self, message: str):
        """Log an error"""
        self.errors.append(message)
        click.echo(click.style(f"  ERROR: {message}", fg='red'), err=True)

    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug info for manifest"""
        from datetime import datetime
        from . import __version__

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tool_version": __version__,
            "execution_log": self.log_entries,
            "warnings": self.warnings,
            "errors": self.errors
        }
```

#### Modified Converter Functions

```python
def generate_subset_font(
    source_font: str,
    chars: Set[str],
    output_path: str,
    logger: Optional[GenerationLogger] = None
) -> tuple[bool, int]:
    """Generate a subset font.

    Returns:
        (success, num_glyphs): Success status and number of glyphs created
    """
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont

        unicode_list = ','.join(chars_to_unicode_list(chars))

        # Log what we're doing
        if logger:
            logger.log_command(
                "subset_font",
                f"fontTools.subset ({len(chars)} characters)",
                "started",
                input=source_font,
                output=output_path
            )

        options = subset.Options()
        subsetter = subset.Subsetter(options=options)
        subsetter.populate(unicodes=subset.parse_unicodes(unicode_list))

        font_number = 0 if source_font.lower().endswith('.ttc') else None
        font = TTFont(source_font, fontNumber=font_number)

        # Check character coverage BEFORE subsetting
        if logger and logger.debug:
            check_character_coverage(font, chars, logger)

        subsetter.subset(font)
        font.save(output_path)

        # Count glyphs
        num_glyphs = len(font['glyf'].keys()) if 'glyf' in font else 0
        font.close()

        # Warn if we got very few glyphs
        if logger and num_glyphs < len(chars) * 0.5:
            logger.warn(
                f"Only {num_glyphs} glyphs in subset "
                f"(expected ~{len(chars)}). "
                f"Source font may not contain requested characters."
            )

        if logger:
            import os
            size_kb = os.path.getsize(output_path) / 1024
            logger.log_command(
                "subset_font",
                f"fontTools.subset",
                "success",
                output=output_path,
                size_kb=f"{size_kb:.1f}",
                glyphs_produced=num_glyphs
            )

        return True, num_glyphs

    except Exception as e:
        if logger:
            logger.error(f"Font subsetting failed: {str(e)}")
            logger.log_command(
                "subset_font",
                "fontTools.subset",
                "failed",
                error=str(e)
            )
        return False, 0


def convert_to_bdf(
    ttf_path: str,
    bdf_path: str,
    size: int,
    logger: Optional[GenerationLogger] = None
) -> bool:
    """Convert TTF to BDF with logging."""
    cmd = ['otf2bdf', '-p', str(size), ttf_path, '-o', bdf_path]
    cmd_str = ' '.join(cmd)

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        if logger:
            import os
            size_kb = os.path.getsize(bdf_path) / 1024
            logger.log_command(
                "convert_to_bdf",
                cmd_str,
                "success",
                output=bdf_path,
                size_kb=f"{size_kb:.1f}"
            )

        return True

    except subprocess.CalledProcessError as e:
        if logger:
            error_msg = e.stderr.strip() if e.stderr else "Unknown error"
            logger.error(f"otf2bdf failed: {error_msg}")
            logger.log_command(
                "convert_to_bdf",
                cmd_str,
                "failed",
                error=error_msg,
                exit_code=e.returncode
            )
        return False

    except FileNotFoundError:
        if logger:
            logger.error("otf2bdf command not found. Install with: brew install otf2bdf")
            logger.log_command(
                "convert_to_bdf",
                cmd_str,
                "failed",
                error="Command not found"
            )
        return False
```

---

### 4. Character Coverage Analysis

Add a utility to check which characters are actually in the source font:

```python
def check_character_coverage(font: TTFont, requested_chars: Set[str], logger: GenerationLogger):
    """Check which requested characters exist in the font."""

    # Get all available codepoints
    available_codepoints = set()
    if 'cmap' in font:
        for table in font['cmap'].tables:
            available_codepoints.update(table.cmap.keys())

    found = []
    missing = []

    for char in sorted(requested_chars):
        codepoint = ord(char)
        if codepoint in available_codepoints:
            found.append(char)
        else:
            missing.append(char)

    if missing:
        logger.warn(
            f"{len(missing)} of {len(requested_chars)} requested characters "
            f"not found in source font"
        )

        if logger.debug:
            click.echo("\n  Missing characters:")
            for char in missing[:10]:  # Show first 10
                click.echo(f"    ✗ U+{ord(char):04X} ({char})")
            if len(missing) > 10:
                click.echo(f"    ... and {len(missing) - 10} more")
            click.echo()
```

---

## Recommended Implementation Order

1. **Phase 1**: Add basic error messages (no flag needed)
   - Show errors when commands fail
   - Warn when character coverage is low
   - Est: 1-2 hours

2. **Phase 2**: Add `--verbose` flag
   - Show progress through pipeline
   - Show commands being run
   - Show warnings in detail
   - Est: 2-3 hours

3. **Phase 3**: Add `--debug` flag
   - Include all verbose output
   - Add character coverage analysis
   - Save debug info to manifest
   - Est: 2-3 hours

---

## Example Usage

```bash
# Normal mode - see errors but minimal output
uv run cp-font-gen generate --config examples/icons/config.yaml

# Verbose - see what's happening
uv run cp-font-gen generate --config examples/icons/config.yaml --verbose

# Debug - see everything + save to manifest
uv run cp-font-gen generate --config examples/icons/config.yaml --debug
```

---

## Benefits

- **Users** can diagnose their own problems
- **Bug reports** will include debug manifests
- **Development** easier with better visibility
- **CI/CD** can use verbose mode for logs
- **Backward compatible** - no breaking changes
