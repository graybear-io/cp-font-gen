"""Shared test fixtures and helpers for cp-font-gen tests."""


# =============================================================================
# BDF Test Helpers (from Issue #1)
# =============================================================================


def extract_bdf_encodings(bdf_path):
    """Extract ENCODING values from a BDF file.

    Originally from Issue #1 test suite - helper for verifying BDF character encodings.

    Note: Uses UTF-8 first, falls back to Latin-1 (Issue #4 - BDF spec allows both)
    """
    encodings = []
    # Try UTF-8 first, fallback to Latin-1 (same as fix_bdf_encodings)
    try:
        with open(bdf_path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("ENCODING "):
                    encoding = int(line.split()[1])
                    encodings.append(encoding)
    except UnicodeDecodeError:
        with open(bdf_path, encoding="latin-1") as f:
            for line in f:
                if line.startswith("ENCODING "):
                    encoding = int(line.split()[1])
                    encodings.append(encoding)
    return encodings


def create_test_bdf_with_wrong_encodings(bdf_path, num_chars=10, encoding="utf-8"):
    """Create a minimal BDF file with sequential encodings (1, 2, 3...) for testing.

    Originally from Issue #1 test suite - creates a BDF with incorrect encodings
    to test the fix_bdf_encodings() function.

    Args:
        bdf_path: Path to write BDF file
        num_chars: Number of characters to include
        encoding: Text encoding to use (utf-8 or latin-1)
    """
    with open(bdf_path, "w", encoding=encoding) as f:
        f.write("STARTFONT 2.1\n")
        f.write("FONT -test-font\n")
        f.write("SIZE 16 100 100\n")
        f.write("FONTBOUNDINGBOX 10 16 0 0\n")
        f.write("STARTPROPERTIES 1\n")
        f.write("FONT_ASCENT 16\n")
        f.write("ENDPROPERTIES\n")
        f.write(f"CHARS {num_chars}\n")

        # Write characters with WRONG sequential encodings (1, 2, 3...)
        for i in range(num_chars):
            f.write(f"STARTCHAR char{i}\n")
            f.write(f"ENCODING {i + 1}\n")  # Wrong: should be 48-57 for digits
            f.write("SWIDTH 500 0\n")
            f.write("DWIDTH 10 0\n")
            f.write("BBX 10 16 0 0\n")
            f.write("BITMAP\n")
            f.write("FF\n" * 16)  # Dummy bitmap
            f.write("ENDCHAR\n")

        f.write("ENDFONT\n")


def create_test_bdf_with_latin1_metadata(bdf_path, num_chars=3):
    """Create a BDF file with Latin-1 encoded metadata (Issue #4).

    Simulates what otf2bdf outputs when processing fonts with extended
    Latin characters (©, ®, etc.) in font metadata. This tests the
    UTF-8 → Latin-1 fallback in fix_bdf_encodings().

    Args:
        bdf_path: Path to write BDF file
        num_chars: Number of characters to include
    """
    with open(bdf_path, "w", encoding="latin-1") as f:
        f.write("STARTFONT 2.1\n")
        # Include Latin-1 characters in metadata (byte 0xA9 = ©, 0xAE = ®)
        f.write("COMMENT Copyright \xa9 2025 Test Font\n")  # © symbol
        f.write("FONT -TestFont\xae-Regular\n")  # ® symbol
        f.write("SIZE 16 100 100\n")
        f.write("FONTBOUNDINGBOX 10 16 0 0\n")
        f.write("STARTPROPERTIES 2\n")
        f.write("FONT_ASCENT 16\n")
        f.write("COPYRIGHT \"Test Font \xa9 2025\"\n")  # © in property
        f.write("ENDPROPERTIES\n")
        f.write(f"CHARS {num_chars}\n")

        # Characters with wrong sequential encodings
        for i in range(num_chars):
            f.write(f"STARTCHAR char{i}\n")
            f.write(f"ENCODING {i + 1}\n")
            f.write("SWIDTH 500 0\n")
            f.write("DWIDTH 10 0\n")
            f.write("BBX 10 16 0 0\n")
            f.write("BITMAP\n")
            f.write("FF\n" * 16)
            f.write("ENDCHAR\n")

        f.write("ENDFONT\n")
