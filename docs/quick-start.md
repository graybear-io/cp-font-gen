# Quick Start Guide

Get cp-font-gen running in 5 minutes.

## Prerequisites

### System Tools Installation

Install the required font conversion tools for your platform:

| **otf2bdf** | Operating System |
|------|---------------------|
| macOS | [Homebrew](https://formulae.brew.sh/formula/otf2bdf)<br/>`brew install otf2bdf` |
| Linux (Debian/Ubuntu) | [apt](https://packages.debian.org/search?keywords=otf2bdf)<br/>`sudo apt-get install otf2bdf` |
| Linux (Fedora/RHEL) | [dnf](https://packages.fedoraproject.org/search?query=otf2bdf)<br/>`sudo dnf install otf2bdf` |

| **bdftopcf** | Operating System |
| macOS | [Homebrew](https://formulae.brew.sh/formula/bdftopcf)<br/>`brew install bdftopcf` |
| Linux (Debian/Ubuntu) | [apt](https://packages.debian.org/search?keywords=bdftopcf)<br/>`sudo apt-get install bdftopcf` |
| Linux (Fedora/RHEL) | [dnf](https://packages.fedoraproject.org/search?query=bdftopcf)<br/>`sudo dnf install bdftopcf` |

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
uv run pytest
```

## Verify Installation

```bash
cp-font-gen check
```

You should see:

```text
Checking required tools...
✓ otf2bdf found
✓ bdftopcf found
✓ fonttools (pyftsubset) found

All required tools are installed!
```

## Your First Font

### 1. Create a Config File

Create `my-font.yaml`:

```yaml
source_font: "/System/Library/Fonts/Helvetica.ttc"

sizes:
  - 16

characters:
  inline: "0123456789°C "

output:
  directory: "output"
  font_family: "temperature"
  formats: ["pcf"]
```

### 2. Generate the Font

```bash
cp-font-gen generate --config my-font.yaml
```

Output:

```text
Loading config from my-font.yaml...
Collecting characters...
Found 13 unique characters: 0123456789°C

Generating fonts...
Processing sizes...
✓ Font generation complete!
  Generated 1 font files

Output files in: output/temperature/
```

### 3. Check the Output

```bash
ls output/temperature/
```

You should see:

```text
temperature-16pt.pcf
temperature-manifest.json
```

### 4. View the Manifest

```bash
cat output/temperature/temperature-manifest.json
```

See what characters were included and metadata about your font.

## Using Your Font in CircuitPython

Copy the `.pcf` file to your CircuitPython device:

```bash
cp output/temperature/temperature-16pt.pcf /Volumes/CIRCUITPY/fonts/
```

Then in your CircuitPython code:

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

## Next Steps

### Try More Examples

```bash
# See all available examples
ls examples/

# Try the emoji example
cp-font-gen generate --config examples/emoji/config.yaml
```

### Customize Your Font

Edit your config to:

- Add more characters: `inline: "ABC123..."`
- Generate multiple sizes: `sizes: [12, 16, 24]`
- Include Unicode ranges: See [Configuration Reference](configuration.md)

### Preview Your Font

Install and use cp-font-preview to see your font before deploying:

```bash
cd ../cp-font-preview
uv sync
cp-font-preview preview --manifest ../cp-font-gen/output/temperature/temperature-manifest.json
```

## Common Issues

### "otf2bdf not found"

See [System Tools Installation](#system-tools-installation) above for platform-specific install instructions.

### "bdftopcf not found"

See [System Tools Installation](#system-tools-installation) above for platform-specific install instructions.

### Characters appear as boxes on device

The characters aren't in your source font. Use `--debug` to see which are missing:

```bash
cp-font-gen generate --config my-font.yaml --debug
```

## Learn More

- **[User Guide](user-guide.md)** - Comprehensive documentation
- **[Configuration Reference](configuration.md)** - All config options
- **[Examples](../examples/)** - Real-world examples
- **[Troubleshooting](troubleshooting.md)** - Solve common problems
