# cp-font-gen: CircuitPython Font Generator
#
# Uses uv to automatically manage Python environment

# Show available commands
default:
    @just --list

# Check if required tools are installed
check:
    uv run cp-font-gen check

# Check with verbose output (show versions)
check-verbose:
    uv run cp-font-gen check --verbose

# Generate fonts from config file (defaults to minimal example)
generate CONFIG="examples/minimal/config.yaml":
    uv run cp-font-gen generate --config {{CONFIG}}

# Dry run - show what would be generated
dry-run CONFIG="examples/minimal/config.yaml":
    uv run cp-font-gen generate --config {{CONFIG}} --dry-run

# Show what characters would be included
show CONFIG="examples/minimal/config.yaml":
    uv run cp-font-gen show --config {{CONFIG}}

# Extract characters from a text file
extract FILE:
    uv run cp-font-gen extract {{FILE}}

# Show generated fonts and their sizes
list-output:
    @echo "Generated fonts:"
    @find output -type f \( -name "*.pcf" -o -name "*.bdf" \) -exec ls -lh {} \; 2>/dev/null || echo "No fonts generated yet"

# Show manifest for a font family
show-manifest FAMILY="digits":
    @find output -name "{{FAMILY}}-manifest.json" -exec cat {} \; 2>/dev/null | uv run python -m json.tool || echo "No manifest found for '{{FAMILY}}'. Run 'just generate' first."

# Clean generated fonts
clean:
    @echo "Removing generated fonts..."
    rm -rf output/*
    @echo "✓ Clean complete"

# Clean Python cache files
clean-cache:
    @echo "Removing Python cache files and directories..."
    find . -type d -name "__pycache__" -not -path "./.venv/*" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -not -path "./.venv/*" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -not -path "./.venv/*" -delete 2>/dev/null || true
    rm -rf .pytest_cache .ruff_cache .mypy_cache
    rm -rf .coverage htmlcov
    rm -rf dist build src/*.egg-info
    find . -type f -name ".DS_Store" -delete 2>/dev/null || true
    @echo "✓ Cache cleaned"

# Clean everything (fonts, cache, venv)
clean-all: clean clean-cache
    @echo "Removing virtual environment..."
    rm -rf .venv uv.lock
    @echo "✓ Full clean complete"

# Show help
help:
    uv run cp-font-gen --help

# Sync dependencies (creates/updates .venv)
sync:
    uv sync

# Run tests
test:
    uv run python -m pytest

# Run tests with coverage
test-cov:
    uv run python -m pytest --cov=cp_font_gen --cov-report=term-missing

# Run tests in watch mode
test-watch:
    uv run python -m pytest_watch

# Format code with ruff
fmt:
    uv run ruff format .

# Check formatting without changing files
fmt-check:
    uv run ruff format --check .

# Lint code with ruff
lint:
    uv run ruff check .

# Lint and auto-fix issues
lint-fix:
    uv run ruff check --fix .

# Type check with mypy
typecheck:
    uv run mypy src/

# Run all quality checks (lint + typecheck + test)
check-all: lint typecheck test
    @echo "✓ All checks passed!"

# Format, lint, and test - full pre-commit workflow
pre-commit: fmt lint-fix test
    @echo "✓ Code formatted, linted, and tested!"
