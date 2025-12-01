"""Tests for converter.py - Font conversion functions.

Includes unit tests for fix_bdf_encodings() and regression tests
for the BDF encoding bug (Issue #1).
"""

import os
from unittest import mock

import pytest

from cp_font_gen.converter import (
    convert_to_bdf,
    convert_to_pcf,
    fix_bdf_encodings,
    generate_subset_font,
)
from cp_font_gen.logger import GenerationLogger

from .conftest import create_test_bdf_with_wrong_encodings, extract_bdf_encodings

# =============================================================================
# Unit Tests: fix_bdf_encodings() Function
# =============================================================================
# Originally from Issue #1 - tests for the encoding fix function


def test_fix_bdf_encodings_corrects_sequential_to_unicode(tmp_path):
    """Test that fix_bdf_encodings converts sequential encodings to Unicode codepoints.

    Issue #1: BDF fonts had sequential encodings (1, 2, 3...) instead of
    Unicode codepoints (48, 49, 50...). This tests the fix.
    """
    # Create a BDF with wrong sequential encodings (1, 2, 3...)
    bdf_file = tmp_path / "test.bdf"
    create_test_bdf_with_wrong_encodings(bdf_file, num_chars=10)

    # Verify it has wrong encodings
    encodings_before = extract_bdf_encodings(bdf_file)
    assert encodings_before == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "Test setup failed"

    # Fix the encodings
    chars = set("0123456789")
    success = fix_bdf_encodings(str(bdf_file), chars)
    assert success, "fix_bdf_encodings should succeed"

    # Verify encodings are now correct (48-57 for digits)
    encodings_after = extract_bdf_encodings(bdf_file)
    expected = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]  # Unicode for '0'-'9'
    assert encodings_after == expected, (
        f"Encodings should be fixed to Unicode codepoints.\n"
        f"Expected: {expected}\n"
        f"Got: {encodings_after}"
    )


def test_fix_bdf_encodings_preserves_correct_encodings(tmp_path):
    """Test that fix_bdf_encodings doesn't change already-correct encodings.

    Issue #1 related: Ensure fix doesn't break fonts that already have correct encodings.
    """
    # Create a BDF with CORRECT encodings (48-57)
    bdf_file = tmp_path / "test.bdf"
    with open(bdf_file, "w") as f:
        f.write("STARTFONT 2.1\n")
        f.write("FONT -test-font\n")
        f.write("SIZE 16 100 100\n")
        f.write("FONTBOUNDINGBOX 10 16 0 0\n")
        f.write("STARTPROPERTIES 1\n")
        f.write("FONT_ASCENT 16\n")
        f.write("ENDPROPERTIES\n")
        f.write("CHARS 3\n")

        # Write with CORRECT encodings
        for i, codepoint in enumerate([48, 49, 50]):  # '0', '1', '2'
            f.write(f"STARTCHAR char{i}\n")
            f.write(f"ENCODING {codepoint}\n")  # Already correct
            f.write("SWIDTH 500 0\n")
            f.write("DWIDTH 10 0\n")
            f.write("BBX 10 16 0 0\n")
            f.write("BITMAP\n")
            f.write("FF\n" * 16)
            f.write("ENDCHAR\n")

        f.write("ENDFONT\n")

    # Apply fix
    chars = set("012")
    success = fix_bdf_encodings(str(bdf_file), chars)
    assert success

    # Verify encodings unchanged
    encodings = extract_bdf_encodings(bdf_file)
    assert encodings == [48, 49, 50], "Correct encodings should be preserved"


def test_fix_bdf_encodings_handles_various_characters(tmp_path):
    """Test fix_bdf_encodings with different character types (letters, symbols).

    Issue #1 related: Verify fix works for non-digit characters too.
    """
    bdf_file = tmp_path / "test.bdf"
    create_test_bdf_with_wrong_encodings(bdf_file, num_chars=5)

    # Use letters instead of digits
    chars = set("ABCDE")
    success = fix_bdf_encodings(str(bdf_file), chars)
    assert success

    # Verify encodings match Unicode for 'A'-'E' (65-69)
    encodings = extract_bdf_encodings(bdf_file)
    expected = [65, 66, 67, 68, 69]  # Unicode for 'A'-'E'
    assert encodings == expected


