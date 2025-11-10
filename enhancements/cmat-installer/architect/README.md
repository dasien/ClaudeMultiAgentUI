---
enhancement: cmat-installer
agent: architect
task_id: task_1762445530_49766
timestamp: 2025-11-06T08:00:00Z
status: READY_FOR_IMPLEMENTATION
---

# Architect Phase: CMAT Template Installer

## Status: ✅ READY FOR IMPLEMENTATION

**Agent:** Architect
**Enhancement:** cmat-installer
**Task ID:** task_1762445530_49766
**Completion Date:** 2025-11-06

---

## Executive Summary

The architecture and technical design for the CMAT Template Installer feature is complete and ready for implementation. This enhancement enables one-click installation of the Claude Multi-Agent Template v3.0 structure from GitHub directly through the UI.

**Key Deliverables:**
1. ✅ Complete system architecture (layered, testable, secure)
2. ✅ Detailed component specifications (CMATInstaller, InstallCMATDialog)
3. ✅ Security architecture (multi-layer validation, threat prevention)
4. ✅ Threading architecture (responsive UI, thread-safe operations)
5. ✅ Implementation sequence (phased approach, 5.5-7.5 day estimate)
6. ✅ Testing strategy (unit, integration, manual)
7. ✅ Integration specifications (menu, settings, connection flow)

---

## Documents in This Package

### 1. implementation_plan.md (PRIMARY DELIVERABLE)

**Purpose:** Complete architecture and step-by-step implementation guide

**Contents:**
- System architecture and design patterns
- Component specifications (CMATInstaller, InstallCMATDialog)
- Data flow and threading architecture
- Security architecture (path validation, ZIP security, HTTPS)
- Error handling strategy
- Integration points (menu, settings, connection)
- Implementation sequence (4 phases, prioritized)
- Testing strategy (unit, integration, manual)
- Configuration and constants
- Acceptance criteria

**Start Here:** This is the main document for implementers.

### 2. api_specifications.md (SUPPORTING DOCUMENT)

**Purpose:** Detailed API reference and code examples

**Contents:**
- Complete API specifications for all classes
- Method signatures with full docstrings
- Exception hierarchy
- Progress callback protocol
- Settings extension API
- Code examples for common patterns
- Testing utilities and fixtures
- Integration examples

**Use For:** Reference during implementation for exact signatures and examples.

### 3. README.md (THIS DOCUMENT)

**Purpose:** Quick navigation and handoff summary

---

## Architecture Overview

### System Architecture

```
┌──────────────────────────────┐
│      UI Layer                │
│  InstallCMATDialog           │  ← User interaction, progress display
└──────────┬───────────────────┘
           │
           ↓
┌──────────────────────────────┐
│  Business Logic Layer        │
│  CMATInstaller               │  ← Download, extract, validate
└──────────┬───────────────────┘
           │
           ↓
┌──────────────────────────────┐
│  Infrastructure Layer        │
│  Python Standard Library     │  ← urllib, zipfile, pathlib, threading
└──────────────────────────────┘
```

### Key Design Decisions

1. **Layered Architecture:** UI, business logic, and infrastructure cleanly separated
2. **Threading:** Background thread for blocking I/O, main thread for UI
3. **Security:** Multi-layer validation (paths, ZIP entries, system directories)
4. **Atomic Operations:** Extract to temp → validate → move atomically with rollback
5. **Standard Library Only:** No external dependencies (urllib, zipfile, pathlib, threading)

### Files to Create

```
src/
├── installers/
│   ├── __init__.py                    # NEW - Package initialization
│   └── cmat_installer.py              # NEW - CMATInstaller class (~400 lines)
└── dialogs/
    └── install_cmat.py                # NEW - InstallCMATDialog class (~350 lines)
```

### Files to Modify

```
src/
├── main.py                            # MODIFY - Add menu item (~10 lines)
└── settings.py                        # MODIFY - Add 3 methods (~15 lines)
```

---

## Implementation Roadmap

### Phase 1: Core Infrastructure (Priority 1)

**Estimated Time:** 2-3 days

