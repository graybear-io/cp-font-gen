# cp-font-gen

Generate minimal bitmap fonts for memory-constrained CircuitPython devices.

## What It Does

CircuitPython devices have limited flash storage (KB, not MB). Full fonts waste precious space.

**cp-font-gen** creates custom bitmap fonts containing **only the glyphs you need**:
- Specify exactly which characters to include
- Generate PCF/BDF fonts at multiple sizes
- Save 90%+ of font storage space
- Get metadata about what was generated

## Installation

### Prerequisites
- **uv** - `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **just** - `brew install just`
- **System tools** - See [System Tools Installation](quick-start.md#system-tools-installation) for otf2bdf and bdftopcf

### Setup
```bash
cd cp-font-gen
uv sync          # Install dependencies
just check       # Verify tools are installed
```

## Quick Start

### 1. Edit Your Config

Edit `config.yaml` to specify which characters you need:

```yaml
source_font: "/System/Library/Fonts/Helvetica.ttc"

sizes:
  - 12
  - 16

characters:
  inline: "0123456789°C "
  file: "chars.txt"  # Load from file (optional)
  unicode_ranges:    # Or specify ranges (optional)
    - "U+0030-0039"  # Digits 0-9

output:
  directory: "output"
  formats: ["bdf", "pcf"]
  metadata: true
  font_family: "custom"
```

### 2. Generate Fonts

```bash
just generate
```

### 3. Check Output

```bash
just list-output      # See generated files
just show-manifest    # See what was included
```

### 4. Deploy

Copy fonts from `output/{font_family}/` to your CIRCUITPY drive:
```bash
# Copy all files for a font family
cp output/custom/custom-* /Volumes/CIRCUITPY/fonts/
```

## Usage

### Common Commands

```bash
# Check if tools are installed
just check

# Generate fonts
just generate

# Preview without generating
just dry-run

# Show what would be included
just show

# Extract characters from a file
just extract my_text.txt

# View generated files
just list-output
```

### CLI Reference

| Command | Description |
|---------|-------------|
| `just check` | Verify tools are installed |
| `just check-verbose` | Show tool versions |
| `just generate` | Generate fonts from config |
| `just dry-run` | Preview without generating |
| `just show` | Show config details |
| `just extract FILE` | Extract unique chars from file |
| `just list-output` | List generated files |
| `just show-manifest` | Show manifest.json |
| `just clean` | Remove generated fonts |

Or use the CLI directly:
```bash
cp-font-gen check
cp-font-gen generate --config myconfig.yaml
cp-font-gen extract text.txt
```

## Configuration

### Character Sources

Specify characters in three ways:

**1. Inline**
```yaml
characters:
  inline: "0123456789ABCabc"
```

**2. From File**
```yaml
characters:
  file: "chars.txt"
```

**3. Unicode Ranges**
```yaml
characters:
  unicode_ranges:
    - "U+0030-0039"  # Digits
    - "U+0041-005A"  # Uppercase A-Z
    - "U+00B0"       # Degree symbol
```

All sources are combined and deduplicated.

### Font Sizes

Generate multiple sizes in one run:
```yaml
sizes:
  - 12
  - 16
  - 20
```

### Output Formats

**PCF** (recommended) - Binary, compact, fast to load
**BDF** (optional) - ASCII, human-readable, larger

```yaml
output:
  formats: ["bdf", "pcf"]  # Generate both
  # formats: ["pcf"]       # PCF only (recommended)
```

### Output Directory

Fonts are organized by font family:
```
output/
  digits/
    digits-16pt.pcf
    digits-manifest.json
  menu/
    menu-12pt.pcf
    menu-16pt.pcf
    menu-manifest.json
```

**Glob-friendly naming**: All files for a font family share the same prefix (e.g., `digits-*`)

**Path Resolution:**
- Relative paths: Resolved from current directory or tool config default
- Absolute paths: Used as-is
- `~/` paths: Expanded to home directory

**Tool-Wide Config (Optional):**

Create `~/.config/cp-font-gen/config.yaml` to set a default output location:
```yaml
output_directory: ~/cp-projects/fonts
```

Now all font configs with `output: "output"` will generate to `~/cp-projects/fonts/output/{font_family}/`

## Using Fonts in CircuitPython

```python
import displayio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

# Load your custom font
font = bitmap_font.load_font("/fonts/custom-12pt.pcf")

# Use it
text = label.Label(font, text="25°C", color=0xFFFFFF)
text.x = 10
text.y = 20

# Add to display
display.show(text)
```

## Memory Savings

Real-world example:

| Font | Size | Savings |
|------|------|---------|
| Full Helvetica 12pt | ~50 KB | - |
| Digits + symbols only | ~2 KB | **96%** |
| Uppercase letters only | ~5 KB | **90%** |

## Output Files

After running `just generate`, check `output/`:

```
output/
└── custom/
    ├── custom-12pt.bdf          # ASCII format (optional)
    ├── custom-12pt.pcf          # Binary format (recommended)
    ├── custom-16pt.bdf
    ├── custom-16pt.pcf
    └── custom-manifest.json     # Metadata
```

**{font_family}-manifest.json** contains:
- Character count
- All included characters
- Unicode ranges
- Output directory path
- Generated file list (filenames only)

## Troubleshooting

### "otf2bdf not found"
See [System Tools Installation](quick-start.md#system-tools-installation) for install instructions.

### "bdftopcf not found"
See [System Tools Installation](quick-start.md#system-tools-installation) for install instructions.

### "Missing characters in output"
Check `{font_family}-manifest.json` to see what was included. Add missing characters to your config.

### "Font looks wrong on display"
Some fonts don't convert well to bitmap. Try:
- Use a simpler font (Helvetica, Arial)
- Increase the point size
- Check the font renders correctly in BDF format first

### "Command not found: cp-font-gen"
Run `uv sync` first to install the package.

## Examples

### Example 1: Temperature Display
```yaml
characters:
  inline: "0123456789.-°CF "
sizes: [16]
```
Generates a font with just digits, decimal, minus, degree symbol, and C/F.

### Example 2: Menu System
```yaml
characters:
  inline: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 "
sizes: [12, 16]
```
Alphanumeric with two sizes for headers and body text.

### Example 3: Custom Icons
```yaml
characters:
  unicode_ranges:
    - "U+2190-2193"  # Arrow symbols
    - "U+2600-2603"  # Weather symbols
sizes: [20]
```

## Tips

- **Start small**: Test with a few characters first
- **Use PCF**: Faster and smaller than BDF
- **Test on hardware**: What looks good on desktop may differ on your display
- **Check manifest**: Verify all characters were included
- **Reuse fonts**: Generate once, use across projects

## Development

For information on developing, testing, or contributing to cp-font-gen, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Resources

- [CircuitPython Font Guide](https://learn.adafruit.com/custom-fonts-for-pyportal-circuitpython-display)
- [Bitmap Font Library](https://docs.circuitpython.org/projects/bitmap-font/en/latest/)
- [Adafruit Learn Guides](https://learn.adafruit.com/)
