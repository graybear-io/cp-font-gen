# Minimal Example: Digits Only

The simplest possible font - just the digits 0-9.

## Use Cases

- Simple counters
- Numeric displays
- Digital clocks
- Scoreboards
- Any display showing only numbers

## What's Included

**Characters**: `0123456789` (10 characters)
**Size**: 16pt
**Format**: PCF only (most efficient)

## Memory Savings

- Full font: ~50 KB
- This subset: ~1.5 KB
- **Savings: 97%**

## Generate

```bash
cd examples/minimal
cp-font-gen generate --config config.yaml
```

## Output

```
output/
└── digits/
    ├── digits-16pt.pcf
    └── digits-manifest.json
```

## Usage in CircuitPython

```python
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

font = bitmap_font.load_font("/fonts/digits-16pt.pcf")
counter = label.Label(font, text="42", color=0xFFFFFF)
```

## Customization

Want to add more characters? Edit `config.yaml`:

```yaml
characters:
  inline: "0123456789:."  # Add colon and decimal for time/decimals
```
