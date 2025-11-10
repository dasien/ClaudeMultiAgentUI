---
slug: cmat-installer-feature
status: NEW
created: 2025-01-04
author: System User
priority: medium
---

# Enhancement: CMAT Template Installer

## Overview
**Goal:** Add the ability to install the Claude Multi-Agent Template (CMAT) `.claude/` folder structure into a user-selected directory directly from the UI.

**User Story:**
As a developer using the Multi-Agent Manager UI, I want to install the CMAT template into a new project directory without manually cloning the GitHub repo, so that I can quickly bootstrap new projects with the multi-agent system.

## Context & Background
**Current State:**
- Users must manually clone the ClaudeMultiAgentTemplate repository to get the `.claude/` folder
- Users must manually copy the `.claude/` folder to their project
- No automated way to bootstrap a new CMAT project
- The UI can connect to existing CMAT projects but cannot create them

**Technical Context:**
- Target platform: Python 3.7+ with Tkinter
- Must download from GitHub repository
- Must handle directory creation and file extraction
- Uses Python standard library only (no external dependencies)
- GitHub repo: https://github.com/yourusername/ClaudeMultiAgentTemplate (adjust URL)
- Need to download the `.claude/` folder structure

**Dependencies:**
- Python standard library: `urllib.request`, `zipfile`, `shutil`
- GitHub API or direct archive download
- Existing Settings class for storing preferences
- BaseDialog for consistent UI

## Requirements

### Functional Requirements
1. **Menu Item**: Add "Install CMAT..." to File menu
2. **Directory Selection**: User selects target directory for installation
3. **Download**: Download latest CMAT template from GitHub
4. **Extraction**: Extract `.claude/` folder to target directory
5. **Validation**: Verify installation completed successfully
6. **Auto-Connect**: Optionally connect to newly installed project
7. **Progress Indication**: Show progress during download and extraction
8. **Error Handling**: Handle network failures, permission errors, invalid directories

### Non-Functional Requirements
- **Performance:** Installation completes within 60 seconds on typical connection
- **Reliability:** Validate downloaded content before extraction
- **Usability:** Clear progress indication and error messages
- **Safety:** Don't overwrite existing `.claude/` folders without confirmation
- **Compatibility:** Works on Windows, macOS, Linux

### Must Have (MVP)
- [ ] Menu item: File > Install CMAT...
- [ ] Directory picker dialog
- [ ] Check if `.claude/` already exists (warn before overwriting)
- [ ] Download CMAT template from GitHub
- [ ] Extract `.claude/` folder to target directory
- [ ] Progress dialog during download/extraction
- [ ] Success message with option to connect
- [ ] Error handling for common failures

### Should Have (if time permits)
- [ ] Version selection (latest vs. specific version)
- [ ] Preview what will be installed
- [ ] Validate installation after extraction
- [ ] Create sample enhancement file
- [ ] Initialize git repository option

### Won't Have (out of scope)
- Custom template selection (reason: single template for now)
- Template editing/customization (reason: use GitHub repo)
- Multiple template sources (reason: single official source)
- Offline installation (reason: requires network)

## Open Questions
> These need answers before architecture review

1. **GitHub download method**: Use GitHub API, download ZIP archive, or git clone?
2. **Version strategy**: Always latest, or let user select release/tag?
3. **Overwrite behavior**: Warn and skip, merge, or full replace?
4. **Post-install**: Auto-connect to installed project or just show success?
5. **Template URL**: Hardcode or make configurable in settings?
6. **Progress granularity**: Just "Installing..." or show download/extract separately?
7. **Permissions**: How to handle directories user can't write to?

## Constraints & Limitations
**Technical Constraints:**
- Must use Python standard library only (no `git` command, no `requests`)
- Must work with urllib.request for downloads
- Cannot require git to be installed
- Limited to public GitHub repositories
- Must handle large downloads (several MB for full template)

**Business/Timeline Constraints:**
- Should be simple and reliable
- Focus on latest version (version selection can come later)
- Don't need to support custom templates initially

**Security Constraints:**
- Validate downloaded content (check for `.claude/` structure)
- Don't execute downloaded scripts automatically
- Warn before overwriting existing files
- Handle directory traversal attempts in ZIP files

## Success Criteria
**Definition of Done:**
- [ ] Menu item visible and clickable
- [ ] Directory picker opens and validates selection
- [ ] Warns if `.claude/` exists in target directory
- [ ] Downloads CMAT template successfully
- [ ] Extracts `.claude/` folder to target
- [ ] Shows progress during operation
- [ ] Success message appears with path
- [ ] Offers to connect to installed project
- [ ] All errors handled gracefully
- [ ] Works on Windows, macOS, and Linux

