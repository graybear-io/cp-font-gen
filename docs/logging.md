# Logging Configuration Guide

cp-font-gen supports three levels of logging verbosity to help you understand what's happening during font generation and debug issues.

## Logging Levels

### 1. Default (Silent Mode)
**What it shows:**
- Basic progress messages
- Critical errors only
- Summary of results

**When to use:**
- Normal font generation
- Automated builds
- When everything is working

**Example output:**
```
Loading config from config.yaml...
Collecting characters...
Found 24 unique characters: ...

Generating fonts...
Processing sizes
✓ Font generation complete!
  Generated 1 font files
```

---

### 2. Verbose Mode
**What it shows:**
- Every step of the pipeline
- Success/failure status for each step
- File sizes and glyph counts
- Warnings about potential issues
- Exact commands being executed

**When to use:**
- First time using a new config
- Troubleshooting font generation issues
- Understanding what the tool is doing
- CI/CD logs

**Example output:**
```
Generating fonts for 1 size(s)

Processing size 24pt:
  [subset_font] fontTools.subset (24 characters)
  WARNING: Only 4 glyphs in subset (expected ~24)
  ✓ [subset_font] fontTools.subset → icons-24pt-subset.ttf (6.1 KB) (4 glyphs)
  ERROR: otf2bdf failed: no glyphs generated
  ✗ [convert_to_bdf] otf2bdf -p 24 icons-24pt-subset.ttf -o icons-24pt.bdf
      Error: otf2bdf: no glyphs generated from 'icons-24pt-subset.ttf'.
  WARNING: Skipping size 24pt due to BDF conversion failure
```

---

### 3. Debug Mode
**What it shows:**
- Everything from verbose mode
- Character coverage analysis (which characters are missing from font)
- Detailed missing character list
- Debug information saved to manifest file

**When to use:**
- Characters aren't showing up in generated font
- Font generation failing with unclear errors
- Need to verify which characters are available in source font
- Creating bug reports

**Example output:**
```
Checking character coverage
  WARNING: 21 of 24 requested characters not found in source font

  Missing characters:
    ✗ U+2190 (←)
    ✗ U+2191 (↑)
    ✗ U+2192 (→)
    ... and 18 more

Generating fonts for 1 size(s)
...
```

**Debug manifest includes:**
```json
{
  "debug_info": {
    "timestamp": "2025-11-28T04:20:35Z",
    "execution_log": [
      {
        "step": "convert_to_bdf",
        "command": "otf2bdf -p 24 ...",
        "status": "failed",
        "error": "no glyphs generated"
      }
    ],
    "character_coverage": {
      "requested": 24,
      "found_in_source": 3,
      "missing": ["U+2190", "U+2191", ...]
    },
    "warnings": [...],
    "errors": [...]
  }
}
```

---

## How to Set Logging Level

### Method 1: CLI Flags (Temporary)

**Verbose:**
```bash
uv run cp-font-gen generate --config config.yaml --verbose
# or
uv run cp-font-gen generate --config config.yaml -v
```

**Debug:**
```bash
uv run cp-font-gen generate --config config.yaml --debug
```

---

### Method 2: Config File (Persistent)

Add a `logging` section to your config file:

**config.yaml:**
```yaml
source_font: "/path/to/font.ttf"
sizes: [16, 24]
characters:
  inline: "ABC123"
output:
  directory: "output"
  font_family: "custom"
  formats: ["pcf"]

# Set default logging level for this config
logging:
  level: "verbose"  # Options: "default", "verbose", "debug"
```

Now every time you run:
```bash
uv run cp-font-gen generate --config config.yaml
```

It will use verbose mode automatically!

---

## Priority: CLI Overrides Config

CLI flags always override config file settings:

**Example:**
```yaml
# config.yaml has:
logging:
  level: "default"
```

```bash
# But you run with --debug:
uv run cp-font-gen generate --config config.yaml --debug
# → Uses debug mode (CLI wins)
```

This lets you:
- Set a default level in config for normal use
- Override temporarily when debugging specific issues

---

## Common Patterns

### Development Config
```yaml
# While developing/testing your config
logging:
  level: "verbose"
```

### Production Config
```yaml
# For stable configs in CI/CD
logging:
  level: "default"
```

### Debugging Config
```yaml
# When investigating character coverage issues
logging:
  level: "debug"
```

### Per-Environment Override
```yaml
# config.yaml (committed to git)
logging:
  level: "default"
```

```bash
# Local debugging (not committed)
uv run cp-font-gen generate --config config.yaml --debug
```

---

## Troubleshooting Decision Tree

**Problem:** Font generation failed, not sure why
→ Use `--verbose` to see which step failed

**Problem:** Characters appear as boxes on device
→ Use `--debug` to see character coverage analysis

**Problem:** "no glyphs generated" error
→ Use `--debug` to see which characters are missing from source font

**Problem:** Want to save debug info for later analysis
→ Use `--debug` to save detailed log to manifest file

**Problem:** Need to see exact commands for manual testing
→ Use `--verbose` to see full command lines

---

## Tips

1. **Start with default**, only add verbose/debug when needed
2. **Use verbose in CI/CD** so you have logs when things fail
3. **Use debug when asking for help** - include the debug manifest in bug reports
4. **Config-based logging** is great for configs you're actively developing
5. **CLI flags** are better for one-off debugging

---

## Examples by Use Case

### Use Case: First time trying a new Unicode font
```bash
# See if your characters are actually in the font
uv run cp-font-gen generate --config icons.yaml --debug
```

### Use Case: Automated build in CI
```yaml
# icons.yaml
logging:
  level: "verbose"  # Always show progress in CI logs
```

### Use Case: Quick iteration during development
```yaml
# my-font.yaml - while testing
logging:
  level: "verbose"
```

```bash
# Just run it, verbose is automatic
uv run cp-font-gen generate --config my-font.yaml
```

### Use Case: Production font that works reliably
```yaml
# production.yaml
logging:
  level: "default"  # Clean output
```

```bash
# If it breaks, temporarily add debug
uv run cp-font-gen generate --config production.yaml --debug
```
