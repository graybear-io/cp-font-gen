# Future Enhancements

## Priority Queue

### ✅ TRACKED: Option 1 & Option 2
These items are prioritized and tracked for implementation after documentation restructure and packaging setup.

---

## ✅ COMPLETED: Test Refactoring (2025-11-29)
Successfully refactored and expanded test coverage from 29% → 67%
- Created comprehensive test files: test_checker.py, test_converter.py, test_generator.py, test_logger.py, test_tool_config.py
- All core modules now have 82-100% coverage
- 113 tests passing

---

## TODO: Add CLI Integration Tests
**Priority**: Code Quality (Final Push - ~1 day)

**Goal**: Reach 70%+ overall coverage by testing cli.py

**Current Status** (as of 2025-11-29):
- **Overall**: 67% (113 passed, 2 skipped)
- **Remaining untested**: cli.py (143 statements, 0% coverage)

**Module Coverage**:
- **logger.py**: 100% ✅
- **tool_config.py**: 100% ✅
- **utils.py**: 100% ✅
- **checker.py**: 94% ✅
- **converter.py**: 92% ✅
- **generator.py**: 82% ✅
- **config.py**: 89% ✅
- **cli.py**: 0% ❌ (Only remaining gap)

**Focus**:
Add integration tests for CLI commands in `test_cli.py`:
1. `generate` command - Test font generation workflow
2. `check` command - Test dependency checking
3. Click argument parsing and validation
4. Error handling and user feedback
5. Output file creation and formats

**Implementation**:
- Use Click's `CliRunner` for testing CLI commands
- Mock file system operations with pytest fixtures
- Test both success and error paths
- Verify output messages and exit codes

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