**Acceptance Tests:**
1. Given empty directory selected, when user installs CMAT, then `.claude/` folder created with all required files
2. Given directory with existing `.claude/`, when user attempts install, then warning shown and user can cancel
3. Given network failure during download, when error occurs, then clear error message and no partial installation
4. Given successful installation, when user clicks "Connect Now", then project opens in UI
5. Given installation complete, when validating structure, then all required v3.0 files present

## Security & Safety Considerations
- **Download validation**: Verify ZIP file is valid before extraction
- **Path validation**: Ensure target directory is safe (no system directories)
- **Overwrite protection**: Warn before replacing existing `.claude/` folder
- **ZIP safety**: Check for directory traversal in ZIP entries
- **Permissions**: Handle permission errors gracefully
- **Network security**: Use HTTPS for GitHub downloads
- **No auto-execution**: Don't run any downloaded scripts

## UI/UX Considerations

### Installation Flow
```
User: File > Install CMAT...
  ↓
Dialog: "Install Claude Multi-Agent Template"
  - Select target directory: [Browse...]
  - Template version: Latest (v3.0)
  - [ ] Create sample enhancement
  - [ ] Initialize git repository
  ↓
[Install] [Cancel]
  ↓
Check: Does target/.claude exist?
  ↓ YES
Warning: ".claude folder exists. Overwrite? [Yes] [No]"
  ↓ NO
Cancel installation
  ↓ YES
Progress: "Downloading template... ⠋ Downloading..."
Progress: "Extracting files... ⠋ Extracting..."
  ↓
Success: "CMAT installed successfully!
          Location: /path/to/project/.claude
          
          [Connect Now] [Close]"
```

### Error Messages
- "Failed to download: Network error"
- "Permission denied: Cannot write to directory"
- "Invalid directory: Cannot install to system directory"
- "Download failed: GitHub repository not accessible"

## Testing Strategy
**Unit Tests:**
- ZIP file extraction logic
- Directory validation (safe paths)
- `.claude/` existence check
- Path construction

**Integration Tests:**
- Mock GitHub download
- Test extraction to temp directory
- Validate extracted structure
- Test overwrite warning flow

**Manual Test Scenarios:**
1. Install to empty directory → Success
2. Install to directory with existing `.claude/` → Warning → Cancel
3. Install to directory with existing `.claude/` → Warning → Overwrite → Success
4. Network failure during download → Error message
5. Permission denied on directory → Error message
6. Cancel during download → No partial installation
7. Connect after install → Project loads successfully

## Implementation Approach

### High-Level Design

```python
# src/dialogs/install_cmat_dialog.py
class InstallCMATDialog(BaseDialog):
    """Dialog for installing CMAT template."""
    
    def __init__(self, parent, settings):
        super().__init__(parent, "Install CMAT Template", 600, 400)
        self.settings = settings
        self.build_ui()
        self.show()
    
    def build_ui(self):
        # Directory picker
        # Options (sample enhancement, git init)
        # Install button
        pass
    
    def install(self):
        # Validate directory
        # Check for existing .claude/
        # Download in thread
        # Extract
        # Show success
        pass
```

```python
# src/utils/cmat_installer.py
class CMATInstaller:
    """Handles downloading and installing CMAT template."""
    
    GITHUB_REPO = "yourusername/ClaudeMultiAgentTemplate"
    BRANCH = "main"
    
    def download_template(self, progress_callback=None):
        """Download template ZIP from GitHub."""
        url = f"https://github.com/{self.GITHUB_REPO}/archive/refs/heads/{self.BRANCH}.zip"
        # Use urllib.request to download
        pass
    
    def extract_claude_folder(self, zip_path, target_dir):
        """Extract only .claude/ folder from ZIP."""
        # Use zipfile to extract
        # Validate structure
        pass
    
    def validate_installation(self, target_dir):
        """Verify installation is complete and valid."""
        # Check for required files
        pass
```

### Download Options

**Option 1: Download ZIP Archive (Recommended)**
```python
url = f"https://github.com/{REPO}/archive/refs/heads/main.zip"
# Download with urllib.request
# Extract with zipfile module
# Pros: No git required, standard library only
# Cons: Gets full repo, must extract only .claude/
```

**Option 2: GitHub API + Individual Files**
```python
# Get tree via GitHub API
# Download each file individually
# Pros: Can get only .claude/ folder
# Cons: Many HTTP requests, slower
```

