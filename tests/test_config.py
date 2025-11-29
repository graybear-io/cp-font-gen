"""Tests for configuration loading."""

from cp_font_gen.config import collect_characters


def test_collect_inline_characters():
    """Test collecting inline characters from config."""
    config = {"characters": {"inline": "0123456789"}}
    chars = collect_characters(config)
    assert len(chars) == 10
    assert "0" in chars
    assert "9" in chars


def test_collect_with_deduplication():
    """Test that duplicate characters are removed."""
    config = {"characters": {"inline": "00011122"}, "deduplicate_chars": True}
    chars = collect_characters(config)
    assert len(chars) == 3
    assert chars == {"0", "1", "2"}


def test_collect_strip_whitespace():
    """Test stripping whitespace when configured."""
    config = {"characters": {"inline": "A B C   "}, "strip_whitespace": True}
    chars = collect_characters(config)
    assert " " not in chars
    assert len(chars) == 3
    assert chars == {"A", "B", "C"}


def test_collect_from_file(tmp_path):
    """Test loading characters from a file."""
    # Create temp file with characters
    char_file = tmp_path / "chars.txt"
    char_file.write_text("ABC")

    config = {"characters": {"file": str(char_file)}}
    chars = collect_characters(config)
    assert chars == {"A", "B", "C"}
