"""Tests for generator.py - Font generation orchestration.

Includes integration tests for the full font generation workflow,
including tests for Issue #1 fix integration.
"""

import json
import os

import pytest

from cp_font_gen.generator import generate_font, generate_metadata
from cp_font_gen.logger import GenerationLogger

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

    Note: Uses 10 characters to avoid otf2bdf issues with very small subsets.
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

    # Use 10 characters to avoid otf2bdf issues with very small subsets
    chars = set("ABCDEFGHIJ")
    generated_files = generate_font(config, chars, tmp_path)

    assert len(generated_files) > 0, "Should generate at least one file"

    bdf_file = tmp_path / "test-abc" / "test-abc-16pt.bdf"
    assert bdf_file.exists(), f"BDF file should exist: {bdf_file}"

    encodings = extract_bdf_encodings(bdf_file)
    expected = [65, 66, 67, 68, 69, 70, 71, 72, 73, 74]  # Unicode for 'A'-'J'
    assert encodings == expected, (
        f"Generated BDF should have correct Unicode encodings for letters.\n"
        f"Expected: {expected} (Unicode for 'A'-'J')\n"
        f"Got: {encodings}"
    )


# =============================================================================
# Additional Tests for Coverage
# =============================================================================


class TestGenerateMetadata:
    """Tests for generate_metadata function."""

    def test_basic_metadata(self):
        """Test basic metadata generation."""
        config = {
            "source_font": "/path/to/font.ttf",
            "sizes": [16, 24],
            "output": {"formats": ["bdf", "pcf"], "font_family": "test-font"},
        }
        chars = set("ABC")
        generated_files = ["test-font-16pt.bdf", "test-font-24pt.bdf"]
        output_dir = "/tmp/output"

        metadata = generate_metadata(config, chars, generated_files, output_dir)

        assert metadata["version"] == "1.0"
        assert metadata["source_font"] == "/path/to/font.ttf"
        assert metadata["character_count"] == 3
        assert metadata["characters"] == "ABC"
        assert len(metadata["unicode_ranges"]) == 3
        assert metadata["sizes"] == [16, 24]
        assert metadata["output_directory"] == "/tmp/output"
        assert metadata["generated_files"] == generated_files
        assert metadata["formats"] == ["bdf", "pcf"]

    def test_metadata_with_debug_info(self):
        """Test metadata generation with debug info."""
        config = {
            "source_font": "/path/to/font.ttf",
            "sizes": [16],
            "output": {"formats": ["bdf"], "font_family": "test"},
        }
        chars = set("123")
        generated_files = ["test-16pt.bdf"]
        output_dir = "/tmp"
        debug_info = {"tool_version": "1.0.0", "warnings": []}

        metadata = generate_metadata(config, chars, generated_files, output_dir, debug_info)

        assert "debug_info" in metadata
        assert metadata["debug_info"] == debug_info


class TestGenerateFontWithLogger:
    """Tests for generate_font with logger."""

    def test_with_verbose_logger(self, tmp_path):
        """Test generate_font with verbose logger."""
        source_font = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(source_font):
            pytest.skip("System font not available")

        config = {
            "source_font": source_font,
            "sizes": [16],
            "output": {"formats": ["bdf"], "font_family": "test-verbose", "metadata": True},
        }

        chars = set("ABCDEFGHIJ")
        logger = GenerationLogger(verbose=True)

        generated_files = generate_font(config, chars, tmp_path, logger)

        assert len(generated_files) > 0

        # Check that manifest was created
        manifest_file = tmp_path / "test-verbose" / "test-verbose-manifest.json"
        assert manifest_file.exists()

        with open(manifest_file) as f:
            manifest = json.load(f)
            assert manifest["character_count"] == 10

    def test_with_debug_logger(self, tmp_path):
        """Test generate_font with debug logger."""
        source_font = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(source_font):
            pytest.skip("System font not available")

        config = {
            "source_font": source_font,
            "sizes": [16],
            "output": {"formats": ["bdf"], "font_family": "test-debug", "metadata": True},
        }

        chars = set("1234567890")
        logger = GenerationLogger(verbose=True, debug=True)

        generated_files = generate_font(config, chars, tmp_path, logger)

        assert len(generated_files) > 0

        # Check that manifest includes debug info
        manifest_file = tmp_path / "test-debug" / "test-debug-manifest.json"
        with open(manifest_file) as f:
            manifest = json.load(f)
            assert "debug_info" in manifest
            assert "character_coverage" in manifest["debug_info"]

    def test_with_pcf_format(self, tmp_path):
        """Test generate_font with PCF format."""
        source_font = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(source_font):
            pytest.skip("System font not available")

        config = {
            "source_font": source_font,
            "sizes": [16],
            "output": {"formats": ["pcf"], "font_family": "test-pcf"},
        }

        chars = set("ABCDEFGHIJ")

        generated_files = generate_font(config, chars, tmp_path)

        assert len(generated_files) > 0
        assert any("pcf" in f for f in generated_files)

    def test_with_both_formats(self, tmp_path):
        """Test generate_font with both BDF and PCF formats."""
        source_font = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(source_font):
            pytest.skip("System font not available")

        config = {
            "source_font": source_font,
            "sizes": [16],
            "output": {"formats": ["bdf", "pcf"], "font_family": "test-both"},
        }

        chars = set("ABCDEFGHIJ")

        generated_files = generate_font(config, chars, tmp_path)

        assert len(generated_files) == 2  # One BDF and one PCF
        assert any("bdf" in f for f in generated_files)
        assert any("pcf" in f for f in generated_files)

    def test_without_metadata(self, tmp_path):
        """Test generate_font without metadata."""
        source_font = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(source_font):
            pytest.skip("System font not available")

        config = {
            "source_font": source_font,
            "sizes": [16],
            "output": {"formats": ["bdf"], "font_family": "test-no-meta", "metadata": False},
        }

        chars = set("ABCDEFGHIJ")

        generated_files = generate_font(config, chars, tmp_path)

        assert len(generated_files) > 0

        # Check that manifest was NOT created
        manifest_file = tmp_path / "test-no-meta" / "test-no-meta-manifest.json"
        assert not manifest_file.exists()
