"""
cp-font-gen: Generate minimal bitmap fonts for CircuitPython devices.
"""

__version__ = "1.0.0"

from .config import collect_characters, load_config
from .generator import generate_font

__all__ = ["generate_font", "load_config", "collect_characters"]
