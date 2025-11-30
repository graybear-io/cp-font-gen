"""Tests for logger.py - Logging infrastructure."""

from datetime import datetime
from unittest import mock

from cp_font_gen.logger import GenerationLogger


class TestGenerationLoggerInit:
    """Tests for GenerationLogger initialization."""

    def test_default_initialization(self):
        """Test logger with default settings."""
        logger = GenerationLogger()
        assert logger.verbose is False
        assert logger.debug is False
        assert logger.log_entries == []
        assert logger.warnings == []
        assert logger.errors == []

    def test_verbose_initialization(self):
        """Test logger with verbose=True."""
        logger = GenerationLogger(verbose=True)
        assert logger.verbose is True
        assert logger.debug is False

    def test_debug_initialization(self):
        """Test logger with debug=True (implies verbose)."""
        logger = GenerationLogger(debug=True)
        assert logger.verbose is True  # debug implies verbose
        assert logger.debug is True

    def test_verbose_and_debug(self):
        """Test logger with both verbose and debug."""
        logger = GenerationLogger(verbose=True, debug=True)
        assert logger.verbose is True
        assert logger.debug is True


class TestLogCommand:
    """Tests for log_command method."""

    def test_log_command_stores_entry(self):
        """Test that log_command stores log entry."""
        logger = GenerationLogger()
        logger.log_command("test_step", "test command", "started")
        assert len(logger.log_entries) == 1
        assert logger.log_entries[0]["step"] == "test_step"
        assert logger.log_entries[0]["command"] == "test command"
        assert logger.log_entries[0]["status"] == "started"

    def test_log_command_with_kwargs(self):
        """Test that log_command stores additional kwargs."""
        logger = GenerationLogger()
        logger.log_command(
            "test_step", "test command", "success", output="file.txt", size_kb="10.5"
        )
        assert len(logger.log_entries) == 1
        assert logger.log_entries[0]["output"] == "file.txt"
        assert logger.log_entries[0]["size_kb"] == "10.5"

    @mock.patch("click.echo")
    def test_log_command_started_verbose(self, mock_echo):
        """Test log_command with status='started' in verbose mode."""
        logger = GenerationLogger(verbose=True)
        logger.log_command("subset_font", "fontTools.subset", "started", input="font.ttf")
        mock_echo.assert_called_once()
        call_args = mock_echo.call_args[0][0]
        assert "[subset_font]" in call_args
        assert "fontTools.subset" in call_args

    @mock.patch("click.echo")
    def test_log_command_success_verbose(self, mock_echo):
        """Test log_command with status='success' in verbose mode."""
        logger = GenerationLogger(verbose=True)
        logger.log_command("convert_to_bdf", "otf2bdf", "success", output="font.bdf", size_kb="2.5")
        assert mock_echo.called
        # Check that success message includes checkmark and output
        call_args = str(mock_echo.call_args[0][0])
        assert "✓" in call_args
        assert "convert_to_bdf" in call_args

    @mock.patch("click.echo")
    def test_log_command_failed_verbose(self, mock_echo):
        """Test log_command with status='failed' in verbose mode."""
        logger = GenerationLogger(verbose=True)
        logger.log_command("convert_to_bdf", "otf2bdf", "failed", error="Command not found")
        assert mock_echo.called
        # Should print error message
        calls = [str(call[0][0]) for call in mock_echo.call_args_list]
        assert any("✗" in call for call in calls)
        assert any("Error: Command not found" in call for call in calls)

    @mock.patch("click.echo")
    def test_log_command_not_verbose(self, mock_echo):
        """Test that log_command doesn't print when not verbose."""
        logger = GenerationLogger(verbose=False)
        logger.log_command("test_step", "test command", "started")
        mock_echo.assert_not_called()


class TestInfoMethod:
    """Tests for info method."""

    @mock.patch("click.echo")
    def test_info_verbose_mode(self, mock_echo):
        """Test that info prints in verbose mode."""
        logger = GenerationLogger(verbose=True)
        logger.info("Test message")
        mock_echo.assert_called_once()
        assert "Test message" in mock_echo.call_args[0][0]

    @mock.patch("click.echo")
    def test_info_not_verbose(self, mock_echo):
        """Test that info doesn't print when not verbose."""
        logger = GenerationLogger(verbose=False)
        logger.info("Test message")
        mock_echo.assert_not_called()

    @mock.patch("click.echo")
    def test_info_with_indent(self, mock_echo):
        """Test info with custom indentation."""
        logger = GenerationLogger(verbose=True)
        logger.info("Test message", indent=4)
        call_args = mock_echo.call_args[0][0]
        assert call_args.startswith("    ")  # 4 spaces
        assert "Test message" in call_args


class TestWarnMethod:
    """Tests for warn method."""

    def test_warn_stores_warning(self):
        """Test that warn stores warning in list."""
        logger = GenerationLogger()
        logger.warn("Test warning")
        assert len(logger.warnings) == 1
        assert logger.warnings[0] == "Test warning"

    @mock.patch("click.echo")
    def test_warn_verbose_mode(self, mock_echo):
        """Test that warn prints in verbose mode."""
        logger = GenerationLogger(verbose=True)
        logger.warn("Test warning")
        mock_echo.assert_called_once()
        call_args = str(mock_echo.call_args[0][0])
        assert "WARNING" in call_args
        assert "Test warning" in call_args

    @mock.patch("click.echo")
    def test_warn_not_verbose(self, mock_echo):
        """Test that warn doesn't print when not verbose."""
        logger = GenerationLogger(verbose=False)
        logger.warn("Test warning")
        # Still stores the warning
        assert len(logger.warnings) == 1
        # But doesn't print
        mock_echo.assert_not_called()


