# Development Guide

Documentation for developers working on cp-font-gen.

## Architecture

### Package Structure

```text
cp-font-gen/
├── pyproject.toml              # Project config & entry point
├── src/cp_font_gen/            # Main package
│   ├── __init__.py             # Public API exports
│   ├── cli.py                  # Click CLI commands
│   ├── checker.py              # Tool validation & version checking
│   ├── config.py               # YAML config loading & char collection
│   ├── converter.py            # Font format conversion (TTF→BDF→PCF)
│   ├── generator.py            # Main generation orchestration
│   └── utils.py                # Unicode & character utilities
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_config.py          # Config loading tests
│   └── test_utils.py           # Utility function tests
├── examples/                   # Example configurations
│   └── config-template.yaml    # Complete config template
└── justfile                    # Command shortcuts (see below)
```

### Module Responsibilities

**cli.py** - Click command definitions

- `check` - Validate required tools
- `generate` - Main font generation
- `extract` - Extract chars from files
- `show` - Display config preview

**generator.py** - Orchestration

- `generate_font()` - Main entry point
- `generate_metadata()` - Create manifest.json
- Coordinates conversion pipeline

**converter.py** - Format conversion

- `generate_subset_font()` - TTF subsetting via pyftsubset
- `convert_to_bdf()` - TTF → BDF via otf2bdf
- `convert_to_pcf()` - BDF → PCF via bdftopcf

**config.py** - Configuration

- `load_config()` - Parse YAML
- `collect_characters()` - Aggregate chars from all sources

**checker.py** - Validation

- `check_command_exists()` - Verify system commands
- `check_python_package()` - Verify Python packages
- `get_tool_requirements()` - List all requirements

**utils.py** - Helpers

- `chars_to_unicode_list()` - Convert chars to U+XXXX format
- `unicode_range_to_chars()` - Parse unicode range strings

## Technology Stack

- **Click 8.0+** - CLI framework
- **PyYAML 6.0+** - Config parsing
- **fonttools 4.0+** - Font subsetting (provides pyftsubset)
- **pytest 7.0+** - Testing framework
- **pytest-cov 4.0+** - Coverage reporting
- **uv** - Package management and virtual environments

### External Tools

- **otf2bdf** - TTF to BDF conversion
- **bdftopcf** - BDF to PCF conversion
- **pyftsubset** - Font subsetting (from fonttools)

## Setup for Development

### 1. Clone and Install

```bash
git clone https://github.com/graybear-io/cp-font-gen.git
cd cp-font-gen
uv sync  # Creates .venv, installs deps + package in editable mode
```

### 2. Verify Installation

```bash
just check       # Check external tools
just test        # Run tests
```

### 3. Activate Environment (optional)

```bash
source .venv/bin/activate
cp-font-gen --help
```

Or use `uv run` for everything:

```bash
uv run cp-font-gen --help
uv run pytest
```

## Using the Justfile

The project includes a `justfile` with common development commands. Run `just` to see all available commands:

```bash
just  # Show all commands
```

### Common Just Commands

**Setup & Verification:**

```bash
just sync                  # Sync dependencies (run after git pull)
just check                 # Verify required tools installed
just check-verbose         # Show tool versions
```

**Development:**

```bash
just test                  # Run tests
just test-cov              # Run tests with coverage
just test-watch            # Run tests in watch mode
```

**Code Quality:**

```bash
just fmt                   # Format code with ruff
just fmt-check             # Check formatting (CI-friendly)
just lint                  # Lint code with ruff
just lint-fix              # Lint and auto-fix issues
just typecheck             # Type check with mypy
just check-all             # Run all checks (lint + typecheck + test)
just pre-commit            # Full workflow (format + lint-fix + test)
```

**Font Generation:**

```bash
just generate              # Generate fonts (uses minimal example)
just generate examples/emoji/config.yaml  # Generate specific example
just dry-run               # Preview what would be generated
just show                  # Show characters from config
```

**Output Management:**

```bash
just list-output           # List generated font files
just show-manifest digits  # View manifest for font family
just clean                 # Remove generated fonts
just clean-all             # Remove fonts, cache, and venv
```

**Utilities:**

```bash
just extract myfile.txt    # Extract unique characters from file
just help                  # Show cp-font-gen CLI help
```

### Justfile vs Direct Commands

The justfile wraps `uv run` commands for convenience:

| Justfile | Direct Command |
|----------|----------------|
| `just test` | `uv run pytest` |
| `just generate` | `uv run cp-font-gen generate --config examples/minimal/config.yaml` |
| `just check` | `uv run cp-font-gen check` |

