---
enhancement: cmat-installer
agent: requirements-analyst
task_id: task_1762444821_45573
timestamp: 2025-11-06T00:00:00Z
status: READY_FOR_DEVELOPMENT
---

# User Stories: CMAT Template Installer

## Epic

**As a** developer using the Multi-Agent Manager UI
**I want to** install the CMAT template into a new project directory directly from the UI
**So that** I can quickly bootstrap new projects without manually cloning repositories

---

## Story 1: Access Installer from Menu

**As a** developer
**I want to** see an "Install CMAT..." option in the File menu
**So that** I can easily discover and access the CMAT installation feature

### Acceptance Criteria
- [ ] "Install CMAT..." menu item appears in File menu
- [ ] Menu item is positioned after "Connect..." and before the separator/Quit
- [ ] Menu item is always enabled (not grayed out)
- [ ] Clicking menu item opens the installation dialog
- [ ] Keyboard shortcut is discoverable (displayed in menu)

### Complexity
Low (1 point)

### Notes
- Follows existing menu patterns in main.py:110-114
- Should integrate naturally with existing File menu structure

---

## Story 2: Select Installation Directory

**As a** developer
**I want to** browse and select a target directory for CMAT installation
**So that** I can control where the template is installed

### Acceptance Criteria
- [ ] Dialog shows "Browse..." button for directory selection
- [ ] File dialog opens when Browse is clicked
- [ ] File dialog filters for directories only (not files)
- [ ] Selected path is displayed in entry field
- [ ] User can also manually type/paste directory path
- [ ] Last-used directory is remembered between sessions
- [ ] Invalid paths are clearly indicated

### Complexity
Low (2 points)

### Notes
- Use existing ConnectDialog browse pattern (connect.py:93-100)
- Store last directory in Settings class like last_queue_manager
- Should validate path on change

---

## Story 3: Validate Directory Before Installation

**As a** developer
**I want to** be warned if a .claude folder already exists in the target directory
**So that** I don't accidentally overwrite existing CMAT installations

### Acceptance Criteria
- [ ] System checks if `.claude/` folder exists in target directory
- [ ] If exists, warning message clearly explains the situation
- [ ] User can choose to overwrite or cancel
- [ ] Warning indicates what will be replaced
- [ ] System validates directory is writable before proceeding
- [ ] System rejects system directories (/usr, /bin, C:\Windows, etc.)
- [ ] Clear error message if directory permissions are insufficient

### Complexity
Medium (3 points)

### Notes
- Use validation pattern similar to ConnectDialog (connect.py:91-150)
- Security-critical: Must prevent installation to system directories
- Should provide helpful guidance if user lacks permissions

---

## Story 4: Download CMAT Template from GitHub

**As a** developer
**I want to** the system to automatically download the latest CMAT template
**So that** I don't have to manually download or clone repositories

### Acceptance Criteria
- [ ] System downloads from official GitHub repository
- [ ] Downloads use HTTPS for security
- [ ] Progress indication shows download is in progress
- [ ] Download percentage or size downloaded is visible
- [ ] User can cancel download in progress
- [ ] Network errors show clear, actionable error messages
- [ ] Timeouts are handled gracefully (30 second timeout)
- [ ] Download uses temporary directory (cleanup on failure)

### Complexity
High (5 points)

### Notes
- Must use urllib.request (standard library only)
- Download ZIP archive: `https://github.com/{repo}/archive/refs/heads/{branch}.zip`
- Implement progress callback for UI updates
- Consider chunked download (8KB chunks) for large files
- GitHub repo URL needs confirmation before implementation

---

## Story 5: Extract .claude Folder Structure

**As a** developer
**I want to** the .claude folder extracted from the template to my target directory
**So that** my project has all necessary CMAT files

### Acceptance Criteria
- [ ] Only `.claude/` folder is extracted (not entire repository)
- [ ] Directory structure is preserved exactly
- [ ] File permissions are maintained where possible
- [ ] Progress indication shows extraction is in progress
- [ ] Directory traversal attacks are prevented (security check)
- [ ] Extraction uses atomic operation (temp → final location)
- [ ] Partial extractions are cleaned up on failure
- [ ] Validates extraction completeness after finishing

### Complexity
High (5 points)

### Notes
- Use Python zipfile module
- GitHub ZIP structure is: `repo-branch/.claude/...`
- Must strip repository prefix when extracting
- Critical security check: Validate no `..` in ZIP paths
- Atomic operation ensures no partial installations left behind

---

## Story 6: Validate Installation Success

**As a** developer
**I want to** confirmation that the installation was successful and complete
**So that** I know my CMAT project is ready to use

### Acceptance Criteria
- [ ] System checks for required v3.0 CMAT files after extraction
- [ ] Required files verified:
  - `.claude/scripts/cmat.sh`
  - `.claude/AGENT_CONTRACTS.json`
  - `.claude/skills/skills.json`
  - `.claude/agents/agents.json`
- [ ] Success message displays installation location
- [ ] Success message shows what was installed (agents count, skills count)
- [ ] Installation fails gracefully if validation fails
- [ ] Clear error message if template structure is invalid

### Complexity
Low (2 points)

### Notes
- Reuse validation logic patterns from ConnectDialog
- Should match CMAT v3.0 structure requirements
- Provides confidence that installation is functional

---

## Story 7: Connect to Newly Installed Project

**As a** developer
**I want to** be offered the option to immediately connect to my newly installed CMAT project
**So that** I can start using it without additional navigation steps

