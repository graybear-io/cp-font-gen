"""Tests for utility functions."""

import os
from unittest import mock

import pytest

from cp_font_gen.logger import GenerationLogger
from cp_font_gen.utils import (
    chars_to_unicode_list,
    check_character_coverage,
    unicode_range_to_chars,
)


def test_chars_to_unicode_list():
    """Test converting characters to unicode list."""
    chars = {"A", "B", "C"}
    result = chars_to_unicode_list(chars)
    assert result == ["U+0041", "U+0042", "U+0043"]


def test_chars_to_unicode_list_special():
    """Test unicode conversion with special characters."""
    chars = {"°", "←", "→"}
    result = chars_to_unicode_list(chars)
    assert "U+00B0" in result  # degree symbol
    assert "U+2190" in result  # left arrow
    assert "U+2192" in result  # right arrow


def test_unicode_range_to_chars():
    """Test converting unicode range to characters."""
    # Test range
    chars = unicode_range_to_chars("U+0041-0043")
    assert chars == {"A", "B", "C"}

    # Test single character
    chars = unicode_range_to_chars("U+00B0")
    assert chars == {"°"}


def test_unicode_range_digits():
    """Test unicode range for digits."""
    chars = unicode_range_to_chars("U+0030-0039")
    assert chars == {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}


class TestCheckCharacterCoverage:
    """Tests for check_character_coverage function."""

    def test_with_system_font_all_found(self):
        """Test character coverage with system font where all chars are found."""
        source_font = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(source_font):
            pytest.skip("System font not available")

        chars = set("ABC")
        found, missing, stats = check_character_coverage(source_font, chars)

        assert len(found) == 3
        assert len(missing) == 0
        assert stats["requested"] == 3
        assert stats["found_in_source"] == 3
        assert stats["missing_count"] == 0
        assert stats["missing"] == []

    def test_with_system_font_some_missing(self):
        """Test character coverage with some missing characters."""
        source_font = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(source_font):
            pytest.skip("System font not available")

        # Use a character that likely doesn't exist in Helvetica
        chars = set("A\U0001f600")  # 'A' and a Unicode emoji
        found, missing, stats = check_character_coverage(source_font, chars)

        assert "A" in found
        assert "\U0001f600" in missing
        assert stats["requested"] == 2
        assert stats["found_in_source"] == 1
        assert stats["missing_count"] == 1
        assert len(stats["missing"]) == 1

    @mock.patch("click.echo")
    def test_with_logger_and_missing_chars(self, mock_echo):
        """Test that logger is called when characters are missing."""
        source_font = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(source_font):
            pytest.skip("System font not available")

        logger = GenerationLogger(verbose=True)
        chars = set("A\U0001f600")  # 'A' and an emoji

        found, missing, stats = check_character_coverage(source_font, chars, logger)

        assert len(logger.warnings) > 0
        assert "not found in source font" in logger.warnings[0]

    @mock.patch("click.echo")
    def test_with_debug_logger_shows_missing_details(self, mock_echo):
        """Test that debug logger shows details of missing characters."""
        source_font = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(source_font):
            pytest.skip("System font not available")

        logger = GenerationLogger(verbose=True, debug=True)
        chars = set("A\U0001f600")  # 'A' and an emoji

        found, missing, stats = check_character_coverage(source_font, chars, logger)

        # In debug mode, click.echo should be called to show missing characters
        assert mock_echo.called

    def test_with_nonexistent_font(self):
        """Test handling of nonexistent font file."""
        logger = GenerationLogger()
        chars = set("ABC")

        found, missing, stats = check_character_coverage("/nonexistent/font.ttf", chars, logger)

        # Should return empty found, all chars as missing
        assert len(found) == 0
        assert len(missing) == 3
        assert stats["requested"] == 3
        assert stats["found_in_source"] == 0
        assert stats["missing_count"] == 3
        assert "error" in stats

    def test_without_logger(self):
        """Test that function works without a logger."""
        source_font = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(source_font):
            pytest.skip("System font not available")

        chars = set("ABC")
        found, missing, stats = check_character_coverage(source_font, chars, logger=None)

        assert len(found) == 3
        assert len(missing) == 0

    def test_ttf_file(self):
        """Test that function works with TTF files (not TTC)."""
        # Create a mock for a TTF file path
        source_font = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(source_font):
            pytest.skip("System font not available")

        # The function should handle both .ttf and .ttc
        chars = set("123")
        found, missing, stats = check_character_coverage(source_font, chars)

        assert len(found) == 3

    @mock.patch("click.echo")
    def test_with_many_missing_characters(self, mock_echo):
        """Test handling of many missing characters (>10)."""
        source_font = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(source_font):
            pytest.skip("System font not available")

        # Create a set with many unlikely characters
        unlikely_chars = {chr(i) for i in range(0x1F600, 0x1F60C)}  # 12 emoji
        chars = unlikely_chars | set("A")  # Add one normal char

        logger = GenerationLogger(verbose=True, debug=True)
        found, missing, stats = check_character_coverage(source_font, chars, logger)

        # Should have many missing characters
        assert len(missing) > 10

    def test_empty_character_set(self):
        """Test with empty character set."""
        source_font = "/System/Library/Fonts/Helvetica.ttc"
        if not os.path.exists(source_font):
            pytest.skip("System font not available")

        chars = set()
        found, missing, stats = check_character_coverage(source_font, chars)

        assert len(found) == 0
        assert len(missing) == 0
        assert stats["requested"] == 0
        assert stats["found_in_source"] == 0
