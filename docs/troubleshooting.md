# Troubleshooting Guide

Solutions to common problems when using cp-font-gen.

## Installation Issues

### "otf2bdf not found"

**Problem:** The `otf2bdf` command is not installed.

**Solution:** See [System Tools Installation](quick-start.md#system-tools-installation) for platform-specific install instructions.

### "bdftopcf not found"

**Problem:** The `bdftopcf` command is not installed.

**Solution:** See [System Tools Installation](quick-start.md#system-tools-installation) for platform-specific install instructions.

### "Command not found: cp-font-gen"

**Problem:** The package is not installed or not in PATH.

**Solution:**

If using uv (developer mode):
```bash
cd cp-font-gen
uv sync
# Then run with: uv run cp-font-gen or cp-font-gen
```

If you installed with pip:
```bash
pip install --upgrade cp-font-gen
```

Check installation:
```bash
which cp-font-gen
cp-font-gen --version
```

---

## Font Generation Issues

### "No font files were generated"

**Problem:** Font generation completed but no PCF/BDF files created.

**Diagnosis:**
```bash
cp-font-gen generate --config config.yaml --debug
```

**Common causes:**

1. **Characters not in source font**
   - Solution: Use `--debug` to see character coverage
   - Try a Unicode font like Arial Unicode.ttf

2. **Invalid source font path**
   - Solution: Check the path in your config
   - Use absolute paths or verify relative path is correct

3. **Permissions issue**
   - Solution: Check you have write access to output directory

### "otf2bdf: no glyphs generated from 'font.ttf'"

**Problem:** The source font doesn't contain the requested characters.

**Diagnosis:**
```bash
cp-font-gen generate --config config.yaml --debug
```

Look for:
```
WARNING: 23 of 24 requested characters not found in source font

Missing characters:
  ✗ U+2190 (←)
  ✗ U+2191 (↑)
  ...
```

**Solutions:**

1. **Use a Unicode font** for symbols:
   ```yaml
   # macOS
   source_font: "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"

   # Linux
   source_font: "/usr/share/fonts/truetype/unifont/unifont.ttf"
   ```

2. **Verify characters are in font** before generating:
   ```bash
   cp-font-gen show --config config.yaml
   ```

3. **Use different character ranges** that exist in your font

### "Font looks wrong on CircuitPython device"

**Problem:** Font displays incorrectly or garbled.

**Solutions:**

1. **Make sure you're using PCF format:**
   ```yaml
   output:
     formats: ["pcf"]  # Not BDF
   ```

2. **Check font size is appropriate:**
   - Very large fonts (48pt+) may not render well as bitmaps
   - Very small fonts (< 8pt) may be unreadable
   - Try sizes 12-24pt first

3. **Verify the font loaded correctly:**
   ```python
   import adafruit_bitmap_font
   try:
       font = adafruit_bitmap_font.bitmap_font.load_font("/fonts/my-font.pcf")
       print(f"Font loaded: {font}")
   except Exception as e:
       print(f"Error loading font: {e}")
   ```

4. **Check CircuitPython version:**
   - Ensure you're using a recent CircuitPython version
   - Font support improved significantly in version 7.0+

### Characters appear as boxes on device

**Problem:** Some characters display as empty boxes or squares.

**Diagnosis:**

1. **Check the manifest:**
   ```bash
   cat output/my-font/my-font-manifest.json
   ```

2. **Use debug mode:**
   ```bash
   cp-font-gen generate --config config.yaml --debug
   ```

**Solutions:**

1. **Characters weren't included:**
   - Add missing characters to your config
   - Regenerate the font

2. **Characters not in source font:**
   - Use `--debug` to see which are missing
   - Switch to a font that has those characters

3. **Wrong font loaded on device:**
   - Verify you copied the correct PCF file
   - Check the font path in your CircuitPython code

---

## Configuration Issues

### "Config file not found"

**Problem:** Can't load the config file.

**Solution:**

1. **Check the path:**
   ```bash
   ls -l config.yaml  # Verify file exists
   ```

2. **Use absolute path:**
   ```bash
   cp-font-gen generate --config /full/path/to/config.yaml
   ```

3. **Check working directory:**
   ```bash
   pwd  # Where am I?
   cd /path/to/config/directory
   cp-font-gen generate --config config.yaml
   ```

### "YAML parse error"

**Problem:** Config file has syntax errors.

**Common issues:**

1. **Indentation must be spaces (not tabs)**
   ```yaml
   # ✗ Wrong (tabs)
   characters:
   →→inline: "ABC"

   # ✓ Correct (spaces)
   characters:
     inline: "ABC"
   ```

2. **Quotes needed for special characters:**
   ```yaml
   # ✗ Wrong
   inline: "ABC:123"  # Colon after quote

   # ✓ Correct
   inline: "ABC:123"
   ```

3. **List format:**
   ```yaml
   # ✗ Wrong
   sizes: 12, 16, 24

   # ✓ Correct
   sizes:
     - 12
     - 16
     - 24

   # ✓ Also correct
   sizes: [12, 16, 24]
   ```

**Validation:**
```bash
# Check config syntax
cp-font-gen show --config config.yaml
```

### "Missing required field"

**Problem:** Config is missing required sections.

**Required fields:**
- `source_font`
- `sizes`
- `characters` (at least one method)
- `output.directory`
- `output.font_family`
- `output.formats`

**Minimal valid config:**
```yaml
source_font: "/path/to/font.ttf"
sizes: [16]
characters:
  inline: "ABC"
output:
  directory: "output"
  font_family: "test"
  formats: ["pcf"]
```

---

## Output Issues

### "Permission denied" writing to output directory

**Problem:** Can't write to output directory.

**Solution:**

1. **Check permissions:**
   ```bash
   ls -ld output/
   ```

2. **Create directory first:**
   ```bash
   mkdir -p output
   ```

3. **Use a directory you own:**
   ```yaml
   output:
     directory: "~/my-fonts"
   ```

### "Output directory already exists"

**Note:** This is OK! cp-font-gen will overwrite existing files.

To start fresh:
```bash
rm -rf output/my-font/
cp-font-gen generate --config config.yaml
```

### Manifest file is missing debug info

**Problem:** Running with `--debug` but manifest doesn't have debug section.

**Solution:**

1. **Ensure metadata is enabled:**
   ```yaml
   output:
     metadata: true
   ```

2. **Use --debug flag:**
   ```bash
   cp-font-gen generate --config config.yaml --debug
   ```

---

## Memory and Performance Issues

### Font generation is slow

**Normal behavior:** Font subsetting takes 1-2 seconds per font size.

**If it's very slow (> 10 sec per size):**

1. **Check character count:**
   ```bash
   cp-font-gen show --config config.yaml
   ```
   - 1000+ characters will be slower
   - Consider reducing character set

2. **Large source font:**
   - Some TTC files contain multiple fonts
   - Try extracting a single TTF variant

### Generated font is too large for device

**Problem:** Font file doesn't fit in CircuitPython flash storage.

**Solutions:**

1. **Use PCF instead of BDF:**
   - PCF is binary (smaller)
   - BDF is text (much larger)

2. **Reduce character count:**
   - Only include characters you actually use
   - Remove unused symbols

3. **Use smaller font size:**
   - Try 12pt instead of 24pt

4. **Generate multiple fonts:**
   - One font for digits (small)
   - One font for letters (small)
   - Instead of one font with everything (large)

**Check font size:**
```bash
ls -lh output/my-font/*.pcf
```

---

## CircuitPython Device Issues

### Font won't load on CircuitPython device

**Problem:** Error loading font in CircuitPython code.

**Check:**

1. **File exists:**
   ```bash
   ls /Volumes/CIRCUITPY/fonts/
   ```

2. **File is PCF format:**
   ```bash
   file output/my-font/my-font-16pt.pcf
   # Should say: "X11 Portable Compiled Font data"
   ```

3. **Path is correct in code:**
   ```python
   # ✗ Wrong
   font = bitmap_font.load_font("my-font-16pt.pcf")

   # ✓ Correct
   font = bitmap_font.load_font("/fonts/my-font-16pt.pcf")
   ```

4. **CircuitPython version supports fonts:**
   - Requires CircuitPython 6.0+
   - Bitmap font support in 7.0+ is better

### Text doesn't appear on display

**Problem:** Font loads but text doesn't show.

**Check:**

1. **Text color vs background:**
   ```python
   # White text on white background won't show
   text = label.Label(font, text="Hello", color=0xFFFFFF)
   ```

2. **Text position:**
   ```python
   # Offscreen text won't show
   text.x = 10  # Should be visible
   text.y = 20
   ```

3. **Text added to display group:**
   ```python
   main_group = displayio.Group()
   main_group.append(text)  # Don't forget this!
   display.root_group = main_group
   ```

---

## Getting Help

If you're still stuck:

1. **Run with debug mode:**
   ```bash
   cp-font-gen generate --config config.yaml --debug
   ```

2. **Check the examples:**
   ```bash
   ls examples/
   # Try a working example
   cp-font-gen generate --config examples/minimal/config.yaml
   ```

3. **Read the logs:**
   - Debug mode shows exactly what's happening
   - Check for warnings about missing characters

4. **Open an issue:**
   - Include your config file
   - Include debug output
   - Describe what you expected vs what happened

---

## See Also

- [Configuration Reference](configuration.md) - All config options
- [Logging Guide](logging.md) - Understanding debug output
- [Examples](../examples/) - Working example configs
- [Development Guide](development.md) - For contributors