**Tasks:**
1. Create `CMATInstaller` class with validation methods
2. Implement download logic with progress tracking
3. Implement extraction with security validation
4. Implement structure validation (v3.0 requirements)
5. Implement atomic installation with rollback
6. Write unit tests for all components

**Critical:** Security validation must be implemented correctly in Phase 1.

### Phase 2: User Interface (Priority 1)

**Estimated Time:** 1-2 days

**Tasks:**
1. Create `InstallCMATDialog` skeleton
2. Implement directory selection UI
3. Implement progress display
4. Implement threading and result handling
5. Implement success/error dialogs
6. Write UI tests

**Critical:** Thread-safe progress updates are essential for responsive UI.

### Phase 3: Integration (Priority 2)

**Estimated Time:** 0.5-1 day

**Tasks:**
1. Add Settings methods
2. Add menu item to main.py
3. Implement connection flow after installation
4. Write integration tests
5. Test end-to-end flow

**Critical:** Connection flow must reuse existing connection logic.

### Phase 4: Polish (Priority 3)

**Estimated Time:** 1-1.5 days

**Tasks:**
1. Refine error messages
2. Improve progress messages
3. UI polish (spacing, icons, tooltips)
4. Platform testing (Windows, macOS, Linux)
5. Documentation updates

---

## Critical Blocker

### ⚠️ GitHub Repository URL Must Be Confirmed

**Issue:** The requirements analysis identified a placeholder GitHub URL that must be confirmed before implementation begins.

**Current Placeholder:**
```python
github_owner = "yourusername"  # ← NEEDS CONFIRMATION
github_repo = "ClaudeMultiAgentTemplate"
github_branch = "main"  # ← VERIFY
```

**Required Action:**
Confirm actual GitHub repository details:
- Owner/organization name
- Repository name
- Branch name (main, master, or v3)

**Recommended:**
```python
DEFAULT_GITHUB_OWNER = "anthropics"  # ← CONFIRM
DEFAULT_GITHUB_REPO = "ClaudeMultiAgentTemplate"  # ← CONFIRM
DEFAULT_GITHUB_BRANCH = "main"  # ← CONFIRM
```

**Impact:** Feature is completely non-functional without correct URL.

**Action Required:** Resolve before starting implementation.

---

## Security Requirements

### Critical Security Features (Must Implement)

1. **System Directory Blocking**
   - Prevent installation to /usr, /bin, /System, C:\Windows, etc.
   - Use comprehensive blacklist with path resolution

2. **Directory Traversal Prevention**
   - Validate every ZIP entry for ".." components
   - Reject absolute paths in ZIP entries
   - Normalize and validate all paths

3. **HTTPS Enforcement**
   - Only allow HTTPS downloads
   - Validate SSL certificates
   - Fail on HTTP or insecure connections

4. **Writability Validation**
   - Test write permissions before starting
   - Fail fast with clear error messages
   - Clean up test files

5. **Atomic Operations**
   - Extract to temp directory first
   - Validate before moving to target
   - Automatic rollback on failure
   - Clean up temp files

**Security Testing Required:**
- Unit tests with malicious ZIP files
- Unit tests with system directory paths
- Manual testing with permission errors
- Manual testing with various attack scenarios

---

## Testing Requirements

### Unit Tests (Required)

**Test File:** `tests/test_cmat_installer.py`

**Coverage Target:** >80%

**Key Test Cases:**
- Path validation (valid, invalid, system directories)
- ZIP entry validation (safe, directory traversal)
- Structure validation (valid v3.0, missing files)
- Backup and rollback functionality
- Error handling for all exception types

### Integration Tests (Required)

**Test File:** `tests/test_install_cmat_integration.py`

**Key Test Cases:**
- Full installation flow with mock ZIP
- Installation with overwrite
- Installation failure with rollback
- Concurrent installations (no interference)

### UI Tests (Required)

**Test File:** `tests/test_install_cmat_dialog.py`

**Key Test Cases:**
- Dialog opens and displays correctly
- Directory selection and validation
- Progress updates during installation
- Error dialogs display correctly
- Success dialog with connect option

### Manual Testing (Required)

**Platforms:**
- Windows 10/11
- macOS 10.15+
- Ubuntu 20.04+

