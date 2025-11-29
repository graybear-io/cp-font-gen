# Configuration Reference

Complete reference for cp-font-gen configuration files.

## Configuration File Format

Configuration files use YAML format. The basic structure:

```yaml
source_font: "/path/to/font.ttf"
sizes: [12, 16, 24]
characters:
  inline: "ABC123"
output:
  directory: "output"
  font_family: "custom"
  formats: ["pcf"]
```

## Required Sections

### source_font

Path to the source font file (TrueType or OpenType).

**Supported formats:**
- `.ttf` - TrueType Font
- `.otf` - OpenType Font
- `.ttc` - TrueType Collection

**Path resolution:**
- Absolute paths: Used as-is
- Relative paths: Relative to config file location
- `~/` paths: Expanded to home directory

**Common system font locations:**
- **macOS**: `/System/Library/Fonts/`
- **Linux**: `/usr/share/fonts/`
- **Windows**: `C:\Windows\Fonts\`

**For Unicode symbols** (arrows, weather, emoji):
- macOS: `/System/Library/Fonts/Supplemental/Arial Unicode.ttf`
- Linux: `/usr/share/fonts/truetype/unifont/unifont.ttf`

**Example:**
```yaml
source_font: "/System/Library/Fonts/Helvetica.ttc"
```

---

### sizes

List of font sizes to generate (in points).

**Typical CircuitPython sizes:**
- `8, 10` - Very small displays
- `12, 14, 16` - Standard text
- `24, 32` - Headers, titles
- `48+` - Large displays, emphasis

**Example:**
```yaml
sizes:
  - 12  # Small text
  - 16  # Medium text
  - 24  # Large text
```

---

### characters

Define which characters to include in the font. You can use **one or more** methods:

#### Method 1: Inline Characters

Specify characters directly in the config (convenient for small sets).

```yaml
characters:
  inline: "0123456789°C "
```

#### Method 2: Load from File

Load characters from a text file (good for large character sets).

```yaml
characters:
  file: "chars.txt"
```

- Path can be absolute or relative to config file
- File should be UTF-8 encoded text
- All unique characters in the file will be included

#### Method 3: Unicode Ranges

Specify Unicode ranges (perfect for symbol sets).

```yaml
characters:
  unicode_ranges:
    - "U+0030-0039"  # Digits 0-9
    - "U+0041-005A"  # Uppercase A-Z
    - "U+0061-007A"  # Lowercase a-z
    - "U+0020"       # Space
```

**Common Unicode ranges:**

| Range | Description | Characters |
|-------|-------------|------------|
| `U+0030-0039` | Digits | 0-9 |
| `U+0041-005A` | Uppercase Latin | A-Z |
| `U+0061-007A` | Lowercase Latin | a-z |
| `U+0020` | Space | (space) |
| `U+00A0-00FF` | Latin-1 Supplement | é, ñ, ü, etc. |
| `U+2190-2193` | Arrows | ← ↑ → ↓ |
| `U+2600-2603` | Weather symbols | ☀ ☁ ☂ ☃ |
| `U+2713-2714` | Checkmarks | ✓ ✔ |
| `U+2717-2718` | X marks | ✗ ✘ |
| `U+25A0-25FF` | Geometric shapes | ■ □ ▲ ● etc. |
| `U+2022` | Bullet | • |

#### Combining Methods

All methods can be combined - characters are merged and deduplicated:

```yaml
characters:
  inline: "0123456789"
  file: "menu_items.txt"
  unicode_ranges:
    - "U+00B0"  # Degree symbol
```

---

### output

Output directory and format configuration.

```yaml
output:
  directory: "output"
  font_family: "custom"
  formats: ["pcf"]
  metadata: true
```

#### directory

Output directory for generated fonts.

- Relative paths: Resolved from tool's default output location
- Absolute paths: Used as-is
- `~/` paths: Expanded to home directory

A subdirectory will be created using the `font_family` name.

**Example:** With `directory: "output"` and `font_family: "digits"`:
```
output/
  digits/
    digits-16pt.pcf
    digits-manifest.json
