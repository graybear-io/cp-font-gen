# Issue #4: UTF-8 Encoding Error Fix Documentation

**Issue:** Icons example fails to generate fonts with UTF-8 encoding error
**Status:** ✅ FIXED
**Date Fixed:** 2025-11-30

## Summary

The icons example failed during font generation with the error:
```
ERROR: Failed to fix BDF encodings: 'utf-8' codec can't decode byte 0xae in position 649: invalid start byte
```

This occurred when processing BDF files that contained Latin-1 (ISO-8859-1) encoded metadata from fonts with copyright symbols (©), registered trademarks (®), or other extended Latin characters.

## Root Cause Analysis

### The Problem

The `fix_bdf_encodings()` function in `converter.py` was opening BDF files without specifying an encoding:

```python
# Line 131 (old code)
with open(bdf_path) as f:  # Defaults to UTF-8
    lines = f.readlines()
```

This defaulted to UTF-8 encoding, but **BDF files from otf2bdf use ISO-8859-1 (Latin-1)** encoding for metadata.

### Why It Failed

1. **otf2bdf** generates BDF files in ISO-8859-1 (Latin-1) encoding
2. When processing **Arial Unicode.ttf**, the font metadata contained extended characters
3. **Byte 0xae** (at position 649) is the registered trademark symbol **®** in Latin-1
4. This byte is **invalid in UTF-8** (UTF-8 requires multi-byte sequences for non-ASCII chars)
5. Python's UTF-8 decoder threw: `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xae`

### Why Other Examples Worked

| Example | Status | Reason |
|---------|--------|--------|
| minimal (digits) | ✅ Works | Only ASCII characters in font metadata |
| emoji | ✅ Works | Font metadata happens to be ASCII-compatible |
| menu | ✅ Works | Font metadata is ASCII |
| multilingual | ✅ Works | Font metadata is ASCII |
| temperature | ✅ Works | Font metadata is ASCII |
| **icons** | ❌ Failed | Arial Unicode.ttf has © or ® symbols in metadata |

## Specification Research

### BDF File Format Encoding

According to the official specifications:

- **X.org BDF Specification**: "BDF files are distributed in USASCII-encoded form, with X Window properties specified using ISO 8859-1 encoding"
- **Adobe BDF Specification**: "A generic BDF file is in ASCII encoding, with X Window properties specified using ISO 8859-1 encoding, which is an extension of ASCII"