**Test Scenarios:**
- Happy path (empty directory)
- Overwrite path (existing .claude)
- Error paths (permissions, network, disk full)
- Cancellation during installation

---

## Acceptance Criteria

### Functional Completeness

✅ **Installation Flow:**
- [ ] Menu item visible and functional
- [ ] Directory selection works
- [ ] Downloads from GitHub successfully
- [ ] Extracts .claude folder correctly
- [ ] Validates installation structure
- [ ] Shows progress during installation
- [ ] Completes within 60 seconds

✅ **Security:**
- [ ] System directories blocked
- [ ] Directory traversal prevented
- [ ] HTTPS-only downloads
- [ ] Path validation works

✅ **Error Handling:**
- [ ] All error types handled
- [ ] Clear error messages
- [ ] Automatic cleanup on failure
- [ ] Can retry after error

✅ **Success Flow:**
- [ ] Success dialog displays
- [ ] Can connect to installed project
- [ ] Connection works correctly

### Non-Functional Quality

✅ **Performance:**
- [ ] Installation < 60 seconds (measured)
- [ ] UI remains responsive
- [ ] Memory usage < 50 MB

✅ **Reliability:**
- [ ] 99%+ success rate (measured)
- [ ] Safe to retry
- [ ] No partial installations

✅ **Usability:**
- [ ] ≤ 3 user interactions
- [ ] Feature is discoverable
- [ ] Clear feedback at each stage

✅ **Compatibility:**
- [ ] Works on Windows 10/11
- [ ] Works on macOS 10.15+
- [ ] Works on Ubuntu 20.04+
- [ ] Python 3.7+ compatible

---

## Risk Mitigation Summary

### Critical Risks (Mitigated)

| Risk | Mitigation Strategy | Implementation Location |
|------|---------------------|------------------------|
| **Directory Traversal** | Validate every ZIP entry, reject ".." | `_validate_zip_entry()` |
| **Network Failures** | Timeout handling, clear errors | `_download_zip()` |
| **UI Unresponsive** | Background threading | `start_installation()` |
| **System Directory Install** | Blacklist with path resolution | `_is_system_directory()` |
| **Incomplete Install** | Atomic operations with rollback | `install()` method |

**See:** `implementation_plan.md` Section 13 for complete risk analysis.

---

## Integration Points

### 1. Menu Integration (main.py)

**Location:** Line ~113 (after "Connect...")

**Change:** Add menu item + handler method

```python
file_menu.add_command(label="Install CMAT...", command=self.show_install_cmat_dialog)
```

**See:** `api_specifications.md` Section 8.1 for complete code.

### 2. Settings Integration (settings.py)

**Change:** Add 3 methods for last install directory

```python
def get_last_install_directory(self) -> Optional[str]: ...
def set_last_install_directory(self, path: str): ...
def clear_last_install_directory(self): ...
```

**Pattern:** Follow existing `last_queue_manager` methods (lines 61-82)

**See:** `api_specifications.md` Section 8.2 for complete code.

### 3. Connection Integration

**Flow:** Install → Success Dialog → Connect (optional)

**Reuse:** Existing `connect_to_queue()` method in MainWindow

---

## Code Patterns to Follow

### 1. Dialog Pattern (from ConnectDialog)

- Inherit from `BaseDialog`
- Use `build_ui()` for UI construction
- Use `show()` to display and wait
- Return result via `self.close(result)`
- Handle Escape key for cancel
- Center on parent automatically

### 2. Settings Pattern (from existing methods)

- Store in `self._data` dictionary
- Use `self._save()` after changes
- Provide get/set/clear methods
- Handle missing keys gracefully

### 3. Threading Pattern (recommended)

- Use `threading.Thread` with `daemon=True`
- Use `queue.Queue` for results
- Use `dialog.after()` for UI updates
- Poll queue from main thread
- Clean up thread on completion

---

## Resources for Implementer

### Required Reading

1. **implementation_plan.md** - Read sections 1-8 completely
2. **api_specifications.md** - Reference during implementation
3. **requirements_specification.md** - Understand all requirements
4. **risk_analysis.md** - Understand security requirements

### Code References

