"""
Integration Tests for Settings persistence with CMAT Installer

Tests cover:
- Settings persistence for last_install_directory
- Settings integration with dialog
- Cross-session persistence
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.settings import Settings


class TestSettingsIntegration(unittest.TestCase):
    """Test Settings class integration for install directory persistence."""

    def setUp(self):
        """Create temporary settings directory."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.settings_file = self.temp_dir / "settings.json"
        self.settings = Settings(settings_file=str(self.settings_file))

    def tearDown(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_get_last_install_directory_none_initially(self):
        """Test get_last_install_directory returns None initially."""
        # Act
        last_dir = self.settings.get_last_install_directory()

        # Assert
        self.assertIsNone(last_dir)

    def test_set_and_get_last_install_directory(self):
        """Test setting and getting last install directory."""
        # Arrange
        test_path = "/Users/test/projects/my-project"

        # Act
        self.settings.set_last_install_directory(test_path)
        retrieved_path = self.settings.get_last_install_directory()

        # Assert
        self.assertEqual(retrieved_path, test_path)

    def test_last_install_directory_persists_across_instances(self):
        """Test last directory persists when creating new Settings instance."""
        # Arrange
        test_path = "/Users/test/projects/persistence-test"

        # Act - set with first instance
        self.settings.set_last_install_directory(test_path)
        self.settings.save()

        # Create new Settings instance pointing to same file
        new_settings = Settings(settings_file=str(self.settings_file))
        retrieved_path = new_settings.get_last_install_directory()

        # Assert
        self.assertEqual(retrieved_path, test_path)

    def test_clear_last_install_directory(self):
        """Test clearing the last install directory."""
        # Arrange
        test_path = "/Users/test/projects/clear-test"
        self.settings.set_last_install_directory(test_path)

        # Act
        self.settings.clear_last_install_directory()
        retrieved_path = self.settings.get_last_install_directory()

        # Assert
        self.assertIsNone(retrieved_path)

    def test_set_last_install_directory_updates_existing(self):
        """Test setting last directory updates when already set."""
        # Arrange
        first_path = "/Users/test/projects/first"
        second_path = "/Users/test/projects/second"

        # Act
        self.settings.set_last_install_directory(first_path)
        self.assertEqual(self.settings.get_last_install_directory(), first_path)

        self.settings.set_last_install_directory(second_path)
        retrieved_path = self.settings.get_last_install_directory()

        # Assert
        self.assertEqual(retrieved_path, second_path)

    def test_settings_file_format(self):
        """Test that settings are stored in correct JSON format."""
        # Arrange
        test_path = "/Users/test/projects/format-test"

        # Act
        self.settings.set_last_install_directory(test_path)
        self.settings.save()

        # Read raw settings file
        with open(self.settings_file, 'r') as f:
            settings_data = json.load(f)

        # Assert
        self.assertIn("last_install_directory", settings_data)
        self.assertEqual(settings_data["last_install_directory"], test_path)

    def test_empty_string_path_handled(self):
        """Test handling of empty string path."""
        # Arrange & Act
        self.settings.set_last_install_directory("")
        retrieved_path = self.settings.get_last_install_directory()

        # Assert - empty string might be stored or converted to None
        # Document actual behavior
        self.assertTrue(retrieved_path == "" or retrieved_path is None)

    def test_path_with_special_characters(self):
        """Test paths with special characters are preserved."""
        # Arrange
        test_path = "/Users/test/My Projects!/Test@2024/CMAT Template (v3.0)"

        # Act
        self.settings.set_last_install_directory(test_path)
        retrieved_path = self.settings.get_last_install_directory()

        # Assert
        self.assertEqual(retrieved_path, test_path)

    def test_windows_path_format(self):
        """Test Windows-style paths are preserved."""
        # Arrange
        test_path = "C:\\Users\\Test\\Projects\\CMAT"

        # Act
        self.settings.set_last_install_directory(test_path)
        retrieved_path = self.settings.get_last_install_directory()

        # Assert
        self.assertEqual(retrieved_path, test_path)

    def test_other_settings_not_affected(self):
        """Test that setting install directory doesn't affect other settings."""
        # Arrange
        self.settings.set("claude_api_key", "test_key_12345")
        self.settings.set("model", "claude-sonnet-3-5")

        # Act
        self.settings.set_last_install_directory("/test/path")

        # Assert - other settings should still exist
        self.assertEqual(self.settings.get("claude_api_key"), "test_key_12345")
        self.assertEqual(self.settings.get("model"), "claude-sonnet-3-5")


class TestSettingsEdgeCases(unittest.TestCase):
    """Test edge cases in settings persistence."""

    def setUp(self):
        """Create temporary settings directory."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.settings_file = self.temp_dir / "settings.json"

    def tearDown(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_settings_creation_with_nonexistent_file(self):
        """Test Settings handles non-existent settings file."""
        # Act
        settings = Settings(settings_file=str(self.settings_file))
        last_dir = settings.get_last_install_directory()

        # Assert
        self.assertIsNone(last_dir)

    def test_settings_with_corrupted_json(self):
        """Test Settings handles corrupted JSON file gracefully."""
        # Arrange - write corrupted JSON
        with open(self.settings_file, 'w') as f:
            f.write("{invalid json content")

        # Act & Assert - should not crash, might return None or default
        try:
            settings = Settings(settings_file=str(self.settings_file))
            last_dir = settings.get_last_install_directory()
            # Success if no exception
        except Exception as e:
            # Document if exception is raised
            self.fail(f"Settings should handle corrupted JSON gracefully: {e}")

    def test_very_long_path(self):
        """Test handling of very long file paths."""
        # Arrange - create path at OS limit
        long_path = "/Users/test/" + ("very_long_directory_name/" * 20) + "project"

        # Act
        settings = Settings(settings_file=str(self.settings_file))
        settings.set_last_install_directory(long_path)
        retrieved_path = settings.get_last_install_directory()

        # Assert
        self.assertEqual(retrieved_path, long_path)


# =============================================================================
# Test Suite Runner
# =============================================================================

def run_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSettingsIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestSettingsEdgeCases))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_tests()

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