class TestErrorMethod:
    """Tests for error method."""

    def test_error_stores_error(self):
        """Test that error stores error in list."""
        logger = GenerationLogger()
        logger.error("Test error")
        assert len(logger.errors) == 1
        assert logger.errors[0] == "Test error"

    @mock.patch("click.echo")
    def test_error_always_prints(self, mock_echo):
        """Test that error always prints, even when not verbose."""
        logger = GenerationLogger(verbose=False)
        logger.error("Test error")
        mock_echo.assert_called_once()
        call_args = str(mock_echo.call_args[0][0])
        assert "ERROR" in call_args
        assert "Test error" in call_args

    @mock.patch("click.echo")
    def test_error_prints_to_stderr(self, mock_echo):
        """Test that error prints to stderr."""
        logger = GenerationLogger()
        logger.error("Test error")
        assert mock_echo.call_args[1]["err"] is True


class TestSuccessMethod:
    """Tests for success method."""

    @mock.patch("click.echo")
    def test_success_verbose_mode(self, mock_echo):
        """Test that success prints in verbose mode."""
        logger = GenerationLogger(verbose=True)
        logger.success("Test success")
        mock_echo.assert_called_once()
        call_args = str(mock_echo.call_args[0][0])
        assert "✓" in call_args
        assert "Test success" in call_args

    @mock.patch("click.echo")
    def test_success_not_verbose(self, mock_echo):
        """Test that success doesn't print when not verbose."""
        logger = GenerationLogger(verbose=False)
        logger.success("Test success")
        mock_echo.assert_not_called()


class TestSectionMethod:
    """Tests for section method."""

    @mock.patch("click.echo")
    def test_section_verbose_mode(self, mock_echo):
        """Test that section prints in verbose mode."""
        logger = GenerationLogger(verbose=True)
        logger.section("Test Section")
        mock_echo.assert_called_once()
        call_args = mock_echo.call_args[0][0]
        assert "Test Section" in call_args
        assert call_args.startswith("\n")

    @mock.patch("click.echo")
    def test_section_not_verbose(self, mock_echo):
        """Test that section doesn't print when not verbose."""
        logger = GenerationLogger(verbose=False)
        logger.section("Test Section")
        mock_echo.assert_not_called()


class TestGetDebugInfo:
    """Tests for get_debug_info method."""

    def test_basic_debug_info(self):
        """Test get_debug_info with basic information."""
        logger = GenerationLogger()
        debug_info = logger.get_debug_info("1.0.0")

        assert "timestamp" in debug_info
        assert "tool_version" in debug_info
        assert debug_info["tool_version"] == "1.0.0"
        assert "execution_log" in debug_info
        assert "warnings" in debug_info
        assert "errors" in debug_info

    def test_debug_info_timestamp_format(self):
        """Test that timestamp is in ISO format with Z suffix."""
        logger = GenerationLogger()
        debug_info = logger.get_debug_info("1.0.0")
        timestamp = debug_info["timestamp"]
        assert timestamp.endswith("Z")
        # Verify it's a valid ISO format
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    def test_debug_info_with_log_entries(self):
        """Test that debug_info includes log entries."""
        logger = GenerationLogger()
        logger.log_command("test_step", "test command", "success")
        debug_info = logger.get_debug_info("1.0.0")

        assert len(debug_info["execution_log"]) == 1
        assert debug_info["execution_log"][0]["step"] == "test_step"

    def test_debug_info_with_warnings_and_errors(self):
        """Test that debug_info includes warnings and errors."""
        logger = GenerationLogger()
        logger.warn("Test warning")
        logger.error("Test error")
        debug_info = logger.get_debug_info("1.0.0")

        assert len(debug_info["warnings"]) == 1
        assert debug_info["warnings"][0] == "Test warning"
        assert len(debug_info["errors"]) == 1
        assert debug_info["errors"][0] == "Test error"

    def test_debug_info_with_character_coverage(self):
        """Test that debug_info includes character coverage when provided."""
        logger = GenerationLogger()
        coverage = {"found": 10, "missing": 2, "rate": "83.3%"}
        debug_info = logger.get_debug_info("1.0.0", character_coverage=coverage)

        assert "character_coverage" in debug_info
        assert debug_info["character_coverage"] == coverage

    def test_debug_info_without_character_coverage(self):
        """Test that character_coverage is not included when None."""
        logger = GenerationLogger()
        debug_info = logger.get_debug_info("1.0.0", character_coverage=None)

        assert "character_coverage" not in debug_info


class TestLoggerIntegration:
    """Integration tests for logger usage patterns."""

    def test_typical_workflow(self):
        """Test a typical logging workflow."""
        logger = GenerationLogger(verbose=True, debug=True)

        logger.section("Starting font generation")
        logger.log_command("subset_font", "fontTools.subset", "started")
        logger.log_command("subset_font", "fontTools.subset", "success", glyphs_produced=10)
        logger.warn("Some characters not found")
        logger.success("Font generated successfully")

        # Verify state
        assert len(logger.log_entries) == 2
        assert len(logger.warnings) == 1
        assert len(logger.errors) == 0

        debug_info = logger.get_debug_info("1.0.0")
        assert len(debug_info["execution_log"]) == 2
        assert len(debug_info["warnings"]) == 1

    @mock.patch("click.echo")
    def test_silent_mode_only_errors(self, mock_echo):
        """Test that only errors print in non-verbose mode."""
        logger = GenerationLogger(verbose=False)

        logger.info("This should not print")
        logger.warn("This should not print")
        logger.success("This should not print")
        logger.error("This should print")

        # Only error should have printed
        assert mock_echo.call_count == 1
        call_args = str(mock_echo.call_args[0][0])
        assert "ERROR" in call_args
