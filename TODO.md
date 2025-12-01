# Future Enhancements

## Priority Queue

### ✅ TRACKED: Option 1 & Option 2
These items are prioritized and tracked for implementation after documentation restructure and packaging setup.

---

## ✅ COMPLETED: Issue #4 - BDF Latin-1 Encoding Fix (2025-11-30)
Fixed UTF-8 encoding error when processing BDF files with Latin-1 metadata
- **Problem**: Icons example failed with `'utf-8' codec can't decode byte 0xae`
- **Solution**: Implemented defensive UTF-8 → Latin-1 fallback in `fix_bdf_encodings()`
- **Testing**: Added `test_fix_bdf_encodings_handles_latin1_metadata()` test
- **Documentation**: Complete fix documentation in `docs/issues/resolved/issue-4.md`
- **Impact**: All examples now work (icons with Unicode symbols now generates successfully)
- **Test count**: 114 tests passing (was 113)
- **PR**: #5 (merged)

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

**Current Status** (as of 2025-11-30):
- **Overall**: 67% (114 passed, 2 skipped)
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

## TODO: Set Up CI/CD and PyPI Publishing
**Priority**: Infrastructure (High Value - ~1 day)

**Goal**: Automate testing with CircleCI and enable PyPI package distribution

**Phase 1: CircleCI Setup**
- Create `.circleci/config.yml` for automated testing
- Run tests on multiple Python versions (3.10, 3.11, 3.12)
- Generate and upload coverage reports (codecov.io or coveralls)
- Run on every push and PR
- Badge for README showing build status

**Phase 2: Package Configuration**
- Ensure `pyproject.toml` is configured for distribution
- Add package metadata (description, keywords, classifiers)
- Configure entry points for CLI commands
- Test local package building (`uv build`)

**Phase 3: PyPI Publishing**
- Test publishing to TestPyPI first
- Configure PyPI token in CircleCI secrets
- Set up CircleCI job to publish on tagged releases (e.g., `v1.0.0`)
- Document release process for maintainers

**Benefits**:
- Automated testing ensures quality
- Easy installation via `pip install cp-font-gen` or `uv add cp-font-gen`
- Versioned releases with automated publishing
- Coverage tracking over time

**Commands**:
```bash
# Local testing
uv build                    # Test package building
uv run twine check dist/*   # Verify package metadata

# CircleCI will handle
pytest --cov                # Run tests with coverage
twine upload dist/*         # Publish to PyPI (on tags)
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