Sources:
- [X.org BDF Specification](https://www.x.org/docs/BDF/bdf.pdf)
- [Adobe BDF Specification](https://adobe-type-tools.github.io/font-tech-notes/pdfs/5005.BDF_Spec.pdf)
- [otf2bdf Manual](http://sofia.nmsu.edu/~mleisher/Software/otf2bdf/otf2bdf-man.html)

### Key Findings

- **BDF spec explicitly allows ISO-8859-1** (Latin-1) for metadata and properties
- **otf2bdf commonly outputs Latin-1** when source fonts contain extended characters
- **ISO-8859-1 is a superset of ASCII** (bytes 0-127 are identical)
- **UTF-8 is NOT compatible with Latin-1** for bytes 128-255

## Risk Analysis: Why Not Force Latin-1?

Before implementing the fix, we analyzed the risks of blindly forcing Latin-1 encoding:

### Risk 1: Mixed Encoding Sources
- **Assumption**: All BDF files use Latin-1
- **Risk**: What if otf2bdf changes to UTF-8 in future versions?
- **Impact**: Reading UTF-8 as Latin-1 corrupts multi-byte characters
  - UTF-8 "é" = bytes `[0xC3, 0xA9]`
  - Read as Latin-1 = "Ã©" (2 wrong characters!)

### Risk 2: Write/Read Mismatch
- Reading with one encoding, writing with another corrupts data
- Must preserve the original encoding when writing back

### Risk 3: Test Suite Had No Coverage
- All existing tests used ASCII-only content
- No test for Latin-1 encoded BDF files
- Tests passed "by accident" because ASCII is valid in both encodings

## The Solution: Defensive Encoding with Fallback

Instead of assuming Latin-1, we implemented a **try UTF-8 first, gracefully fallback to Latin-1** approach:

```python
def fix_bdf_encodings(
    bdf_path: str, chars: set[str], logger: Optional["GenerationLogger"] = None
) -> bool:
    """Fix ENCODING values in BDF to match Unicode codepoints.

    Issue #4: BDF files may use different text encodings depending on the generator:
    - The BDF specification allows ASCII with ISO-8859-1 (Latin-1)
    - otf2bdf commonly outputs ISO-8859-1 encoded metadata
    - This function tries UTF-8 first, then gracefully falls back to Latin-1
    """
    try:
        # Convert chars to sorted list of Unicode codepoints
        char_list = sorted(chars)
        codepoints = [ord(c) for c in char_list]

        # Try UTF-8 first (most common), fallback to Latin-1 (BDF spec)
        encoding_used = "utf-8"
        try:
            with open(bdf_path, encoding="utf-8") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # BDF spec allows ISO-8859-1 (Latin-1) for X Window properties
            if logger and logger.debug:
                logger.info("BDF contains Latin-1 encoded bytes, using ISO-8859-1 encoding")
            encoding_used = "latin-1"
            with open(bdf_path, encoding="latin-1") as f:
                lines = f.readlines()

        # ... fix encodings ...

        # Write back using the SAME encoding we read with (preserves data integrity)
        with open(bdf_path, "w", encoding=encoding_used) as f:
            f.writelines(output_lines)

        return True

    except Exception as e:
        if logger:
            logger.error(f"Failed to fix BDF encodings: {str(e)}")
        return False
```

## Why This Approach is Better

1. **Graceful Degradation**: Handles both UTF-8 and Latin-1 files automatically
2. **No Assumptions**: Doesn't break if otf2bdf behavior changes in the future
3. **Preserves Encoding**: Writes back in the same encoding we read (prevents corruption)
4. **Explicit Logging**: Debug mode shows which encoding was used
5. **Safe**: Won't corrupt data from either encoding
6. **Future-Proof**: Works with any encoding that otf2bdf might use

## Test Coverage Added

### New Test: `test_fix_bdf_encodings_handles_latin1_metadata`

Located in `tests/test_converter.py`, this test:

1. Creates a BDF file with Latin-1 encoded metadata (© and ® symbols)
2. Verifies it cannot be read as UTF-8 (throws UnicodeDecodeError)
3. Calls `fix_bdf_encodings()` and verifies it succeeds
4. Checks that ENCODING values are fixed correctly
5. Verifies Latin-1 metadata characters are preserved

### New Test Helper: `create_test_bdf_with_latin1_metadata`

Located in `tests/conftest.py`, this helper:
- Creates a realistic BDF file with Latin-1 metadata
- Includes copyright (©) and registered trademark (®) symbols
- Simulates what otf2bdf outputs for fonts like Arial Unicode

### Updated Helpers

- `extract_bdf_encodings()`: Now uses the same UTF-8 → Latin-1 fallback
- `create_test_bdf_with_wrong_encodings()`: Added optional `encoding` parameter

## Verification

### Test Results

```bash
$ uv run python -m pytest tests/test_converter.py -v
============================= test session starts ==============================
tests/test_converter.py::test_fix_bdf_encodings_corrects_sequential_to_unicode PASSED
tests/test_converter.py::test_fix_bdf_encodings_preserves_correct_encodings PASSED
tests/test_converter.py::test_fix_bdf_encodings_handles_various_characters PASSED
tests/test_converter.py::test_fix_bdf_encodings_handles_latin1_metadata PASSED  ✨ NEW
...
========================= 17 passed, 2 skipped ================================
```

### Icons Example Now Works

```bash
$ uv run cp-font-gen generate --config examples/icons/config.yaml --verbose

Loading config from examples/icons/config.yaml...
Collecting characters...
Found 24 unique characters: •←↑→↓↰↱↲↳○●☀☁☂☃☔♪♫⛄⛅✓✔✗✘

Generating fonts for 1 size(s)

Processing size 24pt:
  ✓ [subset_font] fontTools.subset → icons-24pt-subset.ttf (21.0 KB) (22 glyphs)
  ✓ [convert_to_bdf] otf2bdf → icons-24pt.bdf (5.0 KB)
  ✓ [convert_to_pcf] bdftopcf → icons-24pt.pcf (6.4 KB)
  ✓ Wrote manifest to icons-manifest.json

✓ Font generation complete!
  Generated 1 font files
```

**Before Fix:**
```json
{
  "generated_files": [],  // ❌ Empty!
  "character_count": 24,
  ...
}
```

**After Fix:**
```json
{
  "generated_files": ["icons-24pt.pcf"],  // ✅ Success!
  "character_count": 24,
  ...
}
```

## Files Modified

1. **src/cp_font_gen/converter.py**
   - Updated `fix_bdf_encodings()` with UTF-8 → Latin-1 fallback
   - Added comprehensive docstring documenting Issue #4
   - Preserves original encoding when writing

2. **tests/conftest.py**
   - Updated `extract_bdf_encodings()` to use same fallback logic
   - Updated `create_test_bdf_with_wrong_encodings()` with encoding parameter
   - Added `create_test_bdf_with_latin1_metadata()` helper

3. **tests/test_converter.py**
   - Added `test_fix_bdf_encodings_handles_latin1_metadata()` test
   - Comprehensive test verifying Latin-1 handling and metadata preservation

## Lessons Learned

1. **Always specify file encodings explicitly** - Don't rely on system defaults
2. **Test with non-ASCII data** - ASCII-only tests can hide encoding issues
3. **Follow specifications** - BDF spec explicitly allows Latin-1
4. **Defensive programming** - Try/fallback is safer than assumptions
5. **Preserve data integrity** - Write back in the same encoding you read
6. **Document research** - Future maintainers need context for encoding decisions

## References

- [Issue #4 on GitHub](https://github.com/graybear-io/cp-font-gen/issues/4)
- [Glyph Bitmap Distribution Format - Wikipedia](https://en.wikipedia.org/wiki/Glyph_Bitmap_Distribution_Format)
- [X.org BDF Specification](https://www.x.org/docs/BDF/bdf.pdf)
- [Adobe BDF Specification](https://adobe-type-tools.github.io/font-tech-notes/pdfs/5005.BDF_Spec.pdf)
- [otf2bdf Manual](http://sofia.nmsu.edu/~mleisher/Software/otf2bdf/otf2bdf-man.html)
- [otf2bdf on Linux man pages](https://linux.die.net/man/1/otf2bdf)

---

**Status**: ✅ Issue resolved, fix tested and documented
**Impact**: All examples now work correctly, including icons with Unicode symbols
**Test Coverage**: Added comprehensive test for Latin-1 encoding scenarios