def test_fix_bdf_encodings_handles_latin1_metadata(tmp_path):
    """Test fix_bdf_encodings with Latin-1 encoded BDF files (Issue #4).

    Issue #4: BDF files from otf2bdf may contain Latin-1 encoded metadata
    (e.g., © or ® symbols in font properties). The fix_bdf_encodings function
    should gracefully handle these by trying UTF-8 first, then falling back
    to Latin-1 encoding.

    This test verifies:
    1. Files with Latin-1 encoding can be read without errors
    2. ENCODING values are still fixed correctly
    3. The file is written back in Latin-1 (preserving original encoding)
    4. Latin-1 metadata characters (©, ®) are preserved
    """
    from .conftest import create_test_bdf_with_latin1_metadata

    bdf_file = tmp_path / "test_latin1.bdf"
    create_test_bdf_with_latin1_metadata(bdf_file, num_chars=3)

    # Verify file was created with Latin-1 encoding
    # Try to read as UTF-8 - should fail
    try:
        with open(bdf_file, encoding="utf-8") as f:
            f.read()
        pytest.fail("File should not be readable as UTF-8 (contains Latin-1 bytes)")
    except UnicodeDecodeError:
        pass  # Expected - file contains Latin-1 bytes

    # Now test that fix_bdf_encodings handles it correctly
    chars = set("ABC")
    success = fix_bdf_encodings(str(bdf_file), chars)
    assert success, "fix_bdf_encodings should handle Latin-1 files"

    # Verify encodings were fixed (should be 65, 66, 67 for A, B, C)
    encodings = extract_bdf_encodings(bdf_file)
    expected = [65, 66, 67]  # Unicode for 'A', 'B', 'C'
    assert encodings == expected, (
        f"Encodings should be fixed even for Latin-1 files.\n"
        f"Expected: {expected}\n"
        f"Got: {encodings}"
    )

    # Verify Latin-1 metadata is preserved (file should still be Latin-1)
    with open(bdf_file, encoding="latin-1") as f:
        content = f.read()
        # Check that © and ® symbols are still present
        assert "\xa9" in content, "Copyright symbol (©) should be preserved"
        assert "\xae" in content, "Registered trademark (®) should be preserved"


# =============================================================================
# Regression Tests: Document Original Bug
# =============================================================================
# Originally from Issue #1 - documents the bug that was fixed


def test_issue_1_regression_convert_to_bdf_produces_sequential_encodings(tmp_path):
    """REGRESSION TEST: Document the original Issue #1 bug.

    This test verifies that convert_to_bdf() alone (without fix_bdf_encodings)
    produces BDF files with sequential encodings (1, 2, 3...) instead of
    Unicode codepoints (48, 49, 50...).

    This documents the bug and ensures we don't lose the fix in the future.
    """
    source_font = "/System/Library/Fonts/Helvetica.ttc"
    if not os.path.exists(source_font):
        pytest.skip("System font not available")

    chars = set("0123456789")
    subset_ttf = tmp_path / "subset.ttf"

    # Create subset font
    success, num_glyphs = generate_subset_font(str(source_font), chars, str(subset_ttf))
    assert success, "Font subsetting should succeed"
    assert num_glyphs > 0, "Should have glyphs"

    # Convert to BDF WITHOUT calling fix_bdf_encodings
    bdf_file = tmp_path / "test.bdf"
    success = convert_to_bdf(str(subset_ttf), str(bdf_file), size=16)
    assert success, "BDF conversion should succeed"
    assert bdf_file.exists()

    # Extract encodings
    encodings = extract_bdf_encodings(bdf_file)

    # DOCUMENT THE BUG: Encodings are sequential (1, 2, 3...)
    # NOT the correct Unicode values (48, 49, 50...)
    assert len(encodings) > 0, "Should have encodings"

    # The bug: encodings are sequential starting from 1
    expected_bug = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    expected_correct = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]

    if encodings == expected_correct:
        pytest.fail(
            "This test documents the original bug. If encodings are already "
            "correct without fix_bdf_encodings, the underlying issue may be "
            "fixed in fontTools or otf2bdf. Review whether fix is still needed."
        )

    # Assert the bug exists (sequential encodings)
    assert encodings == expected_bug, (
        f"This test documents Issue #1 bug: convert_to_bdf produces sequential encodings.\n"
        f"Expected (bug): {expected_bug}\n"
        f"Got: {encodings}\n"
        f"Correct would be: {expected_correct}\n"
        f"If this fails, the bug behavior may have changed."
    )