Use whichever you prefer - they're equivalent.

## Code Quality Tools

The project uses modern Python tooling for code quality:

### Ruff - Formatting & Linting

**Ruff** is an extremely fast Python linter and formatter that replaces multiple tools:
- Replaces: black, isort, flake8, pylint, pyupgrade, and more
- Speed: 10-100x faster than traditional tools
- Configuration: See `[tool.ruff]` in `pyproject.toml`

**Usage:**
```bash
just fmt                   # Auto-format all code
just fmt-check             # Check if code is formatted (CI)
just lint                  # Check for linting issues
just lint-fix              # Auto-fix linting issues
```

**What it checks:**
- Code style (PEP 8)
- Import sorting
- Unused imports
- Type annotation modernization (e.g., `List` → `list`)
- Common bugs and anti-patterns
- Code simplification opportunities

### Mypy - Type Checking

**Mypy** performs static type analysis:
- Catches type errors before runtime
- Improves code documentation
- Configuration: See `[tool.mypy]` in `pyproject.toml`

**Usage:**
```bash
just typecheck             # Run type checking
```

**Current settings:**
- Permissive mode (can tighten over time)
- Checks type hints where present
- Ignores missing imports

### Pre-commit Hooks (Optional)

**Pre-commit** can run checks automatically before commits:

**Setup:**
```bash
uv run pre-commit install  # One-time setup
```

**Manual run:**
```bash
just pre-commit            # Run full workflow manually
```

### Recommended Workflow

**During development:**
```bash
# Make changes
just fmt                   # Format code
just lint-fix              # Fix auto-fixable issues
just test                  # Run tests
```

**Before committing:**
```bash
just pre-commit            # Format + lint + test
# or
just check-all             # Lint + typecheck + test (stricter)
```

**In CI/CD:**
```bash
just fmt-check             # Fail if not formatted
just lint                  # Fail on linting issues
just typecheck             # Fail on type errors
just test-cov              # Run tests with coverage
```

## Running Tests

### Basic Testing

```bash
# Run all tests
just test

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_utils.py

# Run specific test
uv run pytest tests/test_utils.py::test_chars_to_unicode_list
```

### Coverage

```bash
# Run with coverage
just test-cov

# Generate HTML coverage report
uv run pytest --cov=cp_font_gen --cov-report=html
open htmlcov/index.html
```

### Watch Mode

```bash
just test-watch  # Re-run on file changes
```

## Writing Tests

Tests use pytest and are located in `tests/`.

### Example Test

```python
# tests/test_my_feature.py
import pytest
from cp_font_gen.utils import my_function

def test_basic_functionality():
    """Test basic use case."""
    result = my_function('input')
    assert result == 'expected'

def test_edge_case():
    """Test edge case handling."""
    with pytest.raises(ValueError):
        my_function(None)

def test_with_fixture(tmp_path):
    """Test using pytest fixture."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    # ... test using file
```

### Available Fixtures

- `tmp_path` - Temporary directory for test files
- `capsys` - Capture stdout/stderr
- `monkeypatch` - Mock functions/environment

## Code Style

### Conventions

- **PEP 8** style guide
- **Type hints** for function signatures
- **Docstrings** for public functions
- **Clear variable names** over brevity

### Example

```python
def convert_to_bdf(ttf_path: str, bdf_path: str, size: int) -> bool:
    """Convert TTF to BDF format using otf2bdf.

    Args:
        ttf_path: Path to TTF file
        bdf_path: Path for output BDF file
        size: Font size in points

    Returns:
        True if successful, False otherwise
    """
    # Implementation
```

## Adding Features

### 1. New CLI Command

Edit `src/cp_font_gen/cli.py`:

```python
@cli.command()
@click.option('--option', help='Description')
def mycommand(option):
    """Command description."""
    # Implementation
```

Add to justfile:

```just
# My new command
mycommand OPTION:
    uv run cp-font-gen mycommand --option {{OPTION}}
```

### 2. New Utility Function

Add to appropriate module (`utils.py`, `config.py`, etc.):

```python
def my_utility(input: str) -> str:
    """Do something useful.

    Args:
        input: Input string

    Returns:
        Processed string
    """
    return input.upper()
```

Write tests in `tests/test_module.py`:

```python
def test_my_utility():
    assert my_utility('hello') == 'HELLO'
```

### 3. New Configuration Option

