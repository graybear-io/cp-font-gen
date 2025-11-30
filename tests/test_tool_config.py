"""Tests for tool_config.py - Tool-wide configuration management."""

import os
import tempfile
from pathlib import Path
from unittest import mock

import yaml

from cp_font_gen.tool_config import (
    get_default_output_dir,
    get_tool_config_path,
    load_tool_config,
)


class TestGetToolConfigPath:
    """Tests for get_tool_config_path function."""

    def test_default_config_path(self):
        """Test default config path when XDG_CONFIG_HOME is not set."""
        with mock.patch.dict(os.environ, {}, clear=True):
            # Remove XDG_CONFIG_HOME if it exists
            os.environ.pop("XDG_CONFIG_HOME", None)

            config_path = get_tool_config_path()
            expected = Path.home() / ".config" / "cp-font-gen" / "config.yaml"
            assert config_path == expected

    def test_xdg_config_home_set(self):
        """Test config path when XDG_CONFIG_HOME is set."""
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": tmpdir}),
        ):
            config_path = get_tool_config_path()
            expected = Path(tmpdir) / "cp-font-gen" / "config.yaml"
            assert config_path == expected

    def test_returns_path_object(self):
        """Test that the function returns a Path object."""
        config_path = get_tool_config_path()
        assert isinstance(config_path, Path)

    def test_path_ends_with_config_yaml(self):
        """Test that the path ends with config.yaml."""
        config_path = get_tool_config_path()
        assert config_path.name == "config.yaml"


class TestLoadToolConfig:
    """Tests for load_tool_config function."""

    def test_nonexistent_config_returns_none(self):
        """Test that load_tool_config returns None when config doesn't exist."""
        with mock.patch("cp_font_gen.tool_config.get_tool_config_path") as mock_path:
            mock_path.return_value = Path("/nonexistent/path/config.yaml")
            result = load_tool_config()
            assert result is None

    def test_valid_config_file(self):
        """Test loading a valid config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            config_data = {"output_directory": "/tmp/fonts", "verbose": True}
            yaml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            with mock.patch("cp_font_gen.tool_config.get_tool_config_path") as mock_path:
                mock_path.return_value = config_path
                result = load_tool_config()
                assert result == config_data
                assert result["output_directory"] == "/tmp/fonts"
                assert result["verbose"] is True
        finally:
            config_path.unlink()

    def test_empty_config_file(self):
        """Test loading an empty config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            config_path = Path(f.name)

        try:
            with mock.patch("cp_font_gen.tool_config.get_tool_config_path") as mock_path:
                mock_path.return_value = config_path
                result = load_tool_config()
                assert result is None
        finally:
            config_path.unlink()

    def test_invalid_yaml_returns_none(self):
        """Test that invalid YAML returns None."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_path = Path(f.name)

        try:
            with mock.patch("cp_font_gen.tool_config.get_tool_config_path") as mock_path:
                mock_path.return_value = config_path
                result = load_tool_config()
                assert result is None
        finally:
            config_path.unlink()

    def test_config_with_nested_structure(self):
        """Test loading a config with nested structure."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            config_data = {
                "output_directory": "/tmp/fonts",
                "defaults": {"size": 16, "format": "bdf"},
            }
            yaml.dump(config_data, f)
            config_path = Path(f.name)

        try:
            with mock.patch("cp_font_gen.tool_config.get_tool_config_path") as mock_path:
                mock_path.return_value = config_path
                result = load_tool_config()
                assert result["defaults"]["size"] == 16
                assert result["defaults"]["format"] == "bdf"
        finally:
            config_path.unlink()


class TestGetDefaultOutputDir:
    """Tests for get_default_output_dir function."""

    def test_no_config_returns_cwd(self):
        """Test that function returns cwd when no config exists."""
        with mock.patch("cp_font_gen.tool_config.load_tool_config") as mock_load:
            mock_load.return_value = None
            result = get_default_output_dir()
            assert result == Path.cwd()

    def test_config_without_output_directory_returns_cwd(self):
        """Test that function returns cwd when config doesn't have output_directory."""
        with mock.patch("cp_font_gen.tool_config.load_tool_config") as mock_load:
            mock_load.return_value = {"verbose": True}
            result = get_default_output_dir()
            assert result == Path.cwd()

    def test_config_with_output_directory(self):
        """Test that function returns configured output directory."""
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            mock.patch("cp_font_gen.tool_config.load_tool_config") as mock_load,
        ):
            mock_load.return_value = {"output_directory": tmpdir}
            result = get_default_output_dir()
            assert result == Path(tmpdir)

    def test_config_with_tilde_expansion(self):
        """Test that function expands ~ in output directory path."""
        with mock.patch("cp_font_gen.tool_config.load_tool_config") as mock_load:
            mock_load.return_value = {"output_directory": "~/fonts"}
            result = get_default_output_dir()
            assert result == Path.home() / "fonts"
            assert "~" not in str(result)

    def test_returns_path_object(self):
        """Test that the function returns a Path object."""
        with mock.patch("cp_font_gen.tool_config.load_tool_config") as mock_load:
            mock_load.return_value = None
            result = get_default_output_dir()
            assert isinstance(result, Path)

    def test_config_with_relative_path(self):
        """Test handling of relative path in config."""
        with mock.patch("cp_font_gen.tool_config.load_tool_config") as mock_load:
            mock_load.return_value = {"output_directory": "output/fonts"}
            result = get_default_output_dir()
            assert result == Path("output/fonts")

    def test_config_with_absolute_path(self):
        """Test handling of absolute path in config."""
        with mock.patch("cp_font_gen.tool_config.load_tool_config") as mock_load:
            mock_load.return_value = {"output_directory": "/tmp/my-fonts"}
            result = get_default_output_dir()
            assert result == Path("/tmp/my-fonts")