def test_issue_1_regression_old_generated_fonts_have_bug():
    """REGRESSION TEST: Verify that old generated fonts (before fix) have the bug.

    This checks if there are pre-existing generated fonts in output/ that
    demonstrate the original bug. Useful for before/after comparison.

    Note: This test is expected to SKIP if no pre-existing fonts exist,
    or PASS if fonts have been regenerated with the fix.
    """
    from pathlib import Path

    output_dir = Path(__file__).parent.parent / "output" / "digits"
    bdf_file = output_dir / "digits-16pt.bdf"

    if not bdf_file.exists():
        pytest.skip("No pre-existing generated font found (run generation first)")

    # Check what encodings the existing file has
    encodings = extract_bdf_encodings(bdf_file)

    expected_bug = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    expected_fixed = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]

    # This test will fail BEFORE fix is applied, pass AFTER
    # Both outcomes are valid - we're documenting the state
    if encodings == expected_bug:
        pytest.skip(
            f"Pre-existing font has bug (sequential encodings: {encodings}). "
            f"This is expected before fix is applied. Regenerate fonts to test fix."
        )
    elif encodings == expected_fixed:
        # Fix has been applied and fonts regenerated
        pass
    else:
        pytest.fail(
            f"Unexpected encoding pattern in existing font.\n"
            f"Expected either {expected_bug} (bug) or {expected_fixed} (fixed)\n"
            f"Got: {encodings}"
        )


# =============================================================================
# Additional Coverage Tests
# =============================================================================


class TestConvertToPcf:
    """Tests for convert_to_pcf function."""

    def test_convert_to_pcf_success(self, tmp_path):
        """Test successful BDF to PCF conversion."""
        # First create a BDF file
        source_font = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(source_font):
            pytest.skip("System font not available")

        chars = set("ABC")
        subset_ttf = tmp_path / "subset.ttf"

        # Create subset and convert to BDF
        success, _ = generate_subset_font(str(source_font), chars, str(subset_ttf))
        if not success:
            pytest.skip("Subset generation failed")

        bdf_file = tmp_path / "test.bdf"
        success = convert_to_bdf(str(subset_ttf), str(bdf_file), size=16)
        if not success:
            pytest.skip("BDF conversion failed")

        # Now test PCF conversion
        pcf_file = tmp_path / "test.pcf"
        result = convert_to_pcf(str(bdf_file), str(pcf_file))

        assert result is True
        assert pcf_file.exists()
        assert pcf_file.stat().st_size > 0

    def test_convert_to_pcf_with_logger(self, tmp_path):
        """Test PCF conversion with logger."""
        # Create a complete BDF file with all required properties
        bdf_file = tmp_path / "test.bdf"
        with open(bdf_file, "w") as f:
            f.write("STARTFONT 2.1\n")
            f.write("FONT -test-font\n")
            f.write("SIZE 16 100 100\n")
            f.write("FONTBOUNDINGBOX 10 16 0 -2\n")
            f.write("STARTPROPERTIES 2\n")
            f.write("FONT_ASCENT 14\n")
            f.write("FONT_DESCENT 2\n")
            f.write("ENDPROPERTIES\n")
            f.write("CHARS 3\n")
            # Add 3 characters
            for i in range(3):
                f.write(f"STARTCHAR char{i}\n")
                f.write(f"ENCODING {ord('A') + i}\n")
                f.write("SWIDTH 500 0\n")
                f.write("DWIDTH 10 0\n")
                f.write("BBX 10 16 0 -2\n")
                f.write("BITMAP\n")
                f.write("00\n" * 16)
                f.write("ENDCHAR\n")
            f.write("ENDFONT\n")

        pcf_file = tmp_path / "test.pcf"
        logger = GenerationLogger(verbose=True)

        result = convert_to_pcf(str(bdf_file), str(pcf_file), logger)

        assert result is True
        assert pcf_file.exists()

    def test_convert_to_pcf_nonexistent_bdf(self, tmp_path):
        """Test PCF conversion with nonexistent BDF file."""
        bdf_file = tmp_path / "nonexistent.bdf"
        pcf_file = tmp_path / "test.pcf"
        logger = GenerationLogger()

        result = convert_to_pcf(str(bdf_file), str(pcf_file), logger)

        assert result is False
        # Note: PCF file may be created but will be empty/corrupt
        # The important part is that the function returns False

    @mock.patch("subprocess.run")
    def test_convert_to_pcf_command_not_found(self, mock_run, tmp_path):
        """Test PCF conversion when bdftopcf command not found."""
        mock_run.side_effect = FileNotFoundError("bdftopcf not found")

        bdf_file = tmp_path / "test.bdf"
        create_test_bdf_with_wrong_encodings(bdf_file, num_chars=3)

        pcf_file = tmp_path / "test.pcf"
        logger = GenerationLogger()

        result = convert_to_pcf(str(bdf_file), str(pcf_file), logger)

        assert result is False
        assert len(logger.errors) > 0