```

#### font_family

Font family name used for:
- Output subdirectory
- Output filenames (e.g., `custom-16pt.pcf`)
- Manifest filename (e.g., `custom-manifest.json`)

**Naming convention:** Use lowercase with hyphens or underscores.

#### formats

List of output formats to generate.

**Available formats:**
- `"pcf"` - Portable Compiled Format (required for CircuitPython)
- `"bdf"` - Bitmap Distribution Format (human-readable, larger)

**Note:** BDF is always generated as an intermediate format but only kept if explicitly listed.

**Recommended:**
```yaml
formats: ["pcf"]  # PCF only (smaller, faster)
```

**For debugging:**
```yaml
formats: ["pcf", "bdf"]  # Keep both formats
```

#### metadata

Generate manifest JSON file (default: `true`).

The manifest contains:
- Character list and unicode ranges
- Source font information
- File sizes and formats
- Debug information (when using `--debug` mode)

---

## Optional Sections

### Character Processing Options

Control how characters are processed.

```yaml
deduplicate_chars: true    # Remove duplicate characters (default: true)
strip_whitespace: false    # Remove whitespace except space (default: false)
```

#### deduplicate_chars

Remove duplicate characters from all sources (default: `true`).

Set to `false` if you need to preserve duplicates for debugging.

#### strip_whitespace

Remove all whitespace characters except space (default: `false`).

Useful when loading characters from files that might contain newlines, tabs, etc.

---

### Logging Options

Control logging verbosity during font generation.

```yaml
logging:
  level: "default"  # Options: "default", "verbose", "debug"
```

**Levels:**
- `"default"` - Minimal output, shows errors and summary
- `"verbose"` - Detailed progress, shows each step and warnings
- `"debug"` - Everything including character coverage analysis

**Note:** CLI flags override this setting:
- `--verbose` → verbose level
- `--debug` → debug level

See [Logging Guide](logging.md) for details.

---

## Complete Example

```yaml
# Source font
source_font: "/System/Library/Fonts/Helvetica.ttc"

# Generate multiple sizes
sizes:
  - 12
  - 16
  - 24

# Combine multiple character sources
characters:
  inline: "0123456789°C "
  file: "custom_chars.txt"
  unicode_ranges:
    - "U+0041-005A"  # A-Z
    - "U+0061-007A"  # a-z

# Character processing
deduplicate_chars: true
strip_whitespace: false

# Output configuration
output:
  directory: "output"
  font_family: "my-font"
  formats: ["pcf"]
  metadata: true

# Logging
logging:
  level: "verbose"
```

---

## Common Patterns

### Temperature Display
Digits, degree symbol, and unit letters:

```yaml
characters:
  inline: "0123456789.°CF "
```

### Menu System
Letters and basic punctuation:

```yaml
characters:
  unicode_ranges:
    - "U+0041-005A"  # A-Z
    - "U+0061-007A"  # a-z
    - "U+0020"       # Space
  inline: ":-_()[]"
```

### Multilingual Text
Include accented characters:

```yaml
characters:
  unicode_ranges:
    - "U+0041-005A"  # A-Z
    - "U+0061-007A"  # a-z
    - "U+00C0-00FF"  # À-ÿ (accented Latin)
    - "U+0020"       # Space
```

### Icon Font
Symbols only:

```yaml
characters:
  unicode_ranges:
    - "U+2190-2193"  # Arrows
    - "U+2600-2603"  # Weather
    - "U+2713-2714"  # Checkmarks
```

---

## Tool-Wide Configuration

You can set a default output directory for all configs:

**Create:** `~/.config/cp-font-gen/config.yaml`

```yaml
output_directory: ~/cp-projects/fonts
```

Now all font configs with `output: "output"` will generate to:
`~/cp-projects/fonts/output/{font_family}/`

---

## Validation

Use these commands to validate your config:

```bash
# Show what characters would be included
cp-font-gen show --config myconfig.yaml

# Dry run (no files generated)
cp-font-gen generate --config myconfig.yaml --dry-run

# Debug mode (see character coverage)
cp-font-gen generate --config myconfig.yaml --debug
```

---

## See Also

- [Quick Start](quick-start.md) - Get started quickly
- [Examples](../examples/) - Real-world example configs
- [Logging Guide](logging.md) - Debug mode and verbose logging
- [Troubleshooting](troubleshooting.md) - Common config issues
