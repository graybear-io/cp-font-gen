# Temperature Display Example

Font optimized for displaying temperature readings with proper symbols.

## Use Cases

- Weather stations
- Thermometers
- Environmental sensors
- Climate control displays
- Indoor/outdoor temperature monitors

## What's Included

**Characters**: `0123456789.-°CF ` (16 characters)
- Digits 0-9
- Decimal point
- Minus sign (negative temps)
- Degree symbol (°)
- C and F (Celsius/Fahrenheit)
- Space

**Size**: 20pt (large and readable)
**Format**: PCF only

## Memory Savings

- Full font: ~50 KB
- This subset: ~2 KB
- **Savings: 96%**

## Generate

```bash
cd examples/temperature
cp-font-gen generate --config config.yaml
```

## Output

```
output/
└── temp/
    ├── temp-20pt.pcf
    └── temp-manifest.json
```

## Usage in CircuitPython

```python
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
import adafruit_bme280  # Example sensor

# Load font
font = bitmap_font.load_font("/fonts/temp-20pt.pcf")

# Read sensor
sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c)
temp_c = sensor.temperature

# Display with proper formatting
temp_text = label.Label(font, text=f"{temp_c:.1f}°C", color=0xFF0000)
temp_text.x = 10
temp_text.y = 30
display.show(temp_text)
```

## Display Examples

```
"72.5°F"
"-5.2°C"
"98.6°F"
"22.3°C"
```

## Customization

Add humidity reading? Edit `config.yaml`:

```yaml
characters:
  inline: "0123456789.-°CF %RH"  # Add % and RH for relative humidity
```