1. Add to `config.yaml` example
2. Update `config.py` to parse it
3. Use in relevant module
4. Document in README.md
5. Add tests

## Using as a Library

The package can be imported and used programmatically:

```python
from cp_font_gen import generate_font, load_config, collect_characters
from pathlib import Path

# Load and process config
config = load_config('my_config.yaml')
chars = collect_characters(config)

print(f"Generating fonts with {len(chars)} characters")

# Generate fonts
output_dir = Path('output')
output_dir.mkdir(exist_ok=True)
generated_files = generate_font(config, chars, output_dir)

print(f"Generated {len(generated_files)} files:")
for file in generated_files:
    print(f"  - {file}")
```

### Public API

Exported from `__init__.py`:

- `generate_font(config, chars, output_dir)` - Main generation
- `load_config(path)` - Load YAML config
- `collect_characters(config)` - Get character set

### Internal Modules

Can be imported directly if needed:

```python
from cp_font_gen.converter import convert_to_bdf
from cp_font_gen.checker import check_command_exists
from cp_font_gen.utils import chars_to_unicode_list
```

## Debugging

### Enable Verbose Logging

Add to your code:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Debug CLI Commands

```bash
# Add --help to any command
uv run cp-font-gen generate --help

# Use Python debugger
uv run python -m pdb -m cp_font_gen.cli generate
```

### Test Individual Modules

```python
# In Python REPL
from cp_font_gen.config import collect_characters

config = {'characters': {'inline': 'ABC'}}
chars = collect_characters(config)
print(chars)  # {'A', 'B', 'C'}
```

## Release Process

1. Update version in `src/cp_font_gen/__init__.py`
2. Update version in `pyproject.toml`
3. Run full test suite: `just test-cov`
4. Update CHANGELOG.md
5. Commit changes
6. Tag release: `git tag v1.0.1`
7. Push: `git push && git push --tags`

## Common Tasks

### Add a New Test

```bash
# Create test file
touch tests/test_new_feature.py

# Write tests
# Run them
just test
```

### Check Test Coverage

```bash
just test-cov
# Look for uncovered lines in output
```

### Update Dependencies

```bash
# Edit pyproject.toml dependencies
# Then sync
uv sync
```

### Clean Everything

```bash
just clean-all  # Remove output, cache, venv
uv sync         # Reinstall
```

## Font Generation Pipeline

Understanding the full pipeline:

```text
1. User Config (config.yaml)
   ↓
2. collect_characters() → Set of chars
   ↓
3. For each size:
   ↓
   a. generate_subset_font()
      Source TTF → Subset TTF (only needed glyphs)
      [Uses: pyftsubset]
   ↓
   b. convert_to_bdf()
      Subset TTF → BDF (bitmap, ASCII)
      [Uses: otf2bdf]
   ↓
   c. convert_to_pcf()
      BDF → PCF (bitmap, binary)
      [Uses: bdftopcf]
   ↓
4. generate_metadata()
   Create manifest.json
```

## Performance Considerations

- Font subsetting is the slowest step (~1-2s per font)
- BDF conversion is fast (<0.5s)
- PCF conversion is very fast (<0.1s)
- Batch multiple sizes for efficiency

## Troubleshooting Development Issues

### Import Errors

```bash
# Package not installed
uv sync

# Old version cached
just clean-all
uv sync
```

### Tests Failing

```bash
# Run with verbose output
uv run pytest -v

# Run single test
uv run pytest tests/test_utils.py::test_name -v

# Check for print statements
uv run pytest -s
```

### CLI Not Working

```bash
# Verify installation
uv run cp-font-gen --version

# Check entry point
grep "cp-font-gen" pyproject.toml

# Reinstall
uv sync --reinstall
```

## Contributing Guidelines

1. **Fork** the repository
2. **Create a branch** for your feature
3. **Write tests** for new functionality
4. **Ensure tests pass**: `just test`
5. **Update documentation** as needed
6. **Submit pull request** with clear description

## Resources

### Python Tools

- [Click Documentation](https://click.palletsprojects.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [uv Documentation](https://docs.astral.sh/uv/)

### Font Formats

- [BDF Specification](https://www.adobe.com/content/dam/acom/en/devnet/font/pdfs/5005.BDF_Spec.pdf)
- [PCF Format](https://fontforge.org/docs/techref/pcf-format.html)
- [fonttools Documentation](https://fonttools.readthedocs.io/)

### CircuitPython

- [CircuitPython Docs](https://docs.circuitpython.org/)
- [Adafruit Learn](https://learn.adafruit.com/)
