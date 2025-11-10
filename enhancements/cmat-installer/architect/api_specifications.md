---
enhancement: cmat-installer
agent: architect
task_id: task_1762445530_49766
timestamp: 2025-11-06T08:00:00Z
status: READY_FOR_IMPLEMENTATION
---

# API Specifications: CMAT Template Installer

## Overview

This document provides detailed API specifications, code examples, and interface definitions for the CMAT Template Installer components. Use this as a reference during implementation.

---

## Table of Contents

1. [CMATInstaller API](#1-cmatinstaller-api)
2. [InstallCMATDialog API](#2-installcmatdialog-api)
3. [Exception Hierarchy](#3-exception-hierarchy)
4. [Progress Callback Protocol](#4-progress-callback-protocol)
5. [Settings Extension API](#5-settings-extension-api)
6. [Code Examples](#6-code-examples)

---

## 1. CMATInstaller API

### 1.1 Class Definition

```python
"""
CMAT Template Installer - Business Logic Layer

Handles downloading, extracting, and validating CMAT template installations.
Thread-safe, supports progress callbacks, implements atomic operations.
"""

from pathlib import Path
from typing import Optional, Callable, Tuple
import urllib.request
import zipfile
import shutil
import tempfile
import os
import ssl
import uuid


class CMATInstaller:
    """
    Installer for Claude Multi-Agent Template (CMAT) v3.0.

    Provides thread-safe installation of CMAT template from GitHub,
    with progress tracking, security validation, and atomic operations.

    Example:
        >>> installer = CMATInstaller(
        ...     target_directory=Path("/home/user/myproject"),
        ...     github_owner="anthropics",
        ...     github_repo="ClaudeMultiAgentTemplate"
        ... )
        >>> success = installer.install(
        ...     progress_callback=lambda msg, pct: print(f"{pct}%: {msg}"),
        ...     overwrite=False
        ... )
    """

    def __init__(
        self,
        target_directory: Path,
        github_owner: str = "anthropics",
        github_repo: str = "ClaudeMultiAgentTemplate",
        github_branch: str = "main",
    ):
        """
        Initialize CMAT installer.

        Args:
            target_directory: Directory where .claude/ will be installed
            github_owner: GitHub repository owner/organization
            github_repo: GitHub repository name
            github_branch: Branch to download from (default: "main")

        Raises:
            ValueError: If target_directory is invalid or unsafe
            TypeError: If arguments have incorrect types

        Example:
            >>> installer = CMATInstaller(
            ...     target_directory=Path("/path/to/project")
            ... )
        """
        pass

    def install(
        self,
        progress_callback: Optional[Callable[[str, int], None]] = None,
        overwrite: bool = False,
    ) -> bool:
        """
        Perform complete installation: download → extract → validate → install.

        This is the main entry point. Performs installation atomically with
        automatic cleanup and rollback on failure.

        Args:
            progress_callback: Optional callback(message: str, percent: int)
                Called periodically to report progress (0-100)
            overwrite: Whether to overwrite existing .claude folder
                If False and .claude exists, raises InstallationError

        Returns:
            True if installation successful

        Raises:
            InstallationError: If installation fails for any reason
            SecurityError: If security validation fails
            NetworkError: If download fails
            ValidationError: If template structure is invalid

        Thread Safety:
            This method is thread-safe and can be called from background thread.
            progress_callback will be called from the same thread.

        Example:
            >>> def progress(msg, pct):
            ...     print(f"[{pct:3d}%] {msg}")
            >>>
            >>> success = installer.install(
            ...     progress_callback=progress,
            ...     overwrite=False
            ... )
            [  0%] Initializing installation...
            [ 10%] Downloading template from GitHub...
            [ 30%] Download complete, extracting...
            [ 70%] Validating installation...
            [100%] Installation complete!
        """
        pass

    def validate_target_directory(self) -> Tuple[bool, Optional[str]]:
        """
        Validate target directory is safe and writable.

        Checks:
        - Directory exists
        - Directory is writable
        - Directory is not a system directory
        - Directory path is absolute

        Returns:
            (is_valid, error_message) tuple
            - is_valid: True if directory is valid
            - error_message: None if valid, error description if invalid

        Example:
            >>> installer = CMATInstaller(Path("/tmp/test"))
            >>> is_valid, error = installer.validate_target_directory()
            >>> if not is_valid:
            ...     print(f"Invalid: {error}")
        """
        pass

    def check_existing_installation(self) -> bool:
        """
        Check if .claude folder already exists in target directory.

        Returns:
            True if .claude exists, False otherwise

        Example:
            >>> if installer.check_existing_installation():
            ...     print("Warning: .claude already exists")
            ...     if not confirm_overwrite():
            ...         return
        """
        pass

    def get_download_url(self) -> str:
        """
        Get the GitHub download URL for the template.

        Returns:
            HTTPS URL to ZIP archive

        Example:
            >>> url = installer.get_download_url()
            >>> print(url)
            https://github.com/anthropics/ClaudeMultiAgentTemplate/archive/refs/heads/main.zip
        """
        pass
```

### 1.2 Private Methods (Internal API)

```python
def _download_zip(
    self,
    progress_callback: Optional[Callable[[str, int], None]]
) -> Path:
    """
    Download ZIP from GitHub to temporary directory.

    Args:
        progress_callback: Progress callback for download updates

    Returns:
        Path to downloaded ZIP file

    Raises:
        NetworkError: If download fails
        SecurityError: If URL is not HTTPS

    Progress Range: 0-30%

    Implementation Notes:
    - Uses urllib.request.urlopen with SSL verification
    - Downloads in chunks (8 KB) to track progress
    - Reports progress every 5% or 500 KB
    - Uses temporary file for atomic download
    - Cleans up on failure
    """
    pass


def _extract_zip(
    self,
    zip_path: Path,
    progress_callback: Optional[Callable[[str, int], None]]
) -> Path:
    """
    Extract .claude folder from ZIP to temporary directory.

    Args:
        zip_path: Path to downloaded ZIP file
        progress_callback: Progress callback for extraction updates

    Returns:
        Path to extracted .claude folder in temp directory

    Raises:
        ValidationError: If ZIP is corrupted or invalid
        SecurityError: If ZIP contains unsafe entries

    Progress Range: 30-70%

    Implementation Notes:
    - Validates every ZIP entry before extraction
    - Rejects entries with ".." or absolute paths
    - Extracts to temp directory first
    - Locates .claude folder in extracted structure
    - ZIP may have repo name prefix (e.g., "repo-main/.claude/")
    """
    pass


def _validate_structure(self, extracted_path: Path) -> bool:
    """
    Validate extracted .claude folder has required v3.0 structure.

    Args:
        extracted_path: Path to extracted .claude folder

    Returns:
        True if structure is valid, False otherwise

    Required Files:
    - .claude/scripts/cmat.sh
    - .claude/AGENT_CONTRACTS.json
    - .claude/skills/skills.json

    Recommended Files (warnings only):
    - .claude/queues/task_queue.json
    - .claude/agents/agents.json
    - .claude/WORKFLOW_STATES.json

    Progress Range: 70-90%
    """
    pass


def _move_to_target(self, temp_path: Path) -> None:
    """
    Atomically move .claude from temp to target directory.

    Args:
        temp_path: Path to .claude folder in temp directory

    Raises:
        OSError: If move fails
        PermissionError: If target not writable

    Progress Range: 90-100%

    Implementation Notes:
    - Uses shutil.move for atomic operation
    - Creates parent directories if needed
    - Verifies permissions before move
    - On Windows, may need to handle file locks
    """
    pass


def _backup_existing(self) -> Optional[Path]:
    """
    Backup existing .claude folder before overwrite.

    Returns:
        Path to backup folder, or None if no backup needed

    Backup Location:
    - Same parent directory as target
    - Named: .claude.backup.{timestamp}

    Example:
    - Target: /home/user/project/.claude
    - Backup: /home/user/project/.claude.backup.20250106_080000
    """
    pass


def _rollback(self, backup_path: Optional[Path]) -> None:
    """
    Restore from backup on installation failure.

    Args:
        backup_path: Path to backup folder (if exists)

    Restores backup to original location and cleans up temp files.
    """
    pass


def _cleanup_temp(self, temp_dir: Path) -> None:
    """
    Clean up temporary files and directories.

    Args:
        temp_dir: Path to temporary directory

    Silently ignores errors (best-effort cleanup).
    """
    pass


def _validate_zip_entry(self, zip_entry_name: str) -> bool:
    """
    Validate ZIP entry for security threats.

    Args:
        zip_entry_name: Name/path of ZIP entry

    Returns:
        True if entry is safe, False if dangerous

    Checks:
    - No ".." components (directory traversal)
    - Not an absolute path
    - No suspicious characters (<, >, :, ", |, ?, *)
    - Path normalizes correctly

    Example:
        >>> installer._validate_zip_entry("folder/.claude/cmat.sh")
        True
        >>> installer._validate_zip_entry("../../../etc/passwd")
        False
    """
    pass


def _is_system_directory(self, path: Path) -> bool:
    """
    Check if path is or is within a system directory.

    Args:
        path: Path to check

    Returns:
        True if path is a system directory, False otherwise

    System Directories:
    - Unix/Linux/macOS: /usr, /bin, /etc, /System, etc.
    - Windows: C:\\Windows, C:\\Program Files, etc.

    Example:
        >>> installer._is_system_directory(Path("/usr/local"))
        True
        >>> installer._is_system_directory(Path("/home/user"))
        False
    """
    pass
```

---

## 2. InstallCMATDialog API

### 2.1 Class Definition

```python
"""
Install CMAT Template Dialog - UI Layer

Tkinter dialog for CMAT template installation with progress tracking.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import queue
from typing import Optional, Dict, Any

from .base_dialog import BaseDialog
from ..installers.cmat_installer import CMATInstaller, CMATInstallerError


class InstallCMATDialog(BaseDialog):
    """
    Dialog for installing CMAT template from GitHub.

    Provides user interface for:
    - Selecting installation directory
    - Tracking installation progress
    - Handling errors
    - Confirming success and connecting to project

    Inherits from BaseDialog for consistent behavior.
    """

    def __init__(self, parent):
        """
        Initialize installation dialog.

        Args:
            parent: Parent window (MainWindow)

        Creates dialog with:
        - 700x500 dimensions
        - Modal behavior
        - Centered on parent
        """
        super().__init__(parent, "Install CMAT Template", 700, 500)

        # State
        self.target_directory: Optional[Path] = None
        self.installer: Optional[CMATInstaller] = None
        self.installation_thread: Optional[threading.Thread] = None
        self.result_queue: queue.Queue = queue.Queue()

        # UI Variables
        self.path_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.progress_var = tk.IntVar(value=0)
        self.progress_message_var = tk.StringVar(value="Ready to install")

        # Build UI and show
        self.build_ui()
        self.load_last_directory()
        self.show()

    def build_ui(self):
        """
        Build dialog user interface.

        Layout:
        - Instructions label
        - Directory selection frame
        - Validation status
        - Progress frame (initially hidden)
        - Button frame

        See implementation_plan.md Section 2.2 for detailed layout.
        """
        pass

    def browse_directory(self):
        """
        Open directory picker dialog.

        Updates path_var with selected directory.
        Triggers validation automatically via path_var trace.
        """
        pass

    def validate_directory(self):
        """
        Validate selected directory and update UI.

        Called automatically when path_var changes.

        Updates:
        - status_var: Validation result message
        - install_button state: Enabled if valid
        - status color: Green/red/orange based on validation

        Validation Checks:
        - Directory exists
        - Directory is writable
        - Directory is not system directory
        - Check for existing .claude folder
        """
        pass

    def start_installation(self):
        """
        Begin installation in background thread.

        Flow:
        1. Create CMATInstaller instance
        2. Check for existing installation
        3. Confirm overwrite if needed
        4. Start background thread
        5. Begin polling for results
        6. Update UI state to INSTALLING
        """
        pass

    def update_progress(self, message: str, percent: int):
        """
        Update progress bar and message.

        Thread-safe: Can be called from background thread.
        Marshals UI updates to main thread using dialog.after().

        Args:
            message: Progress message to display
            percent: Progress percentage (0-100)
        """
        pass

    def on_installation_complete(self, success: bool):
        """
        Handle installation completion.

        Args:
            success: True if installation succeeded

        Actions:
        - Show success/error dialog
        - Clean up background thread
        - Reset UI state
        - Close dialog if user connects
        """
        pass

    def show_success_dialog(self):
        """
        Show success message with connect option.

        Dialog includes:
        - Success message
        - Installation location
        - "Connect Now" button
        - "Close" button

        If user clicks "Connect Now":
        - Close installation dialog
        - Return result with connect=True and cmat_script path
        """
        pass

    def handle_error(self, error: Exception):
        """
        Display error message to user.

        Args:
            error: Exception that occurred

        Maps exception types to user-friendly messages.
        Shows retry suggestion where appropriate.
        """
        pass
```

---

## 3. Exception Hierarchy

```python
"""
Exception hierarchy for CMAT installer.
"""


class CMATInstallerError(Exception):
    """
    Base exception for all CMAT installer errors.

    Attributes:
        message: Error message
        user_message: User-friendly error message (optional)
    """

    def __init__(self, message: str, user_message: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.user_message = user_message or message


class SecurityError(CMATInstallerError):
    """
    Security validation failed.

    Raised when:
    - System directory detected
    - ZIP contains directory traversal
    - Non-HTTPS URL detected
    - Path validation fails
    """
    pass


class NetworkError(CMATInstallerError):
    """
    Network operation failed.

    Raised when:
    - Connection timeout
    - DNS resolution failure
    - HTTP error response (404, 500, etc.)
    - SSL certificate error
    - Download incomplete
    """
    pass


class ValidationError(CMATInstallerError):
    """
    Installation validation failed.

    Raised when:
    - Required files missing
    - Invalid directory structure
    - Corrupted ZIP file
    - Template version mismatch
    """
    pass


class FileSystemError(CMATInstallerError):
    """
    File system operation failed.

    Raised when:
    - Permission denied
    - Disk full
    - Path too long
    - File system read-only
    """
    pass


# Usage Example:
try:
    installer.install()
except SecurityError as e:
    messagebox.showerror("Security Error", e.user_message or e.message)
except NetworkError as e:
    messagebox.showerror("Network Error", e.user_message or e.message)
except ValidationError as e:
    messagebox.showerror("Validation Error", e.user_message or e.message)
except CMATInstallerError as e:
    messagebox.showerror("Installation Error", e.user_message or e.message)
```

---

## 4. Progress Callback Protocol

```python
"""
Progress callback protocol for installation tracking.
"""

from typing import Protocol, Callable


class ProgressCallback(Protocol):
    """
    Protocol for progress callbacks.

    Implementers receive progress updates during installation.
    """

    def __call__(self, message: str, percent: int) -> None:
        """
        Called to report installation progress.

        Args:
            message: Human-readable progress message
            percent: Progress percentage (0-100)

        Example:
            >>> def my_progress(message: str, percent: int):
            ...     print(f"[{percent:3d}%] {message}")
            >>>
            >>> installer.install(progress_callback=my_progress)
        """
        ...


# Type alias for convenience
ProgressCallbackType = Callable[[str, int], None]


# Progress milestones (documented in implementation_plan.md):
PROGRESS_MILESTONES = {
    0: "Initializing installation...",
    5: "Backing up existing installation...",
    10: "Downloading template from GitHub...",
    30: "Download complete, extracting...",
    70: "Validating installation...",
    90: "Finalizing installation...",
    100: "Installation complete!",
}
```

---

## 5. Settings Extension API

```python
"""
Extension to Settings class for CMAT installer.

Add these methods to src/settings.py
"""


def get_last_install_directory(self) -> Optional[str]:
    """
    Get the last used CMAT installation directory.

    Returns:
        Path to last install directory or None if not set

    Example:
        >>> settings = Settings()
        >>> last_dir = settings.get_last_install_directory()
        >>> if last_dir:
        ...     print(f"Last installed to: {last_dir}")
    """
    return self._data.get('last_install_directory')


def set_last_install_directory(self, path: str):
    """
    Set the last used CMAT installation directory.

    Args:
        path: Path to directory (should be absolute)

    Example:
        >>> settings = Settings()
        >>> settings.set_last_install_directory("/home/user/project")
    """
    self._data['last_install_directory'] = path
    self._save()


def clear_last_install_directory(self):
    """
    Clear the last install directory.

    Example:
        >>> settings = Settings()
        >>> settings.clear_last_install_directory()
    """
    if 'last_install_directory' in self._data:
        del self._data['last_install_directory']
        self._save()
```

---

## 6. Code Examples

### 6.1 Basic Installation

```python
from pathlib import Path
from installers.cmat_installer import CMATInstaller


def install_cmat(target_dir: str):
    """Simple installation example."""

    installer = CMATInstaller(
        target_directory=Path(target_dir),
        github_owner="anthropics",
        github_repo="ClaudeMultiAgentTemplate",
        github_branch="main"
    )

    # Validate directory
    is_valid, error = installer.validate_target_directory()
    if not is_valid:
        print(f"Error: {error}")
        return False

    # Check for existing installation
    if installer.check_existing_installation():
        print("Warning: .claude already exists")
        overwrite = input("Overwrite? (y/n): ").lower() == 'y'
        if not overwrite:
            return False
    else:
        overwrite = False

    # Install with progress
    def progress(msg, pct):
        print(f"[{pct:3d}%] {msg}")

    try:
        success = installer.install(
            progress_callback=progress,
            overwrite=overwrite
        )
        print("Installation succeeded!" if success else "Installation failed.")
        return success
    except Exception as e:
        print(f"Error: {e}")
        return False


# Usage:
install_cmat("/home/user/myproject")
```

### 6.2 Dialog Integration

```python
from dialogs.install_cmat import InstallCMATDialog


def show_installer(parent_window):
    """Show installer dialog and handle result."""

    result = InstallCMATDialog(parent_window).result

    if result and result.get("success"):
        if result.get("connect"):
            # User wants to connect to installed project
            cmat_script = result["cmat_script"]
            print(f"Connecting to: {cmat_script}")
            # ... connection logic ...
        else:
            print("Installation completed, user declined connection")
    else:
        print("Installation cancelled or failed")
```

### 6.3 Thread-Safe Progress Updates

```python
import tkinter as tk
from tkinter import ttk
import threading
import queue


class ProgressDialog:
    """Example of thread-safe progress updates."""

    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.progress_var = tk.IntVar(value=0)
        self.message_var = tk.StringVar(value="Starting...")

        # Progress bar
        self.progress = ttk.Progressbar(
            self.dialog,
            variable=self.progress_var,
            maximum=100
        )
        self.progress.pack(fill="x", padx=20, pady=10)

        # Message label
        self.label = ttk.Label(
            self.dialog,
            textvariable=self.message_var
        )
        self.label.pack(padx=20, pady=10)

        # Result queue
        self.result_queue = queue.Queue()

    def progress_callback(self, message: str, percent: int):
        """Thread-safe progress callback."""
        # Schedule UI update on main thread
        self.dialog.after(0, self._update_ui, message, percent)

    def _update_ui(self, message: str, percent: int):
        """Update UI (must run on main thread)."""
        self.progress_var.set(percent)
        self.message_var.set(message)
        self.dialog.update_idletasks()

    def run_installation(self, installer):
        """Run installation in background thread."""

        def install_thread():
            try:
                installer.install(progress_callback=self.progress_callback)
                self.result_queue.put(("success", None))
            except Exception as e:
                self.result_queue.put(("error", e))

        thread = threading.Thread(target=install_thread, daemon=True)
        thread.start()

        # Poll for result
        self._poll_result()

    def _poll_result(self):
        """Poll result queue (runs on main thread)."""
        try:
            result_type, data = self.result_queue.get_nowait()
            if result_type == "success":
                print("Installation succeeded!")
            elif result_type == "error":
                print(f"Installation failed: {data}")
        except queue.Empty:
            # Not done yet, poll again
            self.dialog.after(100, self._poll_result)
```

### 6.4 Error Handling

```python
from installers.cmat_installer import (
    CMATInstaller,
    SecurityError,
    NetworkError,
    ValidationError,
    FileSystemError
)


def safe_install(target_dir: str) -> bool:
    """Installation with comprehensive error handling."""

    installer = CMATInstaller(target_directory=Path(target_dir))

    try:
        return installer.install()

    except SecurityError as e:
        print(f"SECURITY ERROR: {e.message}")
        print("Installation aborted for your protection.")
        print(f"Details: {e.user_message}")
        return False

    except NetworkError as e:
        print(f"NETWORK ERROR: {e.message}")
        print("Please check your internet connection and try again.")
        print(f"Details: {e.user_message}")
        return False

    except ValidationError as e:
        print(f"VALIDATION ERROR: {e.message}")
        print("The template structure is invalid or corrupted.")
        print(f"Details: {e.user_message}")
        return False

    except FileSystemError as e:
        print(f"FILE SYSTEM ERROR: {e.message}")
        print("Please check permissions and disk space.")
        print(f"Details: {e.user_message}")
        return False

    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        print("Please report this issue to the developers.")
        return False
```

### 6.5 Custom Progress Display

```python
class FancyProgressDisplay:
    """Custom progress display with multiple progress bars."""

    def __init__(self):
        self.current_stage = None
        self.stages = {
            "download": {"start": 0, "end": 30, "label": "Download"},
            "extract": {"start": 30, "end": 70, "label": "Extract"},
            "validate": {"start": 70, "end": 90, "label": "Validate"},
            "finalize": {"start": 90, "end": 100, "label": "Finalize"},
        }

    def __call__(self, message: str, percent: int):
        """Progress callback."""
        # Determine current stage
        stage = self._get_stage(percent)

        if stage != self.current_stage:
            # New stage started
            self.current_stage = stage
            print(f"\n=== {self.stages[stage]['label']} ===")

        # Calculate stage-specific progress
        stage_info = self.stages[stage]
        stage_percent = (
            (percent - stage_info["start"]) /
            (stage_info["end"] - stage_info["start"]) * 100
        )

        # Display progress bar
        bar_length = 40
        filled = int(bar_length * stage_percent / 100)
        bar = "█" * filled + "░" * (bar_length - filled)

        print(f"\r[{bar}] {stage_percent:5.1f}% - {message}", end="", flush=True)

    def _get_stage(self, percent: int) -> str:
        """Determine current stage from overall percent."""
        for stage, info in self.stages.items():
            if info["start"] <= percent < info["end"]:
                return stage
        return "finalize"  # 100%


# Usage:
installer.install(progress_callback=FancyProgressDisplay())
```

---

## 7. Testing Utilities

### 7.1 Mock Installer for UI Testing

```python
class MockCMATInstaller:
    """Mock installer for UI testing without network access."""

    def __init__(self, target_directory: Path, **kwargs):
        self.target_directory = target_directory
        self.should_fail = False
        self.fail_at_percent = None

    def install(self, progress_callback=None, overwrite=False):
        """Simulate installation with controllable behavior."""
        import time

        stages = [
            (0, "Initializing..."),
            (10, "Downloading..."),
            (30, "Extracting..."),
            (70, "Validating..."),
            (90, "Finalizing..."),
            (100, "Complete!"),
        ]

        for percent, message in stages:
            if progress_callback:
                progress_callback(message, percent)

            # Simulate work
            time.sleep(0.2)

            # Simulate failure if configured
            if self.should_fail and percent >= (self.fail_at_percent or 50):
                raise NetworkError("Simulated network failure")

        return True

    def validate_target_directory(self):
        """Always valid for testing."""
        return (True, None)

    def check_existing_installation(self):
        """Check if .claude exists."""
        return (self.target_directory / ".claude").exists()
```

### 7.2 Test Fixtures

```python
import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_project_dir():
    """Create temporary project directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_github_zip():
    """Create mock GitHub ZIP for testing."""
    import zipfile

    # Create temp ZIP
    zip_path = Path(tempfile.mktemp(suffix=".zip"))

    with zipfile.ZipFile(zip_path, 'w') as zf:
        # Add mock CMAT structure
        zf.writestr("repo-main/.claude/scripts/cmat.sh", "#!/bin/bash\necho 'cmat'")
        zf.writestr("repo-main/.claude/AGENT_CONTRACTS.json", "{}")
        zf.writestr("repo-main/.claude/skills/skills.json", "{}")

    yield zip_path

    zip_path.unlink(missing_ok=True)


@pytest.fixture
def installer(temp_project_dir):
    """Create installer instance."""
    return CMATInstaller(
        target_directory=temp_project_dir,
        github_owner="test",
        github_repo="test",
        github_branch="main"
    )
```

---

## 8. Integration Examples

### 8.1 Menu Integration (main.py)

```python
# In MainWindow.build_menu_bar():

def build_menu_bar(self):
    """Build menu bar with CMAT installer."""
    menubar = tk.Menu(self.root)
    self.root.config(menu=menubar)

    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)

    file_menu.add_command(
        label="Connect...",
        command=self.show_connect_dialog,
        accelerator="Ctrl+O"
    )

    # NEW: CMAT Installer
    file_menu.add_command(
        label="Install CMAT...",
        command=self.show_install_cmat_dialog
    )

    file_menu.add_separator()
    file_menu.add_command(
        label="Quit",
        command=self.quit_app,
        accelerator="Ctrl+Q"
    )


def show_install_cmat_dialog(self):
    """Show CMAT installer dialog."""
    from .dialogs.install_cmat import InstallCMATDialog

    result = InstallCMATDialog(self.root).result

    if result and result.get("success"):
        if result.get("connect"):
            # User wants to connect to installed project
            cmat_script = result["cmat_script"]

            # Use existing connection logic
            try:
                self.connect_to_queue(cmat_script)
                messagebox.showinfo(
                    "Connected",
                    f"Successfully connected to project:\n{cmat_script}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Connection Failed",
                    f"Could not connect to project:\n{str(e)}"
                )
```

### 8.2 Settings Integration (settings.py)

```python
# Add to Settings class:

# =============================================================================
# CMAT Installer Settings
# =============================================================================

def get_last_install_directory(self) -> Optional[str]:
    """Get the last used CMAT installation directory."""
    return self._data.get('last_install_directory')

def set_last_install_directory(self, path: str):
    """Set the last used CMAT installation directory."""
    self._data['last_install_directory'] = path
    self._save()

def clear_last_install_directory(self):
    """Clear the last install directory."""
    if 'last_install_directory' in self._data:
        del self._data['last_install_directory']
        self._save()
```

---

**End of API Specifications**

This document provides complete API specifications for implementing the CMAT Template Installer. Refer to `implementation_plan.md` for architecture and implementation sequence.
