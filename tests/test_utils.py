"""Tests for utility functions."""

from cp_font_gen.utils import chars_to_unicode_list, unicode_range_to_chars


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
