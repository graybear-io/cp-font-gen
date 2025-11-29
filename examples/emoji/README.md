# Emoji Example

Font with emoji for visual displays and status indicators.

## Use Cases

- Status indicators (✅ ❌ ⚠️)
- Weather displays (🌤️ ⛅ ☁️ 🌧️)
- Progress/metrics (📊 📈 📉)
- System status (🔋 🔌 💡 🔥)
- User feedback (😀 😊 😎)
- Navigation (⬆️ ⬇️ ⬅️ ➡️)

## What's Included

**Emoji Categories**:
- **Numbers**: 0-9
- **Faces**: 😀 😃 😄 😁 😊 ☺️ 😎 😍
- **Status**: ✅ ❌ ⚠️ 🔴 🟢 🟡 🔵
- **Weather**: 🌡️ 💧 💨 🌤️ ⛅ ☁️ 🌧️ ⛈️
- **System**: 🔋 🔌 💡 🔥 ❄️
- **Arrows**: ⬆️ ⬇️ ⬅️ ➡️
- **Charts**: 📊 📈 📉 💾 📁
- **Misc**: ✨ 🎯 🎉 🏆 ⭐

**Total**: ~60 characters
**Size**: 32pt (larger for visibility)
**Format**: PCF only

## Important Notes

### Emoji Font Location

**macOS**: `/System/Library/Fonts/Apple Color Emoji.ttc`

**Linux**: Common locations:
- `/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf`
- `/usr/share/fonts/google-noto-emoji/NotoColorEmoji.ttf`

**Windows**: `C:\Windows\Fonts\seguiemj.ttf`

Update `source_font` in `config.yaml` for your system.

### Emoji Rendering

⚠️ **Important**: Most CircuitPython displays render emoji as monochrome (black/white) since PCF doesn't support color. The emoji will show as outlines/silhouettes.

For color emoji, you'd need to use bitmap images instead of fonts.

## Generate

```bash
cd examples/emoji
cp-font-gen generate --config config.yaml
```

## Output

```
output/
└── emoji/
    ├── emoji-32pt.pcf
    └── emoji-manifest.json
```

## Usage in CircuitPython

```python
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

# Load emoji font
emoji_font = bitmap_font.load_font("/fonts/emoji-32pt.pcf")

# Status indicator
status = label.Label(emoji_font, text="✅", color=0x00FF00)
status.x = 10
status.y = 10

# Weather display
weather = label.Label(emoji_font, text="⛅", color=0xFFFFFF)
weather.x = 50
weather.y = 10

# Battery level with emoji
battery_text = "🔋 100%"
battery = label.Label(emoji_font, text=battery_text, color=0xFFFF00)
```

## Example Displays

```python
# Status dashboard
"✅ WiFi Connected"
"🔋 85%"
"🌡️ 72°F"

# Weather forecast
"🌤️ Today: 75°F"
"⛅ Tomorrow: 68°F"
"🌧️ Wed: 62°F"

# Progress indicator
"📊 Loading..."
"✨ Complete!"

# Navigation menu
"⬆️ Scroll Up"
"⬇️ Scroll Down"
"➡️ Next Page"
```

## Customization

### Add More Emoji

Edit `chars.txt` and add any emoji you need:

```
# Food & Drink
🍕🍔🍟☕🍺

# Animals
🐶🐱🐭🐹🐰

# Activities
⚽🏀🎮🎲🎸
```

### Find Emoji Unicode

To find specific emoji:
1. Visit [Emojipedia](https://emojipedia.org/)
2. Search for your emoji
3. Copy the character or note its codepoint (e.g., U+1F600)

### Use Unicode Ranges

Instead of `chars.txt`, use unicode ranges in `config.yaml`:

```yaml
characters:
  unicode_ranges:
    - "U+1F600-1F64F"  # Emoticons
    - "U+2600-26FF"    # Miscellaneous Symbols
    - "U+2700-27BF"    # Dingbats
```

## Multi-Byte Unicode Support

Emoji are multi-byte Unicode characters (typically 4 bytes each). The tool handles this automatically:

- Files are read with UTF-8 encoding
- Character counting is correct (not byte counting)
- All Unicode ranges supported (including emoji)

No special configuration needed!

## Troubleshooting

**"Font not found"**: Update `source_font` path for your operating system.

**"Emoji appear blank"**: Some emoji aren't in all fonts. Try a different emoji font:
- Noto Color Emoji (Google)
- Segoe UI Emoji (Windows)
- Apple Color Emoji (macOS)

**"Size too large"**: Emoji fonts can be big. Reduce character count or use smaller size (16pt, 24pt).
