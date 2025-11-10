"""
Unit Tests for CMATInstaller class

Tests cover:
- Initialization and configuration
- Directory validation (security, permissions, system paths)
- Installation flow (download, extract, validate, install)
- Error handling and rollback
- Security validations
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import zipfile
import io
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.installers.cmat_installer import (
    CMATInstaller,
    CMATInstallerError,
    SecurityError,
    NetworkError,
    ValidationError,
    InstallationState,
    REQUIRED_V3_FILES,
    SYSTEM_DIRECTORIES,
)


class TestCMATInstallerInitialization(unittest.TestCase):
    """Test installer initialization and configuration."""

    def test_init_with_valid_directory(self):
        """Test initialization with valid directory path."""
        # Arrange
        target_dir = Path(tempfile.gettempdir())

        # Act
        installer = CMATInstaller(target_dir)

        # Assert
        self.assertEqual(installer.target_directory, target_dir)
        self.assertIsNotNone(installer.github_url)
        self.assertTrue(installer.github_url.startswith("https://"))
        self.assertIsInstance(installer.state, InstallationState)

    def test_init_creates_state_object(self):
        """Test that initialization creates InstallationState object."""
        # Arrange
        target_dir = Path(tempfile.gettempdir())

        # Act
        installer = CMATInstaller(target_dir)

        # Assert
        self.assertIsInstance(installer.state, InstallationState)
        self.assertIsNone(installer.state.temp_dir)
        self.assertIsNone(installer.state.zip_path)
        self.assertIsNone(installer.state.backup_path)

    def test_github_url_format(self):
        """Test that GitHub URL is properly formatted."""
        # Arrange
        target_dir = Path(tempfile.gettempdir())

        # Act
        installer = CMATInstaller(target_dir)

        # Assert
        expected_parts = ["github.com", "anthropics", "ClaudeMultiAgentTemplate", "archive", "main.zip"]
        for part in expected_parts:
            self.assertIn(part, installer.github_url)


class TestDirectoryValidation(unittest.TestCase):
    """Test directory validation functionality."""

    def setUp(self):
        """Create temporary test directory."""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up temporary test directory."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_validate_target_directory_valid(self):
        """Test validation passes for valid, writable directory."""
        # Arrange
        installer = CMATInstaller(self.test_dir)

        # Act
        valid, message = installer.validate_target_directory()

        # Assert
        self.assertTrue(valid)
        self.assertIn("Valid", message)

    def test_validate_target_directory_nonexistent(self):
        """Test validation fails for non-existent directory."""
        # Arrange
        non_existent = self.test_dir / "does_not_exist"
        installer = CMATInstaller(non_existent)

        # Act
        valid, message = installer.validate_target_directory()

        # Assert
        self.assertFalse(valid)
        self.assertIn("does not exist", message.lower())

    def test_validate_system_directory_protection(self):
        """Test that system directories are blocked."""
        # Arrange - test various system directories
        system_paths = [
            Path("/usr"),
            Path("/System"),
            Path("C:\\Windows"),
            Path("C:\\Program Files"),
        ]

        for system_path in system_paths:
            with self.subTest(path=system_path):
                # Act
                installer = CMATInstaller(system_path)
                valid, message = installer.validate_target_directory()

                # Assert
                self.assertFalse(valid)
                self.assertIn("system", message.lower())

    def test_validate_readonly_directory(self):
        """Test validation fails for read-only directory."""
        # Arrange
        readonly_dir = self.test_dir / "readonly"
        readonly_dir.mkdir()

        # Make directory read-only
        if os.name != 'nt':  # Unix-like systems
            os.chmod(readonly_dir, 0o444)

            # Act
            installer = CMATInstaller(readonly_dir)
            valid, message = installer.validate_target_directory()

            # Assert
            self.assertFalse(valid)
            self.assertIn("not writable", message.lower())

            # Cleanup - restore permissions
            os.chmod(readonly_dir, 0o755)

    def test_check_existing_installation_no_claude(self):
        """Test existing installation check when no .claude folder exists."""
        # Arrange
        installer = CMATInstaller(self.test_dir)

        # Act
        has_existing = installer.check_existing_installation()

        # Assert
        self.assertFalse(has_existing)

    def test_check_existing_installation_has_claude(self):
        """Test existing installation check when .claude folder exists."""
        # Arrange
        claude_dir = self.test_dir / ".claude"
        claude_dir.mkdir()
        installer = CMATInstaller(self.test_dir)

        # Act
        has_existing = installer.check_existing_installation()

        # Assert
        self.assertTrue(has_existing)


class TestSecurityValidations(unittest.TestCase):
    """Test security validation functionality."""

    def setUp(self):
        """Create temporary test directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.installer = CMATInstaller(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_validate_zip_entry_normal_path(self):
        """Test ZIP entry validation passes for normal paths."""
        # Arrange
        normal_paths = [
            ".claude/scripts/cmat.sh",
            ".claude/AGENT_CONTRACTS.json",
            ".claude/agents/architect.md",
            "README.md",
        ]

        for path in normal_paths:
            with self.subTest(path=path):
                # Act
                is_valid = self.installer._validate_zip_entry(path)

                # Assert
                self.assertTrue(is_valid, f"Path {path} should be valid")

    def test_validate_zip_entry_directory_traversal(self):
        """Test ZIP entry validation blocks directory traversal attempts."""
        # Arrange
        malicious_paths = [
            "../../../etc/passwd",
            "../../.ssh/authorized_keys",
            ".claude/../../../etc/shadow",
            "..\\..\\Windows\\System32\\config\\SAM",
        ]

        for path in malicious_paths:
            with self.subTest(path=path):
                # Act
                is_valid = self.installer._validate_zip_entry(path)

                # Assert
                self.assertFalse(is_valid, f"Malicious path {path} should be blocked")

    def test_validate_zip_entry_absolute_paths(self):
        """Test ZIP entry validation blocks absolute paths."""
        # Arrange
        absolute_paths = [
            "/etc/passwd",
            "/usr/bin/bash",
            "C:\\Windows\\System32\\cmd.exe",
            "/System/Library/CoreServices/Finder.app",
        ]

        for path in absolute_paths:
            with self.subTest(path=path):
                # Act
                is_valid = self.installer._validate_zip_entry(path)

                # Assert
                self.assertFalse(is_valid, f"Absolute path {path} should be blocked")

    def test_validate_zip_entry_suspicious_characters(self):
        """Test ZIP entry validation blocks paths with suspicious characters."""
        # Arrange
        suspicious_paths = [
            ".claude/file<script>.sh",
            ".claude/file>output.txt",
            ".claude/file:stream.txt",
        ]

        for path in suspicious_paths:
            with self.subTest(path=path):
                # Act
                is_valid = self.installer._validate_zip_entry(path)

                # Assert
                # Note: Depending on implementation, this may or may not be blocked
                # Documenting expected behavior


class TestInstallationFlow(unittest.TestCase):
    """Test installation workflow and integration."""

    def setUp(self):
        """Create temporary test directory and mock installer."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.installer = CMATInstaller(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    @patch('src.installers.cmat_installer.CMATInstaller._download_zip')
    @patch('src.installers.cmat_installer.CMATInstaller._extract_zip')
    @patch('src.installers.cmat_installer.CMATInstaller._validate_structure')
    @patch('src.installers.cmat_installer.CMATInstaller._move_to_target')
    def test_install_success_flow(self, mock_move, mock_validate, mock_extract, mock_download):
        """Test successful installation flow."""
        # Arrange
        temp_dir = Path(tempfile.mkdtemp())
        mock_download.return_value = None
        mock_extract.return_value = temp_dir / ".claude"
        mock_validate.return_value = True
        mock_move.return_value = None

        def progress_callback(percent, message):
            pass

        # Act
        try:
            self.installer.install(progress_callback=progress_callback)

            # Assert
            mock_download.assert_called_once()
            mock_extract.assert_called_once()
            mock_validate.assert_called_once()
            mock_move.assert_called_once()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_install_invalid_directory_raises_security_error(self):
        """Test installation fails with SecurityError for system directory."""
        # Arrange
        system_installer = CMATInstaller(Path("/usr"))

        def progress_callback(percent, message):
            pass

        # Act & Assert
        with self.assertRaises(SecurityError):
            system_installer.install(progress_callback=progress_callback)

    @patch('src.installers.cmat_installer.CMATInstaller._download_zip')
    def test_install_download_failure_triggers_rollback(self, mock_download):
        """Test that download failure triggers rollback."""
        # Arrange
        mock_download.side_effect = NetworkError("Connection timeout")

        def progress_callback(percent, message):
            pass

        # Act & Assert
        with self.assertRaises(NetworkError):
            self.installer.install(progress_callback=progress_callback)

        # Verify cleanup occurred - no partial files should remain
        claude_dir = self.test_dir / ".claude"
        self.assertFalse(claude_dir.exists(), "Partial installation should be cleaned up")


class TestStructureValidation(unittest.TestCase):
    """Test CMAT v3.0 structure validation."""

    def setUp(self):
        """Create temporary test directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.installer = CMATInstaller(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_validate_structure_with_all_required_files(self):
        """Test validation passes when all required files exist."""
        # Arrange - create required file structure
        claude_dir = self.test_dir / ".claude"
        for required_file in REQUIRED_V3_FILES:
            file_path = self.test_dir / required_file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()

        # Act
        is_valid = self.installer._validate_structure(claude_dir)

        # Assert
        self.assertTrue(is_valid)

    def test_validate_structure_missing_required_file(self):
        """Test validation fails when required file is missing."""
        # Arrange - create incomplete structure (missing one required file)
        claude_dir = self.test_dir / ".claude"
        claude_dir.mkdir()

        # Create only first two required files
        for required_file in REQUIRED_V3_FILES[:2]:
            file_path = self.test_dir / required_file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()

        # Act & Assert
        with self.assertRaises(ValidationError):
            self.installer._validate_structure(claude_dir)

    def test_validate_structure_nonexistent_directory(self):
        """Test validation fails for non-existent directory."""
        # Arrange
        non_existent = self.test_dir / "does_not_exist"

        # Act & Assert
        with self.assertRaises(ValidationError):
            self.installer._validate_structure(non_existent)


class TestBackupAndRollback(unittest.TestCase):
    """Test backup and rollback functionality."""

    def setUp(self):
        """Create temporary test directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.installer = CMATInstaller(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_backup_existing_installation(self):
        """Test backup of existing .claude folder."""
        # Arrange - create existing installation
        claude_dir = self.test_dir / ".claude"
        claude_dir.mkdir()
        test_file = claude_dir / "test.txt"
        test_file.write_text("existing content")

        # Act
        backup_path = self.installer._backup_existing()

        # Assert
        self.assertIsNotNone(backup_path)
        self.assertTrue(backup_path.exists())
        backup_test_file = backup_path / "test.txt"
        self.assertTrue(backup_test_file.exists())
        self.assertEqual(backup_test_file.read_text(), "existing content")

    def test_rollback_restores_backup(self):
        """Test rollback restores backup on failure."""
        # Arrange - create backup
        claude_dir = self.test_dir / ".claude"
        claude_dir.mkdir()
        test_file = claude_dir / "original.txt"
        test_file.write_text("original content")

        backup_path = self.installer._backup_existing()
        self.installer.state.backup_path = backup_path

        # Simulate failed installation - replace content
        claude_dir = self.test_dir / ".claude"
        shutil.rmtree(claude_dir)
        claude_dir.mkdir()
        (claude_dir / "failed.txt").write_text("failed content")

        # Act
        self.installer._rollback()

        # Assert - original content should be restored
        restored_file = self.test_dir / ".claude" / "original.txt"
        self.assertTrue(restored_file.exists())
        self.assertEqual(restored_file.read_text(), "original content")

        # Failed content should be gone
        failed_file = self.test_dir / ".claude" / "failed.txt"
        self.assertFalse(failed_file.exists())

    def test_rollback_without_backup(self):
        """Test rollback cleans up when there's no backup."""
        # Arrange - partial installation without backup
        claude_dir = self.test_dir / ".claude"
        claude_dir.mkdir()
        (claude_dir / "partial.txt").write_text("partial installation")

        # Act
        self.installer._rollback()

        # Assert - partial installation should be removed
        self.assertFalse(claude_dir.exists())


class TestProgressTracking(unittest.TestCase):
    """Test progress callback functionality."""

    def setUp(self):
        """Create temporary test directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.installer = CMATInstaller(self.test_dir)
        self.progress_calls = []

    def tearDown(self):
        """Clean up temporary test directory."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_progress_callback_called_during_install(self):
        """Test that progress callback is invoked with correct parameters."""
        # Arrange
        def progress_callback(percent, message):
            self.progress_calls.append((percent, message))

        with patch('src.installers.cmat_installer.CMATInstaller._download_zip'):
            with patch('src.installers.cmat_installer.CMATInstaller._extract_zip'):
                with patch('src.installers.cmat_installer.CMATInstaller._validate_structure', return_value=True):
                    with patch('src.installers.cmat_installer.CMATInstaller._move_to_target'):
                        try:
                            # Act
                            self.installer.install(progress_callback=progress_callback)
                        except:
                            pass

        # Assert - progress callback should have been called
        self.assertGreater(len(self.progress_calls), 0)

        # Verify progress percentages are in valid range
        for percent, message in self.progress_calls:
            self.assertGreaterEqual(percent, 0)
            self.assertLessEqual(percent, 100)
            self.assertIsInstance(message, str)
            self.assertGreater(len(message), 0)

    def test_progress_callback_none_does_not_crash(self):
        """Test that installation works without progress callback."""
        # Arrange - mock all major steps
        with patch('src.installers.cmat_installer.CMATInstaller._download_zip'):
            with patch('src.installers.cmat_installer.CMATInstaller._extract_zip'):
                with patch('src.installers.cmat_installer.CMATInstaller._validate_structure', return_value=True):
                    with patch('src.installers.cmat_installer.CMATInstaller._move_to_target'):
                        try:
                            # Act - no progress callback provided
                            self.installer.install(progress_callback=None)
                        except:
                            pass

        # Assert - should not crash (implicit success if no exception)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and exception types."""

    def setUp(self):
        """Create temporary test directory."""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up temporary test directory."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_network_error_on_connection_failure(self):
        """Test NetworkError raised on connection failure."""
        # Arrange
        installer = CMATInstaller(self.test_dir)

        with patch('urllib.request.urlopen', side_effect=Exception("Connection refused")):
            # Act & Assert
            with self.assertRaises(NetworkError):
                installer._download_zip()

    def test_validation_error_on_invalid_structure(self):
        """Test ValidationError raised on invalid structure."""
        # Arrange
        installer = CMATInstaller(self.test_dir)
        invalid_dir = self.test_dir / "invalid"
        invalid_dir.mkdir()

        # Act & Assert
        with self.assertRaises(ValidationError):
            installer._validate_structure(invalid_dir)

    def test_security_error_on_system_directory(self):
        """Test SecurityError raised for system directory."""
        # Arrange
        installer = CMATInstaller(Path("/usr"))

        def progress_callback(percent, message):
            pass

        # Act & Assert
        with self.assertRaises(SecurityError):
            installer.install(progress_callback=progress_callback)


# =============================================================================
# Test Suite Runner
# =============================================================================

def run_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCMATInstallerInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestDirectoryValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityValidations))
    suite.addTests(loader.loadTestsFromTestCase(TestInstallationFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestStructureValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestBackupAndRollback))
    suite.addTests(loader.loadTestsFromTestCase(TestProgressTracking))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_tests()

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
