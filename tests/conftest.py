"""Shared test fixtures and helpers for cp-font-gen tests."""

import pytest


# =============================================================================
# BDF Test Helpers (from Issue #1)
# =============================================================================

def extract_bdf_encodings(bdf_path):
    """Extract ENCODING values from a BDF file.

    Originally from Issue #1 test suite - helper for verifying BDF character encodings.
    """
    encodings = []
    with open(bdf_path, "r") as f:
        for line in f:
            if line.startswith("ENCODING "):
                encoding = int(line.split()[1])
                encodings.append(encoding)
    return encodings


def create_test_bdf_with_wrong_encodings(bdf_path, num_chars=10):
    """Create a minimal BDF file with sequential encodings (1, 2, 3...) for testing.

    Originally from Issue #1 test suite - creates a BDF with incorrect encodings
    to test the fix_bdf_encodings() function.
    """
    with open(bdf_path, "w") as f:
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
