# Multilingual Example

Font with international characters for displaying multiple languages.

## Use Cases

- Multi-language interfaces
- Language learning devices
- Travel translators
- International weather/news displays
- Displaying names from different countries

## What's Included

**Character Sets**:
- Standard ASCII (A-Z, a-z, 0-9)
- Accented vowels (àáâãäå èéêë etc.)
- Spanish special chars (ñÑ ¡¿)
- French special chars (ç)
- German umlauts (äöü)
- And more!

**Total**: ~130 characters
**Size**: 14pt
**Format**: PCF only

## Languages Supported

With these characters you can display:
- **English** - Full support
- **Spanish** - Full support (¡Hola!)
- **French** - Full support (Bonjour!)
- **German** - Full support (Guten Tag!)
- **Italian** - Full support (Ciao!)
- **Portuguese** - Full support (Olá!)

## Memory Savings

- Full font: ~50 KB
- This subset: ~10 KB
- **Savings: 80%**

## Generate

```bash
cd examples/multilingual
cp-font-gen generate --config config.yaml
```

## Output

```
output/
└── multi/
    ├── multi-14pt.pcf
    └── multi-manifest.json
```

## Usage in CircuitPython

```python
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

font = bitmap_font.load_font("/fonts/multi-14pt.pcf")

# Display in different languages
greetings = [
    "Hello!",      # English
    "¡Hola!",      # Spanish
    "Bonjour!",    # French
    "Guten Tag!",  # German
    "Ciao!",       # Italian
]

for i, greeting in enumerate(greetings):
    text = label.Label(font, text=greeting, color=0xFFFFFF)
    text.y = 10 + (i * 20)
```

## Adding More Languages

### Cyrillic (Russian, Ukrainian, etc.)
```yaml
unicode_ranges:
  - "U+0400-04FF"  # Cyrillic alphabet
```

### Greek
```yaml
unicode_ranges:
  - "U+0370-03FF"  # Greek alphabet
```

### Arabic
```yaml
unicode_ranges:
  - "U+0600-06FF"  # Arabic
```

**Warning**: Some scripts (CJK, Arabic) have thousands of characters and will create large fonts!

## Finding Unicode Ranges

Resources:
- [Unicode Charts](https://unicode.org/charts/)
- [Wikipedia: Unicode Blocks](https://en.wikipedia.org/wiki/Unicode_block)

## Testing Your Characters

Want to verify characters are included?

```bash
# Create test file with your text
echo "Héllo Wörld" > test.txt

# Check unicode points
cp-font-gen extract test.txt
```

## Tips

- Start with just the characters you need
- Test on actual hardware (some displays handle unicode differently)
- Check `manifest.json` to verify all characters were included
- Some fonts render accents better than others - try different source fonts
