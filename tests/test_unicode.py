"""Tests for Unicode and multi-byte character handling."""

import tempfile
from pathlib import Path

from cp_font_gen.config import collect_characters


def test_multibyte_unicode_from_file():
    """Test that multi-byte unicode characters are read correctly from files."""
    # Create temp file with various unicode characters
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".txt") as f:
        # Write various unicode character types:
        # - ASCII (single byte)
        # - Accented Latin (2 bytes)
        # - Greek (2-3 bytes)
        # - Emoji (4 bytes)
        # - CJK (3-4 bytes)
        test_chars = "abc123éñü中文😀🌟"
        f.write(test_chars)
        temp_path = f.name

    try:
        config = {"characters": {"file": temp_path}}

        chars = collect_characters(config)

        # Verify all characters were read correctly
        assert "a" in chars  # ASCII
        assert "é" in chars  # Accented
        assert "ñ" in chars  # Accented
        assert "中" in chars  # CJK
        assert "文" in chars  # CJK
        assert "😀" in chars  # Emoji
        assert "🌟" in chars  # Emoji

        # Verify character count is correct (not byte count)
        assert len(chars) == len(test_chars)

    finally:
        Path(temp_path).unlink()


def test_unicode_ranges_with_emoji():
    """Test that unicode ranges work with multi-byte characters."""
    config = {
        "characters": {
            "unicode_ranges": [
                "U+1F600",  # 😀 Grinning Face
                "U+1F31F",  # 🌟 Glowing Star
            ]
        }
    }

    chars = collect_characters(config)

    assert "😀" in chars
    assert "🌟" in chars
    assert len(chars) == 2


def test_mixed_unicode_sources():
    """Test combining inline, file, and unicode ranges with multi-byte chars."""
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".txt") as f:
        f.write("日本語")
        temp_path = f.name

    try:
        config = {
            "characters": {
                "inline": "中文",
                "file": temp_path,
                "unicode_ranges": ["U+1F600"],  # 😀
            }
        }

        chars = collect_characters(config)

        # From inline
        assert "中" in chars
        assert "文" in chars

        # From file
        assert "日" in chars
        assert "本" in chars
        assert "語" in chars

        # From unicode range
        assert "😀" in chars

        assert len(chars) == 6

    finally:
        Path(temp_path).unlink()