**Option 3: Sparse Checkout (Advanced)**
```python
# Requires git command
# Pros: Efficient, official method
# Cons: Requires git installation
```

**Recommendation: Option 1 (ZIP Archive)** - Uses standard library, simple, reliable

### Directory Validation

```python
def validate_target_directory(path: Path) -> tuple[bool, str]:
    """Validate target directory is safe for installation."""
    
    # Check if path is absolute
    if not path.is_absolute():
        return False, "Please provide an absolute path"
    
    # Check for system directories
    system_dirs = ['/usr', '/bin', '/etc', '/System', 'C:\\Windows', 'C:\\Program Files']
    if any(str(path).startswith(sd) for sd in system_dirs):
        return False, "Cannot install to system directory"
    
    # Check if writable
    if path.exists() and not os.access(path, os.W_OK):
        return False, "No write permission for directory"
    
    # Check if .claude exists
    claude_dir = path / ".claude"
    if claude_dir.exists():
        return True, "Warning: .claude folder already exists"
    
    return True, "Directory is valid"
```

### Installation Flow

```python
def install_cmat(target_dir: Path, on_progress=None):
    """Install CMAT template to target directory."""
    
    # 1. Create temp directory for download
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = Path(temp_dir) / "template.zip"
        
        # 2. Download ZIP
        if on_progress:
            on_progress("Downloading template from GitHub...")
        
        download_github_zip(zip_path)
        
        # 3. Extract .claude folder
        if on_progress:
            on_progress("Extracting files...")
        
        extract_claude_folder(zip_path, target_dir)
        
        # 4. Validate installation
        if on_progress:
            on_progress("Validating installation...")
        
        if not validate_installation(target_dir):
            raise Exception("Installation validation failed")
        
        # 5. Success!
        if on_progress:
            on_progress("Installation complete!")
```

## Technical Specification

### GitHub Download

```python
def download_github_zip(output_path: Path, repo: str, branch: str = "main"):
    """
    Download GitHub repository as ZIP archive.
    
    Args:
        output_path: Where to save the ZIP file
        repo: Repository (e.g., "owner/repo")
        branch: Branch name (default: "main")
    """
    url = f"https://github.com/{repo}/archive/refs/heads/{branch}.zip"
    
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'ClaudeMultiAgentUI/1.0'}
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        total_size = int(response.headers.get('Content-Length', 0))
        
        with open(output_path, 'wb') as f:
            downloaded = 0
            chunk_size = 8192
            
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                
                f.write(chunk)
                downloaded += len(chunk)
                
                # Report progress
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    # Callback for progress
```

### ZIP Extraction

```python
def extract_claude_folder(zip_path: Path, target_dir: Path):
    """
    Extract only the .claude/ folder from ZIP to target directory.
    
    Args:
        zip_path: Path to downloaded ZIP file
        target_dir: Where to extract .claude/ folder
    """
    import zipfile
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Find .claude/ entries in ZIP
        # GitHub ZIP has structure: repo-name-branch/.claude/...
        
        for member in zip_ref.namelist():
            # Look for .claude/ in path
            if '/.claude/' in member or member.endswith('/.claude'):
                # Extract and strip repo prefix
                # Security: Check for directory traversal
                if '..' in member:
                    continue
                
                # Extract to target
                pass
```

### Validation

```python
def validate_installation(target_dir: Path) -> bool:
    """
    Validate that CMAT was installed correctly.
    
    Checks for required v3.0 structure:
    - .claude/scripts/cmat.sh
    - .claude/AGENT_CONTRACTS.json
    - .claude/skills/skills.json
    - .claude/agents/agents.json
    """
    required_files = [
        ".claude/scripts/cmat.sh",
        ".claude/AGENT_CONTRACTS.json",
        ".claude/skills/skills.json",
        ".claude/agents/agents.json"
    ]
    
    for file_path in required_files:
        full_path = target_dir / file_path
        if not full_path.exists():
            return False
    
    return True
```

## UI Design

### Install Dialog

```
┌─────────────────────────────────────────┐
│  Install Claude Multi-Agent Template    │
├─────────────────────────────────────────┤
│                                          │
│  Target Directory: *                     │
│  [/path/to/project          ] [Browse...]│
│                                          │
│  Template Version:                       │
│  ○ Latest (v3.0)                         │
│  ○ Specific version: [v3.0.0 ▼]         │
│                                          │
│  Options:                                │
│  ☐ Create sample enhancement            │
│  ☐ Initialize git repository             │
│                                          │
│  ─────────────────────────────────────  │
│                                          │
│  This will download and install:         │
│  • CMAT scripts and tools                │
│  • Agent definitions and contracts       │
│  • Skills system                         │
│  • Queue management system               │
│  • Workflow templates                    │
│                                          │
│  Source: github.com/you/CMATTemplate     │
│                                          │
│         [Install]  [Cancel]              │
└─────────────────────────────────────────┘
```

