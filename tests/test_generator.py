"""Tests for generator.py - Font generation orchestration.

Includes integration tests for the full font generation workflow,
including tests for Issue #1 fix integration.
"""

import os

import pytest

from cp_font_gen.generator import generate_font

from .conftest import extract_bdf_encodings


# =============================================================================
# Integration Tests: Full Workflow
# =============================================================================


def test_generate_font_produces_correct_encodings(tmp_path):
    """Test that generate_font() workflow produces BDF with correct encodings.

    Issue #1 Integration Test: Verifies the fix is properly integrated into
    the full generation workflow.
    """
    source_font = "/System/Library/Fonts/Helvetica.ttc"
    if not os.path.exists(source_font):
        pytest.skip("System font not available")

    # Config for generating digits font
    config = {
        "source_font": source_font,
        "sizes": [16],
        "output": {
            "formats": ["bdf"],
            "font_family": "test-digits",
        },
    }

    chars = set("0123456789")

    # Generate font using full workflow
    generated_files = generate_font(config, chars, tmp_path)

    # Verify file was created
    assert len(generated_files) > 0, "Should generate at least one file"

    # Check the BDF file
    bdf_file = tmp_path / "test-digits" / "test-digits-16pt.bdf"
    assert bdf_file.exists(), f"BDF file should exist: {bdf_file}"

    # Verify encodings are CORRECT (48-57 for '0'-'9')
    encodings = extract_bdf_encodings(bdf_file)
    expected = list(range(48, 58))  # 48-57 for '0'-'9'

    assert encodings == expected, (
        f"Generated BDF should have correct Unicode encodings (Issue #1 fix).\n"
        f"Expected: {expected} (Unicode for '0'-'9')\n"
        f"Got: {encodings}\n"
        f"If this fails, the fix in generator.py may not be working."
    )


def test_generate_font_with_letters_has_correct_encodings(tmp_path):
    """Test that fix works for non-digit characters too.

    Issue #1 Integration Test: Verify encoding fix works for letters,
    not just digits.
    """
    source_font = "/System/Library/Fonts/Helvetica.ttc"
    if not os.path.exists(source_font):
        pytest.skip("System font not available")

    config = {
        "source_font": source_font,
        "sizes": [16],
        "output": {
            "formats": ["bdf"],
            "font_family": "test-abc",
        },
    }

    chars = set("ABC")
    generated_files = generate_font(config, chars, tmp_path)

    assert len(generated_files) > 0

    bdf_file = tmp_path / "test-abc" / "test-abc-16pt.bdf"
    assert bdf_file.exists()

    encodings = extract_bdf_encodings(bdf_file)
    expected = [65, 66, 67]  # Unicode for 'A', 'B', 'C'
    assert encodings == expected
