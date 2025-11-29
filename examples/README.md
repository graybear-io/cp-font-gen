# Font Generation Examples

Real-world examples showing different use cases for cp-font-gen.

**See also:** [config-template.yaml](config-template.yaml) - Complete configuration template with all available options documented.

## Quick Overview

| Example | Use Case | Characters | Size | Savings |
|---------|----------|------------|------|---------|
| [minimal](minimal/) | Counters, clocks | 10 digits | ~1.5 KB | 97% |
| [temperature](temperature/) | Weather, sensors | 16 chars + symbols | ~2 KB | 96% |
| [menu](menu/) | UI menus, settings | Full alphanumeric | ~8 KB | 92% |
| [icons](icons/) | Status, navigation | Unicode symbols | ~3 KB | 94% |
| [emoji](emoji/) | Visual indicators | 60 emoji | ~5 KB | 90% |
| [multilingual](multilingual/) | International text | 130+ chars | ~10 KB | 80% |

## How to Use

Each example directory contains:

- `config.yaml` - Font generation configuration
- `chars.txt` - Character file (when used)
- `README.md` - Detailed documentation

### Generate an Example

```bash
# Navigate to example
cd examples/minimal

# Generate fonts
cp-font-gen generate --config config.yaml

# Check output
ls output/
```

## Starting Points

### Just Need Numbers?

Start with **[minimal](minimal/)** - Only digits 0-9

### Sensor Display?

Use **[temperature](temperature/)** - Numbers + symbols

### Full UI?

Try **[menu](menu/)** - Complete alphanumeric

### Icons/Symbols?

Check **[icons](icons/)** - Unicode symbols

### Emoji & Status Indicators?

Try **[emoji](emoji/)** - Visual emoji for displays

### Multiple Languages?

See **[multilingual](multilingual/)** - International characters

## Tips

- **Start simple**: Begin with minimal example
- **Test often**: Generate and check `manifest.json`
- **Measure results**: Check actual file sizes
- **Iterate**: Add characters as needed
- **Document**: Note which characters you actually use

## Need Help?

Each example has detailed documentation in its README.md.

For more info:

- [Main README](../README.md) - Tool usage
- [DEVELOPMENT.md](../DEVELOPMENT.md) - Developer guide

## Customizing Examples

All examples can be customized:

1. Copy example to your project
2. Edit `config.yaml`
3. Modify characters as needed
4. Generate!

## Testing Before Hardware

```bash
# See what would be generated
cp-font-gen generate --config config.yaml --dry-run

# Check character list
cp-font-gen show --config config.yaml

# Verify a text file has needed chars
cp-font-gen extract your-text.txt
```

## Memory Planning

Use examples to estimate your font size:

- **10 characters**: ~1.5 KB (digits only)
- **20 characters**: ~2-3 KB (digits + symbols)
- **70 characters**: ~5-8 KB (alphanumeric)
- **130 characters**: ~10-12 KB (international)

Add ~2 KB per additional size variant (12pt, 16pt, etc.)

## Mixing Examples

Combine techniques from multiple examples:

```yaml
# Menu + Temperature
characters:
  file: "menu/chars.txt"  # Load alphanumeric
  inline: "°CF"           # Add temperature symbols
```

```yaml
# Minimal + Icons
characters:
  inline: "0123456789"    # Digits
  unicode_ranges:
    - "U+2190-2193"       # Add arrows
```

## Common Patterns

### Pattern 1: Inline for Small Sets

**Best for**: <20 characters

```yaml
characters:
  inline: "0123456789"
```

### Pattern 2: File for Readability

**Best for**: Custom character sets, easy editing

```yaml
characters:
  file: "chars.txt"
```

### Pattern 3: Unicode Ranges

**Best for**: Complete character ranges, symbols

```yaml
characters:
  unicode_ranges:
    - "U+0030-0039"  # Digits
    - "U+0041-005A"  # Uppercase
```

### Pattern 4: Combined

**Best for**: Complex requirements

```yaml
characters:
  inline: "0123456789"  # Basics
  file: "custom.txt"    # Additional
  unicode_ranges:
    - "U+2600-2603"     # Weather symbols
```