- **BaseDialog pattern:** `src/dialogs/base_dialog.py`
- **Dialog example:** `src/dialogs/connect.py`
- **Settings pattern:** `src/settings.py`
- **Menu integration:** `src/main.py:110-114`
- **QueueInterface:** `src/queue_interface.py` (for understanding connection)

### Key Technologies

- **tkinter:** UI framework (already used throughout)
- **urllib.request:** HTTP downloads (standard library)
- **zipfile:** ZIP extraction (standard library)
- **pathlib:** Path operations (standard library)
- **threading:** Background operations (standard library)
- **queue:** Thread communication (standard library)

---

## Questions for Implementer

### Before Starting

1. **GitHub URL (BLOCKER):** What is the actual repository URL?
2. **Version Strategy:** Download from main branch or latest release?
3. **Post-Install Options:** Add git init or sample enhancement? (Recommend: defer)

### During Implementation

4. **Progress Bar Style:** Determinate with percentage? (Recommend: yes)
5. **Auto-Retry:** Retry failed downloads automatically? (Recommend: no)
6. **Test Connection:** Add "Test Connection" button? (Recommend: defer)

### For Architect (if needed)

- Any ambiguities in architecture?
- Need clarification on any design decision?
- Want to propose alternative approach?

**Contact:** Escalate questions via workflow system or directly to architect agent.

---

## Success Metrics

### Development Metrics

- [ ] Implementation complete within 5.5-7.5 days
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Manual testing on all 3 platforms successful

### User Experience Metrics

- [ ] Installation time < 60 seconds (measured)
- [ ] User interactions ≤ 3 (counted)
- [ ] Error rate < 1% with stable internet (measured)
- [ ] Feature discoverable without documentation (observed)

### Quality Metrics

- [ ] Zero critical security vulnerabilities
- [ ] All error cases handled with clear messages
- [ ] 100% cleanup on failure (no partial installs)
- [ ] UI responsive throughout operation

---

## Next Steps

### Immediate Actions

1. **Resolve Blocker:** Confirm GitHub repository URL
2. **Review Plan:** Read implementation_plan.md thoroughly
3. **Set Up Environment:** Create dev branch, prepare test environment
4. **Begin Phase 1:** Start with CMATInstaller core infrastructure

### Implementation Sequence

1. **Phase 1:** Core Infrastructure (CMATInstaller) - 2-3 days
2. **Phase 2:** User Interface (InstallCMATDialog) - 1-2 days
3. **Phase 3:** Integration (Menu, Settings, Connection) - 0.5-1 day
4. **Phase 4:** Polish (Error messages, UI, Testing) - 1-1.5 days

### Quality Gates

- ✅ After Phase 1: All unit tests passing, security tests passing
- ✅ After Phase 2: UI tests passing, threading works correctly
- ✅ After Phase 3: Integration tests passing, end-to-end flow works
- ✅ After Phase 4: Manual testing complete on all platforms

---

## Handoff Checklist

### Architect Deliverables

- [x] System architecture designed
- [x] Component specifications complete
- [x] Security architecture defined
- [x] Threading architecture specified
- [x] Error handling strategy documented
- [x] Integration points identified
- [x] Implementation sequence defined
- [x] Testing strategy created
- [x] API specifications documented
- [x] Code examples provided

### Implementer Prerequisites

- [ ] Review implementation_plan.md
- [ ] Review api_specifications.md
- [ ] Review requirements documents
- [ ] Understand security requirements
- [ ] Confirm GitHub repository URL
- [ ] Set up development environment
- [ ] Prepare test environment

### Blocker Resolution

- [ ] GitHub repository URL confirmed
- [ ] Version strategy decided (main branch recommended)
- [ ] Post-install options decided (defer recommended)

---

## Document Change Log

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2025-11-06 | 1.0 | Initial architecture complete | Architect |

---

## Contact and Support

**Primary Document:** implementation_plan.md
**Supporting Document:** api_specifications.md
**Enhancement ID:** cmat-installer
**Task ID:** task_1762445530_49766

**Architect Status:** ✅ READY_FOR_IMPLEMENTATION

**Next Agent:** Implementer

---

**End of Architect README**
