"""Tests for converter.py - Font conversion functions.

Includes unit tests for fix_bdf_encodings() and regression tests
for the BDF encoding bug (Issue #1).
"""

import os

import pytest

from cp_font_gen.converter import convert_to_bdf, fix_bdf_encodings, generate_subset_font

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
