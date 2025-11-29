# Unicode Icons/Symbols Example

Font containing unicode symbols for icons and visual indicators.

## Use Cases

- Weather displays (☀ ☁ ☂)
- Navigation indicators (← → ↑ ↓)
- Status markers (✓ ✗)
- UI elements (• ○)
- Fun displays (♪ ♫)

## What's Included

**Symbol Sets**:
- Arrows: ← ↑ → ↓ and curved arrows
- Weather: ☀ ☁ ☂ ☃ ⛄ ⛅
- Checkmarks: ✓ ✔
- X marks: ✗ ✘
- Bullets: • ● ○
- Music: ♪ ♫

**Size**: 24pt (large for visibility)
**Format**: PCF only

## Memory Savings

- Full font: ~50 KB
- These symbols: ~3 KB
- **Savings: 94%**

## Generate

```bash
cd examples/icons
cp-font-gen generate --config config.yaml
```

## Output

```
output/
└── icons/
    ├── icons-24pt.pcf
    └── icons-manifest.json
```

## Usage in CircuitPython

```python
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

# Load icon font
icon_font = bitmap_font.load_font("/fonts/icons-24pt.pcf")

# Weather display
weather = label.Label(icon_font, text="☀", color=0xFFFF00)  # Sun
weather.x = 10
weather.y = 10

# Status indicator
status = label.Label(icon_font, text="✓", color=0x00FF00)  # Checkmark
status.x = 50
status.y = 10

# Navigation
nav = label.Label(icon_font, text="→", color=0xFFFFFF)  # Arrow
nav.x = 90
nav.y = 10
```

## Display Examples

```python
# Weather forecast
"☀ 72°F"
"☁ 65°F"
"☂ 58°F"

# Menu navigation
"→ Settings"
"← Back"

# Task status
"✓ Connected"
"✗ Error"
"• Waiting"
```

## Customization

Need different symbols? Check [Unicode charts](https://unicode.org/charts/):

```yaml
characters:
  unicode_ranges:
    - "U+2665"       # ♥ Heart
    - "U+2764"       # ❤ Heavy heart
    - "U+1F4A1"      # 💡 Light bulb
```

## Testing Symbols

Not sure if a symbol will work? Use `just extract`:

```bash
echo "☀☁☂" > test.txt
cp-font-gen extract test.txt
```

This shows the unicode points for your symbols.