### Progress Dialog

```
┌─────────────────────────────────┐
│  Installing CMAT Template       │
├─────────────────────────────────┤
│                                  │
│  ⠋ Downloading from GitHub...   │
│                                  │
│  [████████░░░░░░░░░░] 45%       │
│                                  │
│  Downloaded: 2.3 MB / 5.1 MB    │
│                                  │
└─────────────────────────────────┘
```

### Success Dialog

```
┌─────────────────────────────────────┐
│  Installation Complete              │
├─────────────────────────────────────┤
│                                     │
│  ✓ CMAT template installed!         │
│                                     │
│  Location:                          │
│  /Users/you/projects/myapp/.claude  │
│                                     │
│  Installed:                         │
│  • Scripts and tools                │
│  • 5 agents                         │
│  • 12 skills                        │
│  • Workflow system                  │
│                                     │
│    [Connect Now]  [Close]           │
└─────────────────────────────────────┘
```

## Testing Strategy
**Unit Tests:**
- Directory validation logic
- ZIP extraction with path filtering
- Installation validation
- GitHub URL construction

**Integration Tests:**
- Mock GitHub download
- Extract to temp directory
- Validate extracted structure
- Test overwrite warning

**Manual Test Scenarios:**
1. Install to empty directory → Success → Connect
2. Install to directory with `.claude/` → Warning → Cancel
3. Install to directory with `.claude/` → Warning → Overwrite → Success
4. Network failure → Error message
5. Invalid directory → Validation error
6. Permission denied → Error message
7. Partial download (cancel) → No files left
8. Install then create task → Works

## Implementation Plan

### Phase 1: Core Installer (Days 1-2)
- Create `src/utils/cmat_installer.py`
- Implement `download_github_zip()`
- Implement `extract_claude_folder()`
- Implement `validate_installation()`
- Unit tests

### Phase 2: UI Dialog (Day 3)
- Create `src/dialogs/install_cmat_dialog.py`
- Implement directory picker
- Implement validation
- Implement install button

### Phase 3: Progress & Threading (Day 4)
- Thread the download/extraction
- Progress dialog
- Cancel support
- Error handling

### Phase 4: Integration & Polish (Day 5)
- Add menu item to main.py
- Connect after install option
- Documentation
- Manual testing

## References & Research
**GitHub Archive Download:**
- URL pattern: `https://github.com/USER/REPO/archive/refs/heads/BRANCH.zip`
- Public repos don't require authentication
- ZIP contains `REPO-BRANCH/` prefix folder

**Python ZIP Handling:**
- `zipfile.ZipFile()` - Standard library
- Security: Check for `..` in paths
- Can extract specific files/folders

**Similar Implementations:**
- Package managers (pip, npm)
- Template generators (cookiecutter pattern)
- Git sparse checkout

**Directory Traversal Prevention:**
```python
def is_safe_path(base_path: Path, target_path: Path) -> bool:
    """Check if target is within base path (no traversal)."""
    try:
        target_path.resolve().relative_to(base_path.resolve())
        return True
    except ValueError:
        return False
```

## Notes for PM Subagent
- Verify GitHub repository URL before implementation
- Confirm we want "latest" vs. version selection
- Decide on post-install options (sample enhancement, git init)
- Validate that "zero dependencies" constraint can be maintained

## Notes for Architect Subagent
- Design must use only Python standard library (urllib, zipfile, shutil)
- Consider using ThreadPoolExecutor for download if large
- Design progress callback mechanism
- Plan for cancellation during download
- Consider atomic installation (temp dir → move on success)

## Notes for Implementer Subagent
- Use `urllib.request.urlopen()` for download (no requests library)
- Use `zipfile.ZipFile()` for extraction
- Implement progress callback for UI updates
- Validate all ZIP paths for directory traversal
- Use `tempfile.TemporaryDirectory()` for atomic install
- Add comprehensive error messages
- Test on all platforms (Windows paths, etc.)

## Notes for Testing Subagent
- Mock urllib.request for unit tests
- Test with actual GitHub download in integration tests
- Validate ZIP extraction security
- Test all error paths (network, permissions, validation)
- Manual testing on Windows, macOS, Linux
- Test with slow network (progress updates)
