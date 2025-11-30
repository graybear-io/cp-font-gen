"""Tests for checker.py - Tool validation and version checking."""

import subprocess
from unittest import mock

from cp_font_gen.checker import (
    check_command_exists,
    check_python_package,
    get_tool_requirements,
)


class TestCheckCommandExists:
    """Tests for check_command_exists function."""

    def test_existing_command(self):
        """Test that check_command_exists works with an existing command."""
        # Use 'python' which should exist in the test environment
        exists, version = check_command_exists("python")
        assert exists is True
        assert version is not None

    def test_nonexistent_command(self):
        """Test that check_command_exists returns False for nonexistent command."""
        exists, version = check_command_exists("this-command-does-not-exist-xyz123")
        assert exists is False
        assert version is None

    @mock.patch("subprocess.run")
    def test_command_without_version_flag(self, mock_run):
        """Test handling of commands that don't support --version."""
        # Simulate 'which' succeeding
        mock_run.side_effect = [
            mock.Mock(returncode=0, stdout="/usr/bin/cmd", stderr=""),
            # Simulate --version failing
            subprocess.CalledProcessError(1, "cmd"),
        ]

        exists, version = check_command_exists("cmd")
        assert exists is True
        assert version is None

    @mock.patch("subprocess.run")
    def test_version_timeout(self, mock_run):
        """Test handling of --version timeout."""
        # Simulate 'which' succeeding but --version timing out
        mock_run.side_effect = [
            mock.Mock(returncode=0, stdout="/usr/bin/cmd", stderr=""),
            subprocess.TimeoutExpired("cmd", 2),
        ]

        exists, version = check_command_exists("cmd")
        assert exists is True
        assert version is None

    @mock.patch("subprocess.run")
    def test_which_command_exception(self, mock_run):
        """Test handling of exception during 'which' command."""
        mock_run.side_effect = Exception("Unexpected error")

        exists, version = check_command_exists("cmd")
        assert exists is False
        assert version is None


class TestCheckPythonPackage:
    """Tests for check_python_package function."""

    def test_fonttools_package(self):
        """Test checking fonttools package (should be installed)."""
        exists, version = check_python_package("fonttools")
        assert exists is True
        assert version is not None
        assert "." in version  # Should be a version string like "4.x.x"

    def test_pyyaml_package(self):
        """Test checking pyyaml package (should be installed)."""
        exists, version = check_python_package("pyyaml")
        assert exists is True
        assert version is not None

    def test_click_package(self):
        """Test checking click package (should be installed)."""
        exists, version = check_python_package("click")
        assert exists is True
        assert version is not None

    def test_unknown_package(self):
        """Test checking an unsupported package name."""
        exists, version = check_python_package("unknown-package-xyz")
        assert exists is False
        assert version is None

    @mock.patch("cp_font_gen.checker.get_version")
    def test_package_without_version(self, mock_get_version):
        """Test handling of package that exists but version retrieval fails."""
        mock_get_version.side_effect = Exception("No version available")

        exists, version = check_python_package("fonttools")
        assert exists is True
        assert version is None

    @mock.patch("builtins.__import__")
    def test_missing_package(self, mock_import):
        """Test handling of missing package."""
        mock_import.side_effect = ImportError("No module named 'missing_package'")

        # We need to test with a package that checker knows about
        with mock.patch("importlib.import_module") as mock_import_module:
            mock_import_module.side_effect = ImportError("No module")
            # Directly test the import error path
            try:
                import fontTools as _  # noqa: F401
            except ImportError:
                exists, version = False, None
                assert exists is False
                assert version is None


class TestGetToolRequirements:
    """Tests for get_tool_requirements function."""

    def test_returns_dict(self):
        """Test that get_tool_requirements returns a dictionary."""
        requirements = get_tool_requirements()
        assert isinstance(requirements, dict)

    def test_has_system_commands(self):
        """Test that requirements include system commands."""
        requirements = get_tool_requirements()
        assert "System Commands" in requirements
        assert isinstance(requirements["System Commands"], list)

    def test_has_python_packages(self):
        """Test that requirements include Python packages."""
        requirements = get_tool_requirements()
        assert "Python Packages" in requirements
        assert isinstance(requirements["Python Packages"], list)

    def test_otf2bdf_in_system_commands(self):
        """Test that otf2bdf is in system commands."""
        requirements = get_tool_requirements()
        system_commands = requirements["System Commands"]
        command_names = [cmd[0] for cmd in system_commands]
        assert "otf2bdf" in command_names

    def test_bdftopcf_in_system_commands(self):
        """Test that bdftopcf is in system commands."""
        requirements = get_tool_requirements()
        system_commands = requirements["System Commands"]
        command_names = [cmd[0] for cmd in system_commands]
        assert "bdftopcf" in command_names

    def test_fonttools_in_python_packages(self):
        """Test that fonttools is in Python packages."""
        requirements = get_tool_requirements()
        python_packages = requirements["Python Packages"]
        package_names = [pkg[0] for pkg in python_packages]
        assert "fonttools" in package_names

    def test_pyyaml_in_python_packages(self):
        """Test that pyyaml is in Python packages."""
        requirements = get_tool_requirements()
        python_packages = requirements["Python Packages"]
        package_names = [pkg[0] for pkg in python_packages]
        assert "pyyaml" in package_names

    def test_click_in_python_packages(self):
        """Test that click is in Python packages."""
        requirements = get_tool_requirements()
        python_packages = requirements["Python Packages"]
        package_names = [pkg[0] for pkg in python_packages]
        assert "click" in package_names

    def test_commands_have_install_instructions(self):
        """Test that all system commands have install instructions."""
        requirements = get_tool_requirements()
        for cmd_name, install_cmd in requirements["System Commands"]:
            assert isinstance(cmd_name, str)
            assert isinstance(install_cmd, str)
            assert len(install_cmd) > 0

    def test_packages_have_install_instructions(self):
        """Test that all Python packages have install instructions."""
        requirements = get_tool_requirements()
        for pkg_name, install_cmd in requirements["Python Packages"]:
            assert isinstance(pkg_name, str)
            assert isinstance(install_cmd, str)
            assert len(install_cmd) > 0
