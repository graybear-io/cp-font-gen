# Menu System Example

Full alphanumeric font for interactive menus and user interfaces.

## Use Cases

- Menu systems
- Settings screens
- User interfaces
- Form labels
- Help text
- Status messages

## What's Included

**Characters**: Full ASCII alphanumeric
- Uppercase A-Z
- Lowercase a-z
- Digits 0-9
- Basic punctuation: `. , ! ? : -`
- Space

**Total**: 69 characters
**Sizes**: 12pt (body), 16pt (headers)
**Format**: PCF only

## Memory Savings

- Full font (12pt + 16pt): ~100 KB
- These subsets: ~8 KB
- **Savings: 92%**

## Generate

```bash
cd examples/menu
cp-font-gen generate --config config.yaml
```

## Output

```
output/
└── menu/
    ├── menu-12pt.pcf
    ├── menu-16pt.pcf
    └── menu-manifest.json
```

## Usage in CircuitPython

```python
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

# Load fonts
header_font = bitmap_font.load_font("/fonts/menu-16pt.pcf")
body_font = bitmap_font.load_font("/fonts/menu-12pt.pcf")

# Create menu
menu_items = ["Settings", "WiFi", "Display", "About"]

# Header
header = label.Label(header_font, text="Menu", color=0xFFFFFF)
header.x = 10
header.y = 10

# Menu items
for i, item in enumerate(menu_items):
    item_label = label.Label(body_font, text=item, color=0xCCCCCC)
    item_label.x = 20
    item_label.y = 40 + (i * 20)
```

## Display Example

```
Menu               <- 16pt header
  Settings         <- 12pt items
  WiFi
  Display
  About
```

## Customization

Need more punctuation? Edit `chars.txt`:

```
.,!?:-()/&
```

Want emoji or symbols? Use unicode ranges in `config.yaml`:

```yaml
characters:
  file: "chars.txt"
  unicode_ranges:
    - "U+2190-2193"  # Arrows
    - "U+2713"       # Checkmark
```
