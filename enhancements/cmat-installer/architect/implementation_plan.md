---
enhancement: cmat-installer
agent: architect
task_id: task_1762445530_49766
timestamp: 2025-11-06T08:00:00Z
status: READY_FOR_IMPLEMENTATION
---

# Implementation Plan: CMAT Template Installer

## Executive Summary

This document provides the complete architecture, technical specifications, and step-by-step implementation guidance for the CMAT Template Installer feature. The feature enables one-click installation of the Claude Multi-Agent Template v3.0 structure from GitHub into user-selected directories.

**Architecture Overview:**
- **UI Layer:** `InstallCMATDialog` (tkinter, inherits from `BaseDialog`)
- **Business Logic Layer:** `CMATInstaller` (download, extract, validate)
- **Infrastructure Layer:** Python standard library only (urllib, zipfile, pathlib, threading)

**Key Design Principles:**
- **Security First:** Multi-layer path validation and directory traversal prevention
- **Atomic Operations:** All-or-nothing installation with automatic rollback
- **Responsive UI:** Background threading for network/disk operations
- **Clear Feedback:** Progress tracking and comprehensive error handling

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Component Specifications](#2-component-specifications)
3. [Data Flow Architecture](#3-data-flow-architecture)
4. [Security Architecture](#4-security-architecture)
5. [Threading Architecture](#5-threading-architecture)
6. [Error Handling Strategy](#6-error-handling-strategy)
7. [Integration Points](#7-integration-points)
8. [Implementation Sequence](#8-implementation-sequence)
9. [Testing Strategy](#9-testing-strategy)
10. [Configuration and Constants](#10-configuration-and-constants)

---

## 1. System Architecture

### 1.1 Architectural Pattern

**Pattern:** Layered Architecture with MVC influences

```
┌─────────────────────────────────────────────────────────────┐
│                        UI Layer                             │
│  InstallCMATDialog (tkinter + BaseDialog)                   │
│  - User interaction                                         │
│  - Progress display                                         │
│  - Error presentation                                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ (delegates to)
                 ↓
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                      │
│  CMATInstaller                                              │
│  - download_template()                                      │
│  - extract_template()                                       │
│  - validate_installation()                                  │
│  - rollback_installation()                                  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ (uses)
                 ↓
┌─────────────────────────────────────────────────────────────┐
│               Infrastructure Layer                          │
│  Standard Library Components                                │
│  - urllib.request (HTTP downloads)                          │
│  - zipfile (ZIP extraction)                                 │
│  - pathlib (Path operations)                                │
│  - threading (Background operations)                        │
│  - shutil (File operations)                                 │
└─────────────────────────────────────────────────────────────┘
```

**Rationale:**
- **Separation of Concerns:** UI, business logic, and infrastructure are clearly separated
- **Testability:** Each layer can be tested independently
- **Maintainability:** Changes to one layer don't cascade to others
- **Consistency:** Follows existing codebase patterns (see `ConnectDialog`, `EnhancementCreateDialog`)

### 1.2 Module Organization

**New Files to Create:**

```
src/
├── dialogs/
│   └── install_cmat.py          # NEW - InstallCMATDialog class
└── installers/                   # NEW - Business logic layer
    ├── __init__.py               # NEW - Package initialization
    └── cmat_installer.py         # NEW - CMATInstaller class
```

**Files to Modify:**

```
src/
├── main.py                       # Add menu item at line ~113
└── settings.py                   # Add last_install_directory methods
```

**Rationale:**
- **New Package `installers/`:** Separates installation logic from UI, enables reuse
- **Dialog in `dialogs/`:** Follows existing pattern for all dialog classes
- **Minimal Changes:** Only 2 files modified, reduces integration risk

---

## 2. Component Specifications

### 2.1 CMATInstaller Class

**File:** `src/installers/cmat_installer.py`

**Purpose:** Core business logic for downloading, extracting, and validating CMAT template

**Public API:**

```python
class CMATInstaller:
    """
    Installer for Claude Multi-Agent Template (CMAT) v3.0.

    Handles download from GitHub, extraction to target directory,
    validation of installation, and rollback on failure.
    """

    def __init__(self,
                 target_directory: Path,
                 github_owner: str = "anthropics",
                 github_repo: str = "ClaudeMultiAgentTemplate",
                 github_branch: str = "main"):
        """
        Initialize installer.

        Args:
            target_directory: Directory where .claude/ will be installed
            github_owner: GitHub repository owner
            github_repo: GitHub repository name
            github_branch: Branch to download from

        Raises:
            ValueError: If target_directory is invalid
        """

    def install(self,
                progress_callback: Optional[Callable[[str, int], None]] = None,
                overwrite: bool = False) -> bool:
        """
        Perform complete installation: download → extract → validate.

        Args:
            progress_callback: Optional callback(message: str, percent: int)
            overwrite: Whether to overwrite existing .claude folder

        Returns:
            True if installation successful, False otherwise

        Raises:
            InstallationError: If installation fails
            SecurityError: If security validation fails
        """

    def validate_target_directory(self) -> Tuple[bool, Optional[str]]:
        """
        Validate target directory is safe and writable.

        Returns:
            (is_valid, error_message) tuple
        """

    def check_existing_installation(self) -> bool:
        """
        Check if .claude folder already exists.

        Returns:
            True if .claude exists, False otherwise
        """
```

**Private Methods:**

```python
def _download_zip(self, progress_callback) -> Path:
    """Download ZIP from GitHub to temp directory."""

def _extract_zip(self, zip_path: Path, progress_callback) -> Path:
    """Extract .claude folder from ZIP to temp directory."""

def _validate_structure(self, extracted_path: Path) -> bool:
    """Validate extracted .claude folder has v3.0 structure."""

def _move_to_target(self, temp_path: Path) -> None:
    """Atomically move .claude from temp to target."""

def _backup_existing(self) -> Optional[Path]:
    """Backup existing .claude folder if present."""

def _rollback(self, backup_path: Optional[Path]) -> None:
    """Restore from backup on failure."""

def _cleanup_temp(self, temp_dir: Path) -> None:
    """Clean up temporary files."""

def _validate_zip_entry(self, zip_entry_name: str) -> bool:
    """Validate ZIP entry for directory traversal attacks."""

def _is_system_directory(self, path: Path) -> bool:
    """Check if path is a system directory."""
```

**Exception Hierarchy:**

```python
class CMATInstallerError(Exception):
    """Base exception for installer errors."""
    pass

class SecurityError(CMATInstallerError):
    """Security validation failed."""
    pass

class NetworkError(CMATInstallerError):
    """Network operation failed."""
    pass

class ValidationError(CMATInstallerError):
    """Installation validation failed."""
    pass
```

**State Management:**

```python
class InstallationState:
    """Track installation state for cleanup/rollback."""

    temp_dir: Optional[Path] = None
    zip_path: Optional[Path] = None
    backup_path: Optional[Path] = None
    extracted_path: Optional[Path] = None
```

### 2.2 InstallCMATDialog Class

**File:** `src/dialogs/install_cmat.py`

**Purpose:** User interface for CMAT installation

**Class Structure:**

```python
class InstallCMATDialog(BaseDialog):
    """
    Dialog for installing CMAT template from GitHub.

    Provides:
    - Directory selection
    - Progress tracking
    - Error handling
    - Success confirmation with auto-connect option
    """

    def __init__(self, parent):
        """
        Initialize dialog.

        Args:
            parent: Parent window (MainWindow)
        """
        super().__init__(parent, "Install CMAT Template", 700, 500)
        self.installer: Optional[CMATInstaller] = None
        self.installation_thread: Optional[threading.Thread] = None
        self.build_ui()
        self.load_last_directory()
        self.show()

    def build_ui(self):
        """Build dialog UI with directory selection and progress display."""

    def browse_directory(self):
        """Open directory picker dialog."""

    def validate_directory(self):
        """Validate selected directory and update UI."""

    def start_installation(self):
        """Begin installation in background thread."""

    def update_progress(self, message: str, percent: int):
        """Update progress bar and message (thread-safe)."""

    def on_installation_complete(self, success: bool):
        """Handle installation completion."""

    def show_success_dialog(self):
        """Show success message with connect option."""

    def handle_error(self, error: Exception):
        """Display error message to user."""
```

**UI Components:**

```
┌─────────────────────────────────────────────────────────┐
│  Install CMAT Template                            [X]   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Select the directory where you want to install the    │
│  CMAT template. A .claude/ folder will be created.     │
│                                                         │
│  ┌─ Installation Directory ─────────────────────────┐  │
│  │  Path: [/home/user/myproject        ] [Browse] │  │
│  │                                                   │  │
│  │  Status: ✓ Valid directory                      │  │
│  │  Note: A .claude/ folder will be created here   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─ Installation Progress ──────────────────────────┐  │
│  │  [████████░░░░░░░░░░░░░░░░░░░░░░░░░░] 30%       │  │
│  │  Downloading template from GitHub...             │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│              [Install]  [Cancel]                        │
└─────────────────────────────────────────────────────────┘
```

**State Machine:**

```
States:
- SELECTING: User selecting directory
- VALIDATING: Validating directory
- READY: Ready to install
- INSTALLING: Installation in progress
- COMPLETED: Installation succeeded
- FAILED: Installation failed

Transitions:
SELECTING → VALIDATING (on directory change)
VALIDATING → READY (if valid) | SELECTING (if invalid)
READY → INSTALLING (on Install button click)
INSTALLING → COMPLETED (on success) | FAILED (on error)
COMPLETED → CLOSED (on OK or Connect)
FAILED → SELECTING (on OK, allows retry)
```

---

## 3. Data Flow Architecture

### 3.1 Installation Flow

```
User Action: Click "Install CMAT..." menu
     ↓
1. InstallCMATDialog opens
     ↓
2. Load last_install_directory from Settings
     ↓
3. User selects/validates directory
     ↓
4. User clicks "Install"
     ↓
5. Create CMATInstaller instance
     ↓
6. Start background thread
     ↓
7. CMATInstaller.install() executes:
   ├─ Download ZIP from GitHub
   │  └─ Progress: 0-30%
   ├─ Extract .claude folder
   │  └─ Progress: 30-70%
   ├─ Validate structure
   │  └─ Progress: 70-90%
   └─ Move to target
      └─ Progress: 90-100%
     ↓
8. Update UI via thread-safe callback
     ↓
9. On completion:
   ├─ Success → Show success dialog + connect option
   └─ Failure → Show error dialog + cleanup
```

### 3.2 Progress Callback Protocol

**Interface:**

```python
ProgressCallback = Callable[[str, int], None]
# Args: (message: str, percent: int)
```

**Thread Safety:**

```python
def update_progress(self, message: str, percent: int):
    """Thread-safe progress update."""
    # Use root.after() to marshal call to main thread
    self.dialog.after(0, self._update_progress_ui, message, percent)

def _update_progress_ui(self, message: str, percent: int):
    """Update UI components (runs on main thread)."""
    self.progress_var.set(percent)
    self.progress_label.config(text=message)
```

**Progress Milestones:**

| Percent | Stage | Message |
|---------|-------|---------|
| 0% | Start | "Initializing installation..." |
| 10% | Download Start | "Downloading template from GitHub..." |
| 30% | Download Complete | "Download complete, extracting..." |
| 70% | Extract Complete | "Validating installation..." |
| 90% | Validation Complete | "Finalizing installation..." |
| 100% | Complete | "Installation complete!" |

### 3.3 Error Propagation

```
Error occurs in CMATInstaller
     ↓
Raise specific exception (NetworkError, ValidationError, etc.)
     ↓
Caught by background thread
     ↓
Posted to main thread via queue or callback
     ↓
InstallCMATDialog.handle_error()
     ↓
Show user-friendly error dialog
     ↓
Clean up partial installation
     ↓
Return to SELECTING state
```

---

## 4. Security Architecture

### 4.1 Path Validation

**System Directory Blacklist:**

```python
SYSTEM_DIRECTORIES = {
    # Unix/Linux/macOS
    "/usr", "/bin", "/sbin", "/etc", "/var", "/tmp", "/boot",
    "/dev", "/proc", "/sys", "/System", "/Library",
    # Windows
    "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
    "C:\\ProgramData", "C:\\System32",
}

def _is_system_directory(self, path: Path) -> bool:
    """
    Check if path is or is within a system directory.

    Uses case-insensitive matching and checks parent hierarchy.
    """
    resolved = path.resolve()
    path_str = str(resolved)

    for sys_dir in SYSTEM_DIRECTORIES:
        # Case-insensitive prefix matching
        if path_str.lower().startswith(sys_dir.lower()):
            return True

    return False
```

**Writability Check:**

```python
def _check_writable(self, path: Path) -> bool:
    """
    Test if directory is writable.

    Creates and removes a test file to verify permissions.
    """
    test_file = path / f".write_test_{uuid.uuid4()}"
    try:
        test_file.touch()
        test_file.unlink()
        return True
    except (OSError, PermissionError):
        return False
```

### 4.2 ZIP Security

**Directory Traversal Prevention:**

```python
def _validate_zip_entry(self, zip_entry_name: str) -> bool:
    """
    Validate ZIP entry doesn't contain directory traversal.

    Rejects entries with:
    - ".." components
    - Absolute paths
    - Symlinks (if detected)

    Returns:
        True if safe, False if dangerous
    """
    # Normalize path
    normalized = os.path.normpath(zip_entry_name)

    # Check for directory traversal
    if ".." in normalized.split(os.sep):
        return False

    # Check for absolute path
    if os.path.isabs(normalized):
        return False

    # Check for suspicious characters (Windows)
    if any(char in normalized for char in ['<', '>', ':', '"', '|', '?', '*']):
        return False

    return True
```

**Safe Extraction:**

```python
def _extract_zip(self, zip_path: Path, progress_callback) -> Path:
    """
    Safely extract ZIP to temp directory.

    Validates every entry before extraction.
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="cmat_install_"))

    with zipfile.ZipFile(zip_path, 'r') as zf:
        for member in zf.namelist():
            # Security validation
            if not self._validate_zip_entry(member):
                raise SecurityError(
                    f"ZIP contains unsafe entry: {member}"
                )

            # Extract to temp directory
            zf.extract(member, temp_dir)

    return temp_dir
```

### 4.3 Download Security

**HTTPS Enforcement:**

```python
def _download_zip(self, progress_callback) -> Path:
    """
    Download ZIP from GitHub over HTTPS.

    Enforces HTTPS, validates SSL certificates.
    """
    url = f"https://github.com/{self.owner}/{self.repo}/archive/refs/heads/{self.branch}.zip"

    # Ensure HTTPS
    if not url.startswith("https://"):
        raise SecurityError("Only HTTPS downloads are allowed")

    # Create context with certificate verification
    context = ssl.create_default_context()

    # Download with timeout
    request = urllib.request.Request(url)
    with urllib.request.urlopen(request, timeout=30, context=context) as response:
        # ... download logic ...
```

---

## 5. Threading Architecture

### 5.1 Thread Model

**Main Thread Responsibilities:**
- UI event handling
- User interaction
- Progress display updates
- Error dialog display

**Background Thread Responsibilities:**
- HTTP download (blocking I/O)
- ZIP extraction (disk I/O)
- File validation (disk I/O)
- File moving (disk I/O)

### 5.2 Thread Communication

**Using Queue for Results:**

```python
class InstallCMATDialog(BaseDialog):
    def __init__(self, parent):
        super().__init__(parent, "Install CMAT Template", 700, 500)
        self.result_queue = queue.Queue()
        # ... rest of init ...

    def start_installation(self):
        """Start installation in background thread."""
        self.installation_thread = threading.Thread(
            target=self._run_installation,
            daemon=True
        )
        self.installation_thread.start()

        # Start polling for results
        self._poll_installation_result()

    def _run_installation(self):
        """Run in background thread."""
        try:
            self.installer.install(progress_callback=self._progress_callback)
            self.result_queue.put(("success", None))
        except Exception as e:
            self.result_queue.put(("error", e))

    def _poll_installation_result(self):
        """Poll queue for installation result (runs on main thread)."""
        try:
            result_type, data = self.result_queue.get_nowait()
            if result_type == "success":
                self.on_installation_complete(True)
            elif result_type == "error":
                self.handle_error(data)
        except queue.Empty:
            # Not done yet, poll again
            self.dialog.after(100, self._poll_installation_result)
```

### 5.3 Progress Updates

**Thread-Safe Progress Callback:**

```python
def _progress_callback(self, message: str, percent: int):
    """
    Progress callback invoked from background thread.

    Marshals update to main thread using dialog.after().
    """
    # Schedule UI update on main thread
    self.dialog.after(0, self._update_progress_ui, message, percent)

def _update_progress_ui(self, message: str, percent: int):
    """
    Update progress UI components.

    MUST be called from main thread only.
    """
    self.progress_var.set(percent)
    self.progress_label.config(text=message)
    self.dialog.update_idletasks()
```

---

## 6. Error Handling Strategy

### 6.1 Error Categories

**Network Errors:**
- Connection timeout
- DNS resolution failure
- HTTP errors (404, 500, etc.)
- SSL certificate errors
- Incomplete download

**File System Errors:**
- Permission denied
- Disk full
- Path too long (Windows)
- Invalid characters in path
- File system read-only

**Validation Errors:**
- Missing required files
- Invalid directory structure
- Corrupted ZIP file
- Security validation failure

**User Errors:**
- Invalid directory selected
- Overwrite without confirmation
- Cancellation during installation

### 6.2 Error Messages

**User-Friendly Messages:**

```python
ERROR_MESSAGES = {
    # Network errors
    "timeout": (
        "Installation Failed: Connection Timeout",
        "Could not connect to GitHub. Please check your internet "
        "connection and try again."
    ),
    "dns_error": (
        "Installation Failed: Cannot Reach GitHub",
        "Could not resolve github.com. Please check your internet "
        "connection and DNS settings."
    ),
    "http_404": (
        "Installation Failed: Template Not Found",
        "The CMAT template repository could not be found. This may be "
        "a temporary issue with GitHub. Please try again later."
    ),

    # File system errors
    "permission_denied": (
        "Installation Failed: Permission Denied",
        "You don't have permission to write to the selected directory. "
        "Please choose a different location or contact your system "
        "administrator."
    ),
    "disk_full": (
        "Installation Failed: Disk Full",
        "There is not enough space on the disk to install CMAT. "
        "Please free up space and try again. Required: ~10 MB"
    ),

    # Validation errors
    "invalid_structure": (
        "Installation Failed: Invalid Template",
        "The downloaded template does not have the expected structure. "
        "This may indicate a problem with the template repository."
    ),
    "security_error": (
        "Installation Failed: Security Check Failed",
        "The template failed security validation. Installation has been "
        "aborted to protect your system."
    ),
}
```

### 6.3 Cleanup on Error

**Automatic Rollback:**

```python
def install(self, progress_callback, overwrite):
    """Install with automatic cleanup on error."""
    state = InstallationState()

    try:
        # Backup existing installation
        if overwrite and self.check_existing_installation():
            state.backup_path = self._backup_existing()
            progress_callback("Backing up existing installation...", 5)

        # Download
        state.temp_dir = Path(tempfile.mkdtemp(prefix="cmat_install_"))
        state.zip_path = self._download_zip(progress_callback)

        # Extract
        state.extracted_path = self._extract_zip(state.zip_path, progress_callback)

        # Validate
        if not self._validate_structure(state.extracted_path):
            raise ValidationError("Invalid template structure")

        # Move to target (atomic)
        self._move_to_target(state.extracted_path)

        # Success - cleanup temp files
        self._cleanup_temp(state.temp_dir)
        return True

    except Exception as e:
        # Rollback on any error
        self._rollback(state)
        raise
```

---

## 7. Integration Points

### 7.1 Menu Integration

**File:** `src/main.py`

**Location:** Line ~113 (after "Connect...")

**Change:**

```python
# File menu
file_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Connect...", command=self.show_connect_dialog, accelerator="Ctrl+O")
# NEW: Add Install CMAT menu item
file_menu.add_command(label="Install CMAT...", command=self.show_install_cmat_dialog)
file_menu.add_separator()
file_menu.add_command(label="Quit", command=self.quit_app, accelerator="Ctrl+Q")
```

**New Method:**

```python
def show_install_cmat_dialog(self):
    """Show CMAT installer dialog."""
    from .dialogs.install_cmat import InstallCMATDialog

    result = InstallCMATDialog(self.root).result

    # If installation succeeded and user wants to connect
    if result and result.get("connect"):
        cmat_script = result["cmat_script"]
        # Use existing connection logic
        self.connect_to_queue(str(cmat_script))
```

### 7.2 Settings Integration

**File:** `src/settings.py`

**New Methods to Add:**

```python
def get_last_install_directory(self) -> Optional[str]:
    """Get the last used CMAT installation directory.

    Returns:
        Path to last install directory or None if not set
    """
    return self._data.get('last_install_directory')

def set_last_install_directory(self, path: str):
    """Set the last used CMAT installation directory.

    Args:
        path: Path to directory
    """
    self._data['last_install_directory'] = path
    self._save()

def clear_last_install_directory(self):
    """Clear the last install directory."""
    if 'last_install_directory' in self._data:
        del self._data['last_install_directory']
        self._save()
```

**Pattern:** Follow existing pattern for `last_queue_manager` methods (lines 61-82)

### 7.3 Connection Integration

**After Successful Installation:**

```python
def show_success_dialog(self):
    """Show success message with connect option."""
    installed_path = self.target_directory / ".claude"
    cmat_script = installed_path / "scripts" / "cmat.sh"

    # Show dialog with connect option
    dialog = tk.Toplevel(self.dialog)
    dialog.title("Installation Complete")
    # ... build success UI ...

    def connect_now():
        self.result = {
            "success": True,
            "connect": True,
            "cmat_script": str(cmat_script)
        }
        dialog.destroy()
        self.close(self.result)

    # Buttons: [Connect Now] [Close]
    connect_btn = ttk.Button(dialog, text="Connect Now", command=connect_now)
    close_btn = ttk.Button(dialog, text="Close", command=lambda: self.close({"success": True}))
```

---

## 8. Implementation Sequence

### Phase 1: Core Infrastructure (Priority 1)

**Step 1.1: Create CMATInstaller Class**
- **File:** `src/installers/cmat_installer.py`
- **Tasks:**
  - Create `CMATInstaller` class with `__init__`
  - Implement path validation methods
  - Implement system directory checking
  - Add exception classes

**Step 1.2: Implement Download Logic**
- **Tasks:**
  - Implement `_download_zip()` with progress tracking
  - Add timeout handling
  - Add HTTPS validation
  - Test with real GitHub URL

**Step 1.3: Implement Extraction Logic**
- **Tasks:**
  - Implement `_extract_zip()` with security validation
  - Add ZIP entry validation
  - Implement directory traversal prevention
  - Test with sample ZIP files

**Step 1.4: Implement Validation Logic**
- **Tasks:**
  - Implement `_validate_structure()`
  - Check for required v3.0 files:
    - `.claude/scripts/cmat.sh`
    - `.claude/AGENT_CONTRACTS.json`
    - `.claude/skills/skills.json`
  - Return clear validation errors

**Step 1.5: Implement Atomic Installation**
- **Tasks:**
  - Implement `_move_to_target()` with atomic operations
  - Implement `_backup_existing()`
  - Implement `_rollback()`
  - Implement `_cleanup_temp()`

**Step 1.6: Implement Main Install Method**
- **Tasks:**
  - Wire up all components in `install()` method
  - Add progress callbacks at each stage
  - Add comprehensive error handling
  - Test end-to-end flow

### Phase 2: User Interface (Priority 1)

**Step 2.1: Create InstallCMATDialog Skeleton**
- **File:** `src/dialogs/install_cmat.py`
- **Tasks:**
  - Create class inheriting from `BaseDialog`
  - Implement `__init__` and `build_ui()`
  - Create basic layout with placeholders

**Step 2.2: Implement Directory Selection**
- **Tasks:**
  - Add directory entry and browse button
  - Implement `browse_directory()` using `filedialog.askdirectory()`
  - Add path validation indicator
  - Connect to Settings for last directory

**Step 2.3: Implement Progress Display**
- **Tasks:**
  - Add progress bar (ttk.Progressbar)
  - Add progress message label
  - Implement thread-safe progress updates
  - Test progress animation

**Step 2.4: Implement Installation Flow**
- **Tasks:**
  - Add Install button with enable/disable logic
  - Implement `start_installation()` with threading
  - Implement result polling with queue
  - Add cancellation support

**Step 2.5: Implement Success/Error Dialogs**
- **Tasks:**
  - Create success dialog with connect option
  - Create error dialog with user-friendly messages
  - Map exception types to error messages
  - Test all error paths

### Phase 3: Integration (Priority 2)

**Step 3.1: Settings Integration**
- **File:** `src/settings.py`
- **Tasks:**
  - Add `get_last_install_directory()` method
  - Add `set_last_install_directory()` method
  - Add `clear_last_install_directory()` method
  - Test persistence across restarts

**Step 3.2: Menu Integration**
- **File:** `src/main.py`
- **Tasks:**
  - Add "Install CMAT..." menu item after "Connect..."
  - Implement `show_install_cmat_dialog()` method
  - Handle connection after installation
  - Test menu integration

**Step 3.3: Connection Flow**
- **Tasks:**
  - Pass installed cmat_script path to connection logic
  - Reuse existing `connect_to_queue()` method
  - Test end-to-end: install → connect → use

### Phase 4: Polish (Priority 3)

**Step 4.1: Error Message Refinement**
- **Tasks:**
  - Review all error messages for clarity
  - Add helpful suggestions to error messages
  - Test error scenarios with users

**Step 4.2: Progress Message Refinement**
- **Tasks:**
  - Add descriptive progress messages
  - Ensure progress bar moves smoothly
  - Add estimated time remaining (optional)

**Step 4.3: UI Polish**
- **Tasks:**
  - Add icons/symbols for validation status
  - Improve spacing and layout
  - Add tooltips for buttons
  - Test on all platforms (Windows, macOS, Linux)

---

## 9. Testing Strategy

### 9.1 Unit Tests

**Test File:** `tests/test_cmat_installer.py`

**Test Cases:**

```python
class TestCMATInstaller:
    """Unit tests for CMATInstaller class."""

    def test_validate_target_directory_valid(self):
        """Test validation of valid directory."""

    def test_validate_target_directory_system_dir(self):
        """Test rejection of system directories."""

    def test_validate_target_directory_not_writable(self):
        """Test rejection of non-writable directories."""

    def test_validate_zip_entry_safe(self):
        """Test validation of safe ZIP entries."""

    def test_validate_zip_entry_directory_traversal(self):
        """Test rejection of directory traversal attacks."""

    def test_validate_structure_valid_v3(self):
        """Test validation of valid v3.0 structure."""

    def test_validate_structure_missing_files(self):
        """Test rejection of incomplete structure."""

    def test_backup_and_rollback(self):
        """Test backup and rollback functionality."""
```

### 9.2 Integration Tests

**Test File:** `tests/test_install_cmat_integration.py`

**Test Cases:**

```python
class TestInstallCMATIntegration:
    """Integration tests for CMAT installation."""

    @pytest.mark.integration
    def test_full_installation_flow(self, tmp_path):
        """Test complete installation from mock ZIP."""

    @pytest.mark.integration
    def test_installation_with_existing_claude(self, tmp_path):
        """Test installation with overwrite."""

    @pytest.mark.integration
    def test_installation_failure_rollback(self, tmp_path):
        """Test rollback on installation failure."""

    @pytest.mark.integration
    def test_concurrent_installations(self, tmp_path):
        """Test multiple installations don't interfere."""
```

### 9.3 UI Tests

**Test File:** `tests/test_install_cmat_dialog.py`

**Test Cases:**

```python
class TestInstallCMATDialog:
    """UI tests for installation dialog."""

    def test_dialog_opens(self):
        """Test dialog opens and displays correctly."""

    def test_directory_selection(self):
        """Test directory browsing and selection."""

    def test_validation_updates_ui(self):
        """Test validation results update UI."""

    def test_progress_updates(self):
        """Test progress bar updates during installation."""

    def test_error_handling_ui(self):
        """Test error messages display correctly."""

    def test_success_dialog(self):
        """Test success dialog with connect option."""
```

### 9.4 Manual Testing

**Test Plan:**

1. **Happy Path:**
   - Install to empty directory
   - Verify all files present
   - Connect to installed project
   - Verify project works

2. **Overwrite Path:**
   - Install to directory with existing .claude
   - Confirm overwrite warning
   - Verify backup created
   - Verify successful overwrite

3. **Error Paths:**
   - Install to non-writable directory
   - Install to system directory
   - Simulate network failure
   - Simulate disk full
   - Cancel during installation

4. **Platform Testing:**
   - Test on Windows 10/11
   - Test on macOS 10.15+
   - Test on Ubuntu 20.04+

---

## 10. Configuration and Constants

### 10.1 GitHub Repository Configuration

**BLOCKER RESOLUTION REQUIRED:**

The requirements analysis identified a blocker: the actual GitHub repository URL must be confirmed before implementation.

**Recommended Configuration:**

```python
# src/installers/cmat_installer.py

# GitHub repository configuration
# TODO: CONFIRM ACTUAL REPOSITORY DETAILS BEFORE IMPLEMENTATION
DEFAULT_GITHUB_OWNER = "anthropics"  # ← NEEDS CONFIRMATION
DEFAULT_GITHUB_REPO = "ClaudeMultiAgentTemplate"  # ← NEEDS CONFIRMATION
DEFAULT_GITHUB_BRANCH = "main"  # ← VERIFY (main vs master vs v3)

# Alternative: Use environment variables for flexibility
GITHUB_OWNER = os.environ.get("CMAT_GITHUB_OWNER", "anthropics")
GITHUB_REPO = os.environ.get("CMAT_GITHUB_REPO", "ClaudeMultiAgentTemplate")
GITHUB_BRANCH = os.environ.get("CMAT_GITHUB_BRANCH", "main")
```

**Action Required:**
- Confirm actual GitHub repository owner/organization
- Confirm actual repository name
- Confirm branch name (main, master, or v3)
- Update constants before implementation begins

### 10.2 Validation Constants

```python
# Required files for CMAT v3.0 validation
REQUIRED_V3_FILES = [
    ".claude/scripts/cmat.sh",
    ".claude/AGENT_CONTRACTS.json",
    ".claude/skills/skills.json",
]

# Recommended files (warnings if missing)
RECOMMENDED_FILES = [
    ".claude/queues/task_queue.json",
    ".claude/agents/agents.json",
    ".claude/WORKFLOW_STATES.json",
]

# System directories to block (cross-platform)
SYSTEM_DIRECTORIES = {
    # Unix/Linux/macOS
    "/usr", "/bin", "/sbin", "/etc", "/var", "/tmp", "/boot",
    "/dev", "/proc", "/sys", "/System", "/Library",
    # Windows
    "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
    "C:\\ProgramData", "C:\\System32",
}
```

### 10.3 Timeout and Size Constants

```python
# Network timeouts
DOWNLOAD_TIMEOUT_SECONDS = 30
CONNECTION_TIMEOUT_SECONDS = 10

# Size limits
MAX_DOWNLOAD_SIZE_MB = 50
MIN_REQUIRED_DISK_SPACE_MB = 10

# Progress update frequency
PROGRESS_UPDATE_INTERVAL_MS = 100
```

### 10.4 UI Constants

```python
# Dialog dimensions
DIALOG_WIDTH = 700
DIALOG_HEIGHT = 500

# Progress bar
PROGRESS_BAR_LENGTH = 400
PROGRESS_BAR_MODE = "determinate"

# Colors
COLOR_SUCCESS = "green"
COLOR_ERROR = "red"
COLOR_WARNING = "orange"
COLOR_INFO = "blue"
```

---

## 11. File Structure Summary

### Files to Create

```
src/
├── installers/
│   ├── __init__.py                    # Package init (empty or re-exports)
│   └── cmat_installer.py              # CMATInstaller class (~400 lines)
└── dialogs/
    └── install_cmat.py                # InstallCMATDialog class (~350 lines)
```

### Files to Modify

```
src/
├── main.py                            # Add menu item + handler (~10 lines)
└── settings.py                        # Add 3 methods (~15 lines)
```

### Testing Files to Create

```
tests/
├── test_cmat_installer.py             # Unit tests (~200 lines)
├── test_install_cmat_integration.py   # Integration tests (~150 lines)
└── test_install_cmat_dialog.py        # UI tests (~100 lines)
```

**Total Estimated LOC:** ~1,225 lines (excluding comments/docstrings)

---

## 12. Implementation Checklist

### Pre-Implementation
- [ ] Confirm GitHub repository URL (BLOCKER)
- [ ] Decide on version strategy (main branch vs releases)
- [ ] Review and approve this implementation plan

### Phase 1: Core Infrastructure
- [ ] Create `src/installers/` package
- [ ] Implement `CMATInstaller.__init__` and validation methods
- [ ] Implement download logic with progress tracking
- [ ] Implement extraction with security validation
- [ ] Implement structure validation
- [ ] Implement atomic installation with rollback
- [ ] Write unit tests for CMATInstaller
- [ ] Test installer independently (without UI)

### Phase 2: User Interface
- [ ] Create `InstallCMATDialog` class
- [ ] Implement directory selection UI
- [ ] Implement progress display
- [ ] Implement threading and progress updates
- [ ] Implement success/error dialogs
- [ ] Write UI tests
- [ ] Test dialog independently (with mock installer)

### Phase 3: Integration
- [ ] Add Settings methods
- [ ] Add menu item to main.py
- [ ] Implement connection flow
- [ ] Write integration tests
- [ ] Test end-to-end flow

### Phase 4: Testing & Polish
- [ ] Manual testing on Windows
- [ ] Manual testing on macOS
- [ ] Manual testing on Linux
- [ ] Test all error scenarios
- [ ] Refine error messages
- [ ] Polish UI and progress messages
- [ ] Code review
- [ ] Documentation update

### Post-Implementation
- [ ] Update README.md with installation feature
- [ ] Create user guide/screenshots
- [ ] Update CHANGELOG
- [ ] Tag release

---

## 13. Risk Mitigation

### Critical Risks

**R1: Network Connectivity Failures**
- **Mitigation:** Timeout handling, clear error messages, automatic cleanup
- **Implementation:** Use urllib with timeouts, catch all network exceptions
- **Test:** Simulate network failures in integration tests

**R4: Directory Traversal in ZIP**
- **Mitigation:** Validate every ZIP entry before extraction
- **Implementation:** `_validate_zip_entry()` checks for ".." and absolute paths
- **Test:** Unit tests with malicious ZIP files

**R10: UI Unresponsive**
- **Mitigation:** Background threading for all blocking operations
- **Implementation:** Thread + queue pattern for installation
- **Test:** Manual testing with slow network

### High-Priority Risks

**R3: File Permission Errors**
- **Mitigation:** Pre-validation with test file write, clear error messages
- **Implementation:** `_check_writable()` before download starts
- **Test:** Manual testing with read-only directories

**R5: Incomplete Installations**
- **Mitigation:** Atomic operations with rollback on failure
- **Implementation:** Extract to temp → validate → move atomically
- **Test:** Integration tests with simulated failures

**R8: Install to System Directory**
- **Mitigation:** System directory blacklist with path resolution
- **Implementation:** `_is_system_directory()` with comprehensive list
- **Test:** Unit tests with system paths

---

## 14. Acceptance Criteria

### Functional Completeness

✅ **Menu Integration:**
- [ ] "Install CMAT..." menu item visible in File menu
- [ ] Menu item opens InstallCMATDialog when clicked
- [ ] Menu item positioned after "Connect..."

✅ **Directory Selection:**
- [ ] User can browse for target directory
- [ ] User can manually enter directory path
- [ ] Last-used directory is pre-populated
- [ ] Invalid directories are rejected with clear messages
- [ ] System directories are blocked

✅ **Installation Process:**
- [ ] Downloads CMAT template from GitHub
- [ ] Extracts .claude folder to target directory
- [ ] Validates installation has all required files
- [ ] Shows progress bar during installation
- [ ] Completes within 60 seconds on typical broadband

✅ **Security:**
- [ ] HTTPS-only downloads
- [ ] Directory traversal prevention
- [ ] System directory blocking
- [ ] All security validations pass

✅ **Error Handling:**
- [ ] Network errors handled with clear messages
- [ ] File system errors handled with clear messages
- [ ] Validation errors handled with clear messages
- [ ] All error paths clean up partial installations
- [ ] User can retry after error

✅ **Success Flow:**
- [ ] Success dialog displays on completion
- [ ] User can connect to installed project
- [ ] Connection works with newly installed project

### Non-Functional Requirements

✅ **Performance:**
- [ ] Installation completes in < 60 seconds (measured)
- [ ] UI remains responsive during installation
- [ ] Memory usage < 50 MB

✅ **Reliability:**
- [ ] 99%+ success rate with stable internet (measured)
- [ ] Safe to retry on failure
- [ ] No partial installations left on failure

✅ **Usability:**
- [ ] Requires ≤ 3 user interactions (counted)
- [ ] Feature is easily discoverable
- [ ] Clear feedback at every stage

✅ **Compatibility:**
- [ ] Works on Windows 10/11
- [ ] Works on macOS 10.15+
- [ ] Works on Ubuntu 20.04+
- [ ] Uses Python standard library only

### Testing Completeness

✅ **Unit Tests:**
- [ ] All CMATInstaller methods tested
- [ ] All validation logic tested
- [ ] All security checks tested
- [ ] Test coverage > 80%

✅ **Integration Tests:**
- [ ] Full installation flow tested
- [ ] Overwrite flow tested
- [ ] Rollback flow tested
- [ ] Error paths tested

✅ **Manual Tests:**
- [ ] Happy path tested on all platforms
- [ ] Error paths tested on all platforms
- [ ] UI responsiveness tested
- [ ] Connection flow tested

---

## 15. Next Steps

### For Implementer Agent

1. **Review this plan thoroughly**
2. **Resolve GitHub URL blocker** (confirm actual repository details)
3. **Begin with Phase 1** (Core Infrastructure)
4. **Test each component independently** before integration
5. **Follow the implementation sequence** to minimize risk
6. **Write tests as you go**, not after implementation
7. **Refer to existing code patterns** in ConnectDialog, Settings

### For Tester Agent (After Implementation)

1. **Run all unit tests** and verify coverage > 80%
2. **Run all integration tests** and verify all pass
3. **Execute manual test plan** on all platforms
4. **Test all error scenarios** from risk analysis
5. **Verify security validations** (directory traversal, system dirs)
6. **Performance testing** (measure installation time)
7. **User acceptance testing** (verify usability requirements)

### Critical Questions for Implementer

**Before Starting:**
- Q1: What is the actual GitHub repository URL? (BLOCKER)
- Q2: Should we download from main branch or latest release? (Recommend: main for MVP)
- Q3: Should we add post-install options like git init? (Recommend: defer to future)

**During Implementation:**
- Q4: What style of progress bar? (Recommend: determinate with percentage)
- Q5: Should we retry failed downloads automatically? (Recommend: no, let user retry)
- Q6: Should we add a "Test Connection" button? (Recommend: defer to future)

---

## 16. Design Decisions and Rationale

### Decision 1: Layered Architecture

**Decision:** Separate UI (dialog) from business logic (installer)

**Rationale:**
- Testability: Can test installer without UI
- Reusability: Installer can be used by CLI or other UIs
- Maintainability: Changes to UI don't affect installation logic
- Follows existing codebase patterns

**Alternatives Considered:**
- ❌ Monolithic dialog class: Poor testability, hard to maintain
- ❌ Multiple installer classes: Over-engineering for this scope

### Decision 2: Threading Model

**Decision:** Single background thread + queue for results

**Rationale:**
- Simplicity: Easier to reason about than multiple threads
- Safety: Minimizes thread synchronization issues
- Performance: One thread sufficient for I/O bound operations
- Follows Python best practices for Tkinter

**Alternatives Considered:**
- ❌ No threading: UI would freeze during installation
- ❌ Thread pool: Unnecessary complexity for single operation
- ❌ Async/await: Not compatible with Tkinter event loop

### Decision 3: Download Method

**Decision:** GitHub ZIP archive (not git clone)

**Rationale:**
- No dependencies: No git installation required
- Standard library: Uses urllib (no external packages)
- Simplicity: Easier to implement and test
- Security: Easier to validate than git operations

**Alternatives Considered:**
- ❌ Git clone: Requires git installation, harder to validate
- ❌ GitHub API: More complex, requires authentication for private repos
- ❌ Direct file downloads: Would require many requests for all files

### Decision 4: Atomic Installation

**Decision:** Extract to temp → validate → move atomically

**Rationale:**
- Safety: All-or-nothing, no partial installations
- Rollback: Easy to restore on failure
- Validation: Can validate before touching target
- Follows installer best practices

**Alternatives Considered:**
- ❌ Direct extraction: Can't rollback, leaves partial installations
- ❌ File-by-file copy: Slower, more error-prone
- ❌ In-place validation: Can't validate before overwriting

### Decision 5: Security Validations

**Decision:** Multi-layer validation (system dirs, ZIP entries, paths)

**Rationale:**
- Defense in depth: Multiple checks catch different threats
- User protection: Prevents accidental damage to system
- Security: Prevents directory traversal attacks
- Required: Security is critical for installer code

**Alternatives Considered:**
- ❌ Single validation: Easier to bypass or miss edge cases
- ❌ No validation: Unacceptable security risk
- ❌ Post-extraction validation: Too late, damage already done

---

## 17. Future Enhancements

**Out of Scope for MVP (Defer to Future):**

1. **Version Selection:** Allow user to choose specific release/tag
2. **Custom Repository:** Allow installation from custom CMAT forks
3. **Template Preview:** Show template contents before installation
4. **Offline Installation:** Install from local ZIP file
5. **Template Customization:** Wizard to customize template during installation
6. **Git Integration:** Automatically initialize git repository
7. **Sample Enhancement:** Create sample enhancement after installation
8. **Update Checker:** Check for template updates

---

## 18. Documentation Requirements

**Files to Update:**

1. **README.md:**
   - Add "Installing CMAT Template" section
   - Add screenshots of installation dialog
   - Add troubleshooting section for common errors

2. **User Guide** (if exists):
   - Add step-by-step installation guide
   - Add FAQ for installation errors
   - Add video/GIF demo of installation

3. **CHANGELOG.md:**
   - Add entry for new feature
   - List new menu item
   - Mention GitHub repository requirement

4. **Code Documentation:**
   - Docstrings for all public methods
   - Comments for complex security validations
   - Architecture diagram in code

---

## 19. Performance Targets

**Installation Time Breakdown:**

| Stage | Time Budget | Percent |
|-------|-------------|---------|
| Download (10 MB) | 0-25 seconds | 0-40% |
| Extract ZIP | 1-3 seconds | 2-5% |
| Validate | <1 second | <2% |
| Move to target | <1 second | <2% |
| **Total** | **<30 seconds** | **100%** |

**Assumptions:**
- Broadband connection (1 Mbps minimum)
- Template size ~10 MB
- SSD or fast HDD
- CPU not heavily loaded

**Optimization Opportunities:**
- Streaming extraction during download (future enhancement)
- Parallel file validation (future enhancement)
- Download resume on failure (future enhancement)

---

## 20. Architectural Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  MainWindow (src/main.py)                               │  │
│  │  - File menu                                            │  │
│  │  - "Install CMAT..." menu item                          │  │
│  └────────────────────────┬────────────────────────────────┘  │
│                           │ shows                              │
│                           ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  InstallCMATDialog (src/dialogs/install_cmat.py)        │  │
│  │  - Directory picker                                     │  │
│  │  - Progress bar                                         │  │
│  │  - Success/error dialogs                                │  │
│  └────────────────────────┬────────────────────────────────┘  │
│                           │ delegates to                       │
└───────────────────────────┼────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Business Logic                             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  CMATInstaller (src/installers/cmat_installer.py)       │  │
│  │  - download_template()                                  │  │
│  │  - extract_template()                                   │  │
│  │  - validate_installation()                              │  │
│  │  - rollback_installation()                              │  │
│  └────────────────────────┬────────────────────────────────┘  │
│                           │ uses                               │
└───────────────────────────┼────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Infrastructure                             │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  urllib.request  │  │   zipfile    │  │     pathlib     │  │
│  │  (HTTP download) │  │ (extraction) │  │ (path handling) │  │
│  └──────────────────┘  └──────────────┘  └─────────────────┘  │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │    threading     │  │    shutil    │  │   tempfile      │  │
│  │  (background)    │  │  (file ops)  │  │  (temp files)   │  │
│  └──────────────────┘  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      External Resources                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  GitHub (github.com)                                     │  │
│  │  https://github.com/{owner}/{repo}/archive/HEAD.zip     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Settings (src/settings.py)                              │  │
│  │  - last_install_directory                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 21. Summary

This implementation plan provides:

✅ **Complete Architecture:** Layered design with clear separation of concerns
✅ **Detailed Specifications:** Every component fully specified with APIs
✅ **Security Focus:** Multi-layer validation and threat mitigation
✅ **Implementation Sequence:** Step-by-step guide with priorities
✅ **Testing Strategy:** Unit, integration, and manual testing plans
✅ **Integration Guide:** Exact locations and code changes for integration
✅ **Risk Mitigation:** Strategies for all identified risks
✅ **Acceptance Criteria:** Clear definition of "done"

**Status:** READY FOR IMPLEMENTATION (pending GitHub URL confirmation)

**Estimated Effort:**
- Implementation: 4-5 days
- Testing: 1-2 days
- Documentation: 0.5 days
- **Total: 5.5-7.5 days**

**Blocked By:**
- GitHub repository URL confirmation (Q1)

**Recommended Next Steps:**
1. Resolve blocker (confirm GitHub URL)
2. Review and approve this plan
3. Pass to implementer agent
4. Begin Phase 1 implementation

---

**End of Implementation Plan**

**Document Version:** 1.0
**Agent:** Architect
**Status:** READY_FOR_IMPLEMENTATION
**Task ID:** task_1762445530_49766
**Timestamp:** 2025-11-06T08:00:00Z