class TestGenerateSubsetFont:
    """Additional tests for generate_subset_font function."""

    def test_with_verbose_logger(self, tmp_path):
        """Test generate_subset_font with verbose logger."""
        source_font = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(source_font):
            pytest.skip("System font not available")

        chars = set("ABC")
        output = tmp_path / "subset.ttf"
        logger = GenerationLogger(verbose=True, debug=True)

        success, num_glyphs = generate_subset_font(str(source_font), chars, str(output), logger)

        assert success is True
        assert num_glyphs > 0
        assert output.exists()

    def test_with_invalid_font_path(self, tmp_path):
        """Test generate_subset_font with invalid font."""
        chars = set("ABC")
        output = tmp_path / "subset.ttf"
        logger = GenerationLogger()

        success, num_glyphs = generate_subset_font(
            "/nonexistent/font.ttf", chars, str(output), logger
        )

        assert success is False
        assert num_glyphs == 0
        assert len(logger.errors) > 0

    def test_with_few_glyphs_warning(self, tmp_path):
        """Test that logger warns when very few glyphs are produced."""
        source_font = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(source_font):
            pytest.skip("System font not available")

        # Request many unlikely characters
        unlikely_chars = {chr(i) for i in range(0x1F600, 0x1F604)}  # emojis
        output = tmp_path / "subset.ttf"
        logger = GenerationLogger(verbose=True)

        success, num_glyphs = generate_subset_font(
            str(source_font), unlikely_chars, str(output), logger
        )

        # May succeed but produce very few glyphs
        if success and num_glyphs < len(unlikely_chars) * 0.5:
            # Should have warned
            assert len(logger.warnings) > 0


class TestConvertToBdf:
    """Additional tests for convert_to_bdf function."""

    def test_with_verbose_logger(self, tmp_path):
        """Test convert_to_bdf with verbose logger."""
        source_font = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(source_font):
            pytest.skip("System font not available")

        # Use 10 characters to avoid otf2bdf issues with very small subsets
        chars = set("1234567890")
        subset_ttf = tmp_path / "subset.ttf"

        success, _ = generate_subset_font(str(source_font), chars, str(subset_ttf))
        if not success:
            pytest.skip("Subset generation failed")

        bdf_file = tmp_path / "test.bdf"
        logger = GenerationLogger(verbose=True, debug=True)

        result = convert_to_bdf(str(subset_ttf), str(bdf_file), size=16, logger=logger)

        assert result is True
        assert bdf_file.exists()

    def test_with_nonexistent_ttf(self, tmp_path):
        """Test convert_to_bdf with nonexistent TTF file."""
        bdf_file = tmp_path / "test.bdf"
        logger = GenerationLogger()

        result = convert_to_bdf("/nonexistent/font.ttf", str(bdf_file), size=16, logger=logger)

        assert result is False
        assert not bdf_file.exists()

    @mock.patch("subprocess.run")
    def test_otf2bdf_command_not_found(self, mock_run, tmp_path):
        """Test convert_to_bdf when otf2bdf command not found."""
        mock_run.side_effect = FileNotFoundError("otf2bdf not found")

        bdf_file = tmp_path / "test.bdf"
        logger = GenerationLogger()

        result = convert_to_bdf("/some/font.ttf", str(bdf_file), size=16, logger=logger)

        assert result is False
        assert len(logger.errors) > 0


class TestFixBdfEncodings:
    """Additional tests for fix_bdf_encodings error handling."""

    def test_with_verbose_logger(self, tmp_path):
        """Test fix_bdf_encodings with verbose logger."""
        bdf_file = tmp_path / "test.bdf"
        create_test_bdf_with_wrong_encodings(bdf_file, num_chars=5)

        chars = set("01234")
        logger = GenerationLogger(verbose=True)

        result = fix_bdf_encodings(str(bdf_file), chars, logger)

        assert result is True

    def test_with_nonexistent_file(self, tmp_path):
        """Test fix_bdf_encodings with nonexistent file."""
        bdf_file = tmp_path / "nonexistent.bdf"
        chars = set("ABC")
        logger = GenerationLogger()

        result = fix_bdf_encodings(str(bdf_file), chars, logger)

        assert result is False
        assert len(logger.errors) > 0

    def test_with_invalid_bdf_content(self, tmp_path):
        """Test fix_bdf_encodings with invalid BDF content."""
        bdf_file = tmp_path / "invalid.bdf"
        with open(bdf_file, "w") as f:
            f.write("Not a valid BDF file\n")

        chars = set("ABC")
        logger = GenerationLogger()

        result = fix_bdf_encodings(str(bdf_file), chars, logger)

        # Should handle gracefully
        assert result is True  # It will "fix" the file even if malformed