### Acceptance Criteria
- [ ] Success dialog includes "Connect Now" button
- [ ] Clicking "Connect Now" closes installer and opens project
- [ ] Project path is automatically populated (no re-browsing)
- [ ] Connection uses same flow as manual "Connect..." command
- [ ] User can decline and manually connect later
- [ ] "Close" button available for users who want to finish later

### Complexity
Medium (3 points)

### Notes
- Return project path as result from dialog
- Main window should handle connection using existing QueueInterface
- Seamless user experience from install to usage

---

## Story 8: Show Progress During Installation

**As a** developer
**I want to** see clear progress indication during download and extraction
**So that** I know the system is working and approximately how long it will take

### Acceptance Criteria
- [ ] Progress dialog appears immediately when installation starts
- [ ] Download phase shows percentage or size downloaded
- [ ] Extraction phase shows extraction in progress
- [ ] Current operation is clearly labeled ("Downloading...", "Extracting...")
- [ ] Progress bar or spinner is visible and animates
- [ ] UI remains responsive during operation
- [ ] Cancel button is available and functional
- [ ] Estimated time remaining (optional but nice to have)

### Complexity
Medium (4 points)

### Notes
- Use threading to keep UI responsive
- Progress callback mechanism for download chunks
- Consider indeterminate progress bar for extraction (hard to measure)
- Reference working.py for progress dialog patterns

---

## Story 9: Handle Network and File System Errors

**As a** developer
**I want to** receive clear error messages when installation fails
**So that** I can understand what went wrong and how to fix it

### Acceptance Criteria
- [ ] Network timeout errors show: "Unable to reach GitHub. Check your internet connection."
- [ ] HTTP errors show: "Failed to download template. GitHub may be unavailable."
- [ ] Permission errors show: "Cannot write to directory. Check folder permissions."
- [ ] Invalid directory shows: "Cannot install to system directory. Choose another location."
- [ ] Disk space errors show: "Insufficient disk space for installation."
- [ ] All errors include actionable next steps
- [ ] Partial installations are cleaned up automatically
- [ ] User can retry installation after fixing issue

### Complexity
Medium (3 points)

### Notes
- Comprehensive error handling is critical for user experience
- Use try/except blocks for each major operation
- Cleanup temp files on all error paths
- Consider logging errors for debugging

---

## Story 10: Remember Installation Preferences

**As a** developer
**I want to** the system to remember my last installation directory
**So that** I don't have to navigate to the same location repeatedly

### Acceptance Criteria
- [ ] Last-used installation directory is stored in settings
- [ ] Directory auto-populates when dialog opens (if previously used)
- [ ] Settings persist across application restarts
- [ ] Invalid stored paths are handled gracefully (removed/cleared)

### Complexity
Low (1 point)

### Notes
- Add to Settings class: `get_last_install_directory()` / `set_last_install_directory()`
- Follow pattern from `last_queue_manager` in settings.py:61-82
- Simple enhancement that improves usability

---

## Out of Scope (Future Stories)

The following stories are explicitly out of scope for MVP but documented for future consideration:

### Version Selection
**As a** developer
**I want to** choose a specific CMAT version to install
**So that** I can use a particular release or branch

**Reason for Deferral:** Adds complexity. Latest version is sufficient for MVP.

---

### Custom Template Sources
**As a** developer
**I want to** install templates from different GitHub repositories
**So that** I can use custom or forked templates

**Reason for Deferral:** Single official template source is sufficient for MVP.

---

### Sample Enhancement Creation
**As a** developer
**I want to** optionally create a sample enhancement file during installation
**So that** I have a starting point for my first task

**Reason for Deferral:** Nice to have but not essential. Can be added post-MVP.

---

### Git Repository Initialization
**As a** developer
**I want to** optionally initialize a git repository during installation
**So that** my project is immediately version controlled

**Reason for Deferral:** Many users will install into existing repos. Can be added post-MVP.

---

## Story Dependencies

```
Story 1 (Menu) → Story 2 (Directory Selection)
                     ↓
                 Story 3 (Validation)
                     ↓
                 Story 4 (Download)
                     ↓
                 Story 5 (Extraction)
                     ↓
                 Story 6 (Validation)
                     ↓
                 Story 7 (Connect)

Story 8 (Progress) → Spans Stories 4-5
Story 9 (Errors) → Spans Stories 2-7
Story 10 (Preferences) → Enhances Story 2
```

---

## Implementation Priority

**Phase 1 - Core Functionality (Must Have):**
1. Story 1 - Menu Integration
2. Story 2 - Directory Selection
3. Story 3 - Directory Validation
4. Story 4 - Download
5. Story 5 - Extraction
6. Story 6 - Installation Validation

**Phase 2 - User Experience (Should Have):**
7. Story 8 - Progress Indication
8. Story 9 - Error Handling
9. Story 10 - Preferences

**Phase 3 - Integration (Should Have):**
10. Story 7 - Auto-Connect

---

## Total Effort Estimate

- **Low Complexity (1-2 points):** 4 stories = 6 points
- **Medium Complexity (3-4 points):** 4 stories = 13 points
- **High Complexity (5 points):** 2 stories = 10 points

**Total: 29 story points**

**Estimated Development Time:** 4-5 days for experienced developer

---

## Success Metrics

**User Experience Metrics:**
- Installation completes in under 60 seconds on typical broadband
- Less than 3 user interactions required (select directory, confirm, connect)
- Zero manual file operations required

**Quality Metrics:**
- 99%+ success rate with stable internet connection
- Zero security vulnerabilities in file operations
- All error cases handled with clear messaging

**Adoption Metrics:**
- Feature discoverable without documentation
- First-time user can successfully install without help
- Reduces CMAT setup time from ~5 minutes (manual) to ~1 minute (automated)
