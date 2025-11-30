# Future Enhancements

## Priority Queue

### ✅ TRACKED: Option 1 & Option 2
These items are prioritized and tracked for implementation after documentation restructure and packaging setup.

---

## TODO: Improve Test Coverage for cp-font-gen
**Priority**: Code Quality (High Value - ~1-2 days)
**Branch**: `test-refactoring` (in progress)

**Goal**: Increase test coverage from current 29% to at least 70%+

**Current Status** (as of test refactoring - 2025-11-29):
- **Overall**: 29% (16 passed, 1 failed, 1 skipped)
- **Test Structure**: ✅ Refactored and organized
  - `conftest.py` - Shared fixtures and helpers
  - `test_converter.py` - Converter unit tests (5 tests)
  - `test_generator.py` - Generator integration tests (2 tests)
  - `test_config.py` - Config tests (4 tests)
  - `test_utils.py` - Utility tests (4 tests)
  - `test_unicode.py` - Unicode tests (3 tests)

**Module Coverage**:
- **config.py**: 89% ✅ (Good coverage)
- **generator.py**: 69% ✅ (Was 12%, improved by Issue #1 tests)
- **converter.py**: 49% ⚠️ (Was 9%, improved by Issue #1 tests)
- **utils.py**: 35% ⚠️ (Needs improvement)
- **checker.py**: 0% ❌ (No tests)
- **cli.py**: 0% ❌ (No tests)
- **logger.py**: 0% ❌ (No tests)
- **tool_config.py**: 0% ❌ (No tests)

**Focus Areas**:
1. **cli.py** (0%) - Add integration tests for CLI commands
2. **checker.py** (0%) - Tool validation logic needs tests
3. **logger.py** (0%) - Test logging functionality
4. **tool_config.py** (0%) - Test configuration management
5. **converter.py** (49%) - Expand coverage of error paths and edge cases
6. **utils.py** (35%) - Increase coverage on utility functions
7. **generator.py** (69%) - Add tests for remaining edge cases
8. **Fix failing test** - `test_generate_font_with_letters_has_correct_encodings` needs investigation

**Implementation**:
- Write unit tests for each module
- Add integration tests for full pipeline
- Use pytest fixtures for temp files and mocking
- Mock subprocess calls in converter tests
- Add coverage tracking to CI/CD pipeline

**Commands**:
```bash
just test-cov              # Check current coverage
just test-watch            # Watch mode while writing tests
```

---

## TODO: Add System Font Tools to Baseline Justfile
**Priority**: Option 1 (Quick Win - ~30 min)

**Goal**: Add system-level font conversion tools to `~/cp-projects/justfile`

**Rationale**: The font generator requires system-level tools (otf2bdf, bdftopcf) that should be available at the workspace level. Python packages (fonttools, pyyaml, click) are managed per-project via `pyproject.toml` and `uv`.

**Implementation**:
- Add `install-font-tools` recipe to baseline justfile
- Install: otf2bdf, bdftopcf (via homebrew/apt)
- Make it a one-time setup command

**Example**:
```just
# In ~/cp-projects/justfile
install-font-tools:
    brew install otf2bdf bdftopcf
    @echo "✓ System font tools installed"
    @echo "Note: Python packages (fonttools, etc.) are managed per-project via uv"
```

**Note**: fonttools, pyyaml, and click are Python packages that should remain in project venvs, not installed globally.

---

## TODO: Auto-generate Config from Python Code
**Priority**: Option 2 (High Value - ~2-3 days)

**Goal**: Scan CircuitPython code to automatically generate config.yaml

**Rationale**: Manually tracking which characters are used in code is error-prone. A scanner can extract all string literals and determine the minimal character set needed.

**Implementation**:
Create a new tool: `cp-code-scanner`

**Features**:
- Parse Python files for string literals
- Extract all unique characters used
- Generate config.yaml with character set
- Optionally scan for unicode escapes (\u2190, etc.)
- Track which files use which characters (for debugging)

**Usage**:
```bash
# Scan a project
cp-code-scanner scan my-project/*.py --output config.yaml

# Then generate fonts
cd cp-font-gen
just generate ../my-project/font-config.yaml
```

**Parser approach**:
- Use Python's `ast` module to parse code
- Walk AST for `ast.Str` or `ast.Constant` nodes
- Extract string values
- Collect unique characters
- Output to YAML format

**Benefits**:
- No manual character tracking
- Ensures all displayed text has glyphs
- Catches forgotten special characters
- Updates as code changes

---

## Additional Future Ideas

### Font Preview Tool
Generate preview images of generated fonts for visual verification before deploying to hardware.

### Font Size Optimizer
Analyze which characters are most frequently used and suggest size optimizations.

### Multiple Font Support
Support for mixing fonts (e.g., one for digits, one for letters) to optimize space.

### Web Interface
Simple web UI for font generation without command line.
