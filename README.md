# cp-font-gen

Generate minimal bitmap fonts for memory-constrained CircuitPython devices.

## Quick Start

```bash
# Install system dependencies (otf2bdf, bdftopcf)
# See: docs/quick-start.md#system-tools-installation

# Install cp-font-gen
uv sync  # For developers
# or: pip install cp-font-gen (once published)

# Create a config
cat > my-font.yaml <<EOF
source_font: "/System/Library/Fonts/Helvetica.ttc"
sizes: [16]
characters:
  inline: "0123456789°C "
output:
  directory: "output"
  font_family: "temperature"
  formats: ["pcf"]
EOF

# Generate fonts
cp-font-gen generate --config my-font.yaml

# Use on CircuitPython device
cp output/temperature/*.pcf /Volumes/CIRCUITPY/fonts/
```

**→ Full setup guide: [docs/quick-start.md](docs/quick-start.md)**

## What It Does

CircuitPython devices have limited flash storage (KB, not MB). Full fonts waste precious space.

**cp-font-gen** creates custom bitmap fonts containing **only the glyphs you need:**

| Font | Size | Savings |
|------|------|---------|
| Full Helvetica 12pt | ~50 KB | - |
| Digits + symbols only | ~2 KB | **96%** |
| Uppercase letters only | ~5 KB | **90%** |

## Features

- **Multiple character sources** - Inline, file, or Unicode ranges
- **Multi-size generation** - Create 12pt, 16pt, 24pt in one run
- **PCF & BDF formats** - Binary (fast) or ASCII (readable)
- **Character coverage analysis** - See what's missing before you deploy
- **Manifest metadata** - JSON file with generation details
- **Debug mode** - Find out why characters don't appear

## Documentation

- **[Quick Start](docs/quick-start.md)** - Get running in 5 minutes
- **[User Guide](docs/user-guide.md)** - Comprehensive usage documentation
- **[Configuration Reference](docs/configuration.md)** - All config options explained
- **[Examples](examples/)** - Real-world example configs
- **[Logging & Debugging](docs/logging.md)** - Verbose and debug modes
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[Development Guide](docs/development.md)** - Contributing and testing
- **[Architecture](docs/architecture.md)** - Design decisions and internals

## Installation

### For Users

```bash
pip install cp-font-gen  # (once published to PyPI)
```

### For Developers

```bash
git clone https://github.com/graybear-io/cp-font-gen.git
cd cp-font-gen
uv sync
```

**Prerequisites:**

- Python 3.10+
- System tools: `otf2bdf`, `bdftopcf` (see [Quick Start](docs/quick-start.md))

## Usage

### Basic Commands

```bash
# Generate fonts from config
cp-font-gen generate --config config.yaml

# Check if required tools are installed
cp-font-gen check

# Preview characters without generating
cp-font-gen show --config config.yaml

# Extract characters from a file
cp-font-gen extract my_text.txt

# Verbose output
cp-font-gen generate --config config.yaml --verbose

# Debug mode with character coverage analysis
cp-font-gen generate --config config.yaml --debug
```

### Using Generated Fonts

```python
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

# Load your custom font
font = bitmap_font.load_font("/fonts/temperature-16pt.pcf")

# Use it
text = label.Label(font, text="25°C", color=0xFFFFFF)
text.x = 10
text.y = 20

display.show(text)
```

## Configuration Example

```yaml
source_font: "/System/Library/Fonts/Helvetica.ttc"

sizes:
  - 12
  - 16
  - 24

characters:
  inline: "0123456789°C "
  file: "chars.txt"
  unicode_ranges:
    - "U+0041-005A"  # A-Z
    - "U+0061-007A"  # a-z

output:
  directory: "output"
  font_family: "custom"
  formats: ["pcf"]
  metadata: true

logging:
  level: "verbose"
```

**→ Full reference: [docs/configuration.md](docs/configuration.md)**

## Examples

Explore working examples in the [`examples/`](examples/) directory:

- **[minimal](examples/minimal/)** - Simplest possible config
- **[temperature](examples/temperature/)** - Digits + degree symbol
- **[menu](examples/menu/)** - Letters and punctuation
- **[emoji](examples/emoji/)** - Unicode emoji and symbols
- **[icons](examples/icons/)** - Arrow and weather symbols
- **[multilingual](examples/multilingual/)** - Accented characters

Try an example:

```bash
cp-font-gen generate --config examples/temperature/config.yaml
```

## Common Patterns

**Temperature display:**

```yaml
characters:
  inline: "0123456789.°CF "
```

**Menu system:**

```yaml
characters:
  unicode_ranges:
    - "U+0041-005A"  # A-Z
    - "U+0061-007A"  # a-z
  inline: " :-_()[]"
```

**Icon font:**

```yaml
characters:
  unicode_ranges:
    - "U+2190-2193"  # Arrows ← ↑ → ↓
    - "U+2600-2603"  # Weather ☀ ☁ ☂
```

## Related Tools

- **[cp-font-preview](../cp-font-preview/)** - Preview fonts locally before deploying
- **[Blinka](https://github.com/adafruit/Adafruit_Blinka_Displayio)** - CircuitPython compatibility layer

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and pull request guidelines.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Credits

Built for the CircuitPython community. Uses:

- [fonttools](https://github.com/fonttools/fonttools) - Font subsetting
- [otf2bdf](https://github.com/jirutka/otf2bdf) - TrueType to BDF conversion
- [bdftopcf](https://gitlab.freedesktop.org/xorg/app/bdftopcf) - BDF to PCF conversion

---

**Need help?** Check [docs/troubleshooting.md](docs/troubleshooting.md) or [open an issue](../../issues).
