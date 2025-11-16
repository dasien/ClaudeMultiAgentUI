# Claude Multi-Agent Manager - User Guide

**Version 1.2.0**

This guide provides comprehensive instructions for using the Claude Multi-Agent Manager, a graphical interface for the Claude Multi-Agent Template (CMAT) system.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Main Window Overview](#main-window-overview)
3. [Project Management](#project-management)
4. [Task Management](#task-management)
5. [Enhancement Generation](#enhancement-generation)
6. [Agent Management](#agent-management)
7. [Skills System](#skills-system)
8. [Workflow Visualization](#workflow-visualization)
9. [Workflow Template Management](#workflow-template-management)
10. [Integration Dashboard](#integration-dashboard)
11. [Settings and Configuration](#settings-and-configuration)
12. [Keyboard Shortcuts](#keyboard-shortcuts)
13. [Common Workflows](#common-workflows)
14. [Troubleshooting](#troubleshooting)

---

## Getting Started

### First Launch

When you first launch the application:

1. The main window opens with "Not connected" status
2. You'll see an empty task queue
3. Most menu options are disabled until you connect to a project

### Prerequisites

Before you begin, you need:

- **Python 3.7+** with Tkinter installed
- Either:
  - An existing CMAT project (v3.0+), OR
  - A directory where you want to install CMAT

### Optional: Claude API Configuration

For AI-powered features, you'll need:

- A Claude API key from [console.anthropic.com](https://console.anthropic.com)
- This enables:
  - Enhancement specification generation
  - Task description generation
  - Agent role definition generation

---

## Main Window Overview

**[SCREENSHOT: Main window overview showing all components]**

### Header Bar

The header displays your connection status:

```
Connected: /path/to/your/project     CMAT v3.0
```

- **Left side**: Shows project root path when connected
- **Right side**: Shows CMAT version number

**[SCREENSHOT: Header bar showing connected state]**

### Task Queue Table

**[SCREENSHOT: Task queue table with multiple tasks in different states]**

The main table displays all tasks with columns:

| Column | Description |
|--------|-------------|
| **Task ID** | Unique identifier (e.g., `task_2025-01-15_1234567890`) |
| **Title** | Short task description |
| **Agent** | Assigned agent name |
| **Status** | Current status (Pending, Active, Completed, Failed) |
| **Start Date** | When task execution began |
| **End Date** | When task completed or failed |
| **Runtime** | Total execution time (e.g., "2m 30s") |

### Task Status Colors

Tasks are color-coded for quick identification:

- **White background** - Pending tasks
- **Light yellow background** - Active tasks
- **Light green background** - Completed tasks
- **Light red background** - Failed tasks

### Status Bar

The bottom status bar shows:

- **Left**: Connection status and task counts
  - Example: `5 Pending | 2 Active | 23 Completed | 1 Failed`
- **Right**: Auto-refresh status
  - Example: `Auto-refresh: ✓ ON (3s)` or `Auto-refresh: OFF`

---

## Project Management

### Installing CMAT Template

**When to use**: You don't have a CMAT project yet and want to create one.

**Menu**: File > Install CMAT Template...

**[SCREENSHOT: Install CMAT Template dialog - initial state]**

**Steps**:

1. Click **Browse...** or enter a directory path
   - This is where the `.claude/` folder will be created
   - Example: `/home/user/my-new-project/`

2. **Directory Validation**: The dialog checks:
   - ✓ Directory exists and is writable
   - ⚠ Warning if `.claude/` already exists (offers overwrite)
   - ✗ Error if path is invalid or not writable

**[SCREENSHOT: Install dialog showing validation checks]**

3. Click **Install**
   - Progress bar shows download and extraction
   - Takes 10-30 seconds depending on connection

**[SCREENSHOT: Install dialog showing progress bar during installation]**

4. **On Success**:
   - Shows success dialog with installation location
   - Option to "Connect Now" or "Close"

**[SCREENSHOT: Installation success dialog]**

5. **If Overwriting**:
   - Automatic backup created: `.claude_backup_[random]/`
   - Backup deleted on successful installation
   - Backup restored on failure

**What gets installed**:
- `.claude/scripts/cmat.sh` - Main CMAT command
- `.claude/agents/` - Agent definitions
- `.claude/skills/` - Skill modules
- `.claude/queues/` - Task queue files
- `.claude/AGENT_CONTRACTS.json` - Workflow contracts
- And more...

### Connecting to Existing Project

**When to use**: You already have a CMAT project and want to work with it.

**Menu**: File > Connect...  
**Shortcut**: `Ctrl+O`

**[SCREENSHOT: Connect to Project dialog]**

**Steps**:

1. Click **Browse...**
2. Navigate to your **project root directory**
   - This is the directory that CONTAINS `.claude/`
   - NOT the `.claude/` directory itself

3. **Validation Checks**: The dialog validates:
   - ✓ CMAT script (`.claude/scripts/cmat.sh`)
   - ✓ Task queue (`.claude/queues/task_queue.json`)
   - ✓ Agent contracts (`.claude/AGENT_CONTRACTS.json`)
   - ✓ Skills system (`.claude/skills/skills.json`)
   - ✓ Agents (`.claude/agents/agents.json`)

**[SCREENSHOT: Connect dialog showing validation checkmarks]**

4. **Version Detection**:
   - Shows "✓ Valid CMAT v3.0 Project" if all checks pass
   - Shows error if older version detected

5. Click **Connect**

**After Connecting**:
- Header updates with project path
- Task queue loads automatically
- All menu options become available
- Connection is saved for next launch

### Switching Projects

You can connect to different projects without restarting:

1. File > Connect...
2. Select different project
3. All data refreshes to new project

The last connected project is remembered and auto-connects on launch.

### Resetting Queue

**Menu**: File > Reset Queue...

**Warning**: This clears ALL tasks and logs.

**Use cases**:
- Starting fresh after testing
- Clearing corrupted queue state
- Resetting after major changes

**What gets reset**:
- All pending tasks → deleted
- All active tasks → deleted
- All completed tasks → deleted
- All failed tasks → deleted
- Queue operations log → cleared

---

## Task Management

### Understanding Tasks

A **task** represents work assigned to an agent. Each task:

- Has a unique ID
- References a source file (usually a markdown enhancement)
- Contains instructions for the agent
- Produces outputs according to the agent's contract
- Can chain to the next agent in the workflow

### Creating a Task

**Menu**: Tasks > Create Task...  
**Shortcut**: `Ctrl+N`  
**Alternative**: Right-click in empty space → Create Task...

**[SCREENSHOT: Create Task dialog - complete view]**

#### Task Creation Dialog

The Create Task dialog has several sections:

##### 1. Basic Information

**[SCREENSHOT: Task creation - basic information section]**

**Title** (required)
- Short, descriptive name for the task
- Example: "Analyze Login Feature Requirements"
- Appears in task queue table

**Quick Start Workflow** (optional)
- Pre-configured workflow templates
- Options:
  - **📋 Full Feature** - Complete development workflow (all agents)
  - **🐛 Bug Fix** - Skip documentation phase
  - **🔥 Hotfix** - Emergency fix, skip analysis
  - **🔧 Refactoring** - Code improvement, skip requirements
- Selecting a workflow auto-fills agent, priority, and automation settings

##### 2. Agent Assignment

**[SCREENSHOT: Agent selection showing skills preview]**

**Agent** (required)
- Select from available agents
- Common agents:
  - **Requirements Analyst** - Analyzes and documents requirements
  - **Architect** - Creates technical designs
  - **Implementer** - Writes code
  - **Tester** - Creates and runs tests
  - **Documenter** - Writes documentation

**Agent Skills Preview**
- Shows skills available to selected agent
- Click "Preview Full Skills Prompt" to see complete skills injection
- Helps understand agent capabilities

##### 3. Task Configuration

**Priority** (required)
- **Critical** - Must be done immediately
- **High** - Important, high priority
- **Normal** - Standard priority (default)
- **Low** - Can be deferred

**Task Type** (required)
- **Analysis** - Requirements and planning work
- **Technical Analysis** - Architecture and design
- **Implementation** - Coding and development
- **Testing** - Test creation and execution
- **Documentation** - Writing docs
- **Integration** - External system integration

##### 4. Source File

**Source File** (required)
- Path to the input document (usually markdown)
- Typically: `enhancements/{enhancement-name}/{enhancement-name}.md`
- Click **Browse...** to select file
- Validation shows if file matches agent's expected pattern

##### 5. Task Description

**Description** (required)
- Detailed instructions for the agent
- What the agent should do
- Expected deliverables
- Success criteria

**Generate with Claude** button:
- Uses AI to create comprehensive description
- Requires Claude API key configured
- Includes agent skills and source file content
- Takes 15-30 seconds

##### 6. Automation Options

**Auto Complete**
- When checked: Task completes without user confirmation
- When unchecked: User must manually complete task
- Use for: Trusted, repeatable tasks

**Auto Chain**
- When checked: Automatically creates next agent's task upon completion
- When unchecked: Workflow stops, user creates next task manually
- Use for: Full workflow automation

#### Creating the Task

**Three options**:

1. **Create Task**
   - Adds task to pending queue
   - Does not start execution
   - Use when: You want to queue multiple tasks

2. **Create & Start**
   - Adds task to pending queue
   - Immediately starts execution
   - Agent runs in background
   - Use when: Ready to execute now

3. **Cancel**
   - Discards task
   - No changes made

### Starting a Task

**Multiple methods**:

1. Right-click pending task → **Start Task**
2. Select pending task and press `Enter`
3. Create with **Create & Start** button

**What happens**:
- Task status changes to "Active"
- Agent executes in background
- Task updates automatically when complete
- Log file created in enhancement's `logs/` directory

### Viewing Task Details

**Double-click any task** or **Right-click → View Details...**

**[SCREENSHOT: Task Details dialog - General Info tab]**

The Task Details dialog has two tabs:

#### General Info Tab

**[SCREENSHOT: Task Details - showing all information sections]**

Displays:

**Basic Information**:
- Task ID (with Copy button)
- Title, Agent, Status
- Priority, Task Type
- Created, Started, Completed timestamps
- Runtime (formatted as "2m 30s", "1h 15m", etc.)

**Source File**:
- Path to input document
- **Open** button to view file in default editor

**Automation Settings**:
- Auto-Complete status
- Auto-Chain status

**Result**:
- Agent's completion status or error message
- Example: `READY_FOR_DEVELOPMENT`

**Skills Section**:
- Available Skills: Shows all skills assigned to agent
- Skills Applied: Shows which skills were actually used (from log analysis)
- Helps understand what capabilities agent used

**Action Buttons**:
- **📄 View Full Log** - Opens complete task execution log
- **📁 Open Output Folder** - Opens directory with task outputs

#### Prompt Tab

**[SCREENSHOT: Task Details - Prompt tab]**

Displays the complete task description sent to the agent, including:
- Original user instructions
- Context from source file
- Skills injected into prompt
- Any additional guidance

### Cancelling a Task

**For pending or active tasks only**.

**Methods**:
1. Right-click task → **Cancel Task**
2. Select task and press `Delete`

**Confirmation dialog**: Shows task ID and asks for confirmation.

**What happens**:
- Pending task: Removed from queue
- Active task: Execution terminated (may leave partial outputs)
- Status changes to "Failed"
- Reason logged: "Cancelled by user"

### Cancelling All Tasks

**Menu**: Tasks > Cancel All Tasks

**Warning dialog**: Confirms bulk cancellation.

**What happens**:
- All pending tasks → Failed
- All active tasks → Execution terminated
- Completed tasks unaffected
- Reason logged: "Bulk cancellation"

### Clearing Finished Tasks

**Menu**: Tasks > Clear Finished...

**What gets cleared**:
- All completed tasks (✓ success)
- All failed tasks (✗ error)

**What remains**:
- Pending tasks
- Active tasks

**Use cases**:
- Cleaning up task queue
- Removing old history
- Starting fresh view

### Viewing Task Logs

**Method 1**: Task Details → **View Full Log** button  
**Method 2**: Right-click task → **View Task Log...**

**[SCREENSHOT: Task Log Viewer with search functionality]**

**Log Viewer Features**:
- Full execution transcript
- Search capability
- Shows agent's thinking process
- Skills application details
- Contract validation results
- Error messages (if any)

**Search in Logs**:
1. Enter search term in search box
2. Click **Find**
3. Matching terms highlighted in yellow
4. Navigate through matches

---

## Enhancement Generation

### What is an Enhancement?

An **enhancement** is a structured specification document that describes:
- What you want to build
- Why it's needed
- Requirements and constraints
- Success criteria
- Testing strategy
- Implementation guidance

Enhancements serve as the primary input for your multi-agent workflow.

### Generating an Enhancement

**Menu**: Enhancements > Generate...  
**Shortcut**: `Ctrl+E`

**Requirements**: Claude API key must be configured.

**[SCREENSHOT: Enhancement Generator dialog - complete view]**

#### Enhancement Generator Dialog

##### 1. Enhancement Title

**Enhancement Title** (required)
- What you're building
- Example: "User Authentication System"
- Clear and descriptive

**Filename (slug)** (auto-generated)
- Lowercase with hyphens
- Example: `user-authentication-system`
- Check **Auto-generate from title** to auto-populate
- Uncheck to manually edit

##### 2. Output Location

**Output Directory** (required)
- Where to save the enhancement
- Default: `{project-root}/enhancements/`
- Click **Browse...** to change

**Final location**: Enhancement saved to:
```
{output-directory}/{filename}/{filename}.md
```

Example:
```
enhancements/user-authentication-system/user-authentication-system.md
```

##### 3. Reference Files

**Optional** - Add related documents for context

**Use cases**:
- Existing documentation
- Related enhancement specs
- Architecture documents
- Design mockups

**Adding files**:
1. Click **Add Files...**
2. Select one or more files
3. Files listed with relative paths
4. Click **Remove** to remove selected file
5. Click **Clear All** to remove all files

**File size limit**: 100KB per file (large files truncated)

##### 4. Description

**Description** (required)
- Explain what you want to accomplish
- Why it's needed
- Who will use it
- Key requirements

**Length**: 3-4 sentences minimum for best results

**Tips**:
- Be specific about features
- Mention constraints if any
- Describe success criteria
- Include technical requirements

##### 5. Generation

Click **Generate with Claude**

**Generation Process**:
1. Shows whimsical working animation
   - "Claudeifying...", "Bedazzling...", "Cogitating..."
   - Working indicator changes every 10 seconds

**[SCREENSHOT: Claude working dialog with animation]**

2. Takes 30-60 seconds (longer for complex enhancements)
3. Uses configured model and token settings

**Model Selection Impact**:
- **Claude Opus 4**: Most comprehensive, takes longer (16K output)
- **Claude Sonnet 4.5**: Best balance (8K output) - recommended
- **Claude Haiku 4**: Fastest, shorter output (8K output)

#### Preview and Edit

**Preview Window** opens with generated content:

**[SCREENSHOT: Enhancement preview window with generated content]**

**Review the enhancement**:
- Comprehensive markdown document
- Includes:
  - Overview and user stories
  - Functional and non-functional requirements
  - MVP scope
  - Constraints and limitations
  - Success criteria and acceptance tests
  - Testing strategy
  - Implementation guidance

**Edit if needed**:
- Content is editable in preview
- Modify any section
- Add or remove requirements
- Adjust scope

**Actions**:

1. **💾 Save**
   - Creates directory structure
   - Saves markdown file
   - Shows success message with file path
   - Ready to create tasks from this enhancement

2. **🔄 Regenerate**
   - Discards current content
   - Generates new version
   - Useful if result doesn't meet expectations

3. **Cancel**
   - Discards enhancement
   - No files created

### Using Generated Enhancements

After saving an enhancement:

1. Create a task: Tasks > Create Task... (`Ctrl+N`)
2. Set **Source File** to your enhancement file
3. Start with **Requirements Analyst** agent
4. Enable **Auto Complete** and **Auto Chain**
5. Click **Create & Start**

The workflow will automatically progress through all agents.

---

## Agent Management

### Understanding Agents

**Agents** are specialized AI assistants that perform specific roles in your workflow. Each agent:
- Has a defined role and responsibilities
- Uses specific tools (bash, edit, mcp_*, etc.)
- Has assigned skills for specialized tasks
- Follows a contract defining inputs and outputs
- Chains to next agent based on completion status

### Viewing Agents

**Menu**: Agents > Manage Agents...

**[SCREENSHOT: Agent Manager dialog showing list of agents]**

The Agent Manager shows all agents in a table:

| Column | Description |
|--------|-------------|
| **Name** | Display name (e.g., "Requirements Analyst") |
| **File** | Filename slug (e.g., "requirements-analyst") |
| **Skills** | Number of assigned skills |
| **Description** | Brief role description |

**Actions**:
- **Double-click** agent to edit
- **Create New Agent** - Add custom agent
- **Edit Selected** - Modify agent configuration
- **Delete Selected** - Remove agent (with confirmation)
- **Refresh** - Reload from files

### Creating a New Agent

Click **Create New Agent** in Agent Manager.

**[SCREENSHOT: Agent Details dialog - Basic Info tab]**

The Agent Details dialog has four tabs:

#### Tab 1: Basic Info

**Agent Name** (required)
- Display name
- Example: "Security Reviewer"

**File Name (slug)** (auto-generated)
- Lowercase with hyphens
- Check **Auto** to auto-generate from name
- Example: `security-reviewer`

**Description** (required)
- Brief role description
- One sentence explaining what agent does

**Role Definition** (required)
- Detailed responsibilities and process
- Click **Generate with Claude** for AI-assisted creation
- Should include:
  - Role and purpose
  - Core responsibilities
  - Workflow steps
  - Output standards
  - Success criteria
  - Scope boundaries (DO/DON'T)

#### Tab 2: Workflow

**[SCREENSHOT: Agent Details dialog - Workflow tab]**

**Workflow Role** (required)
- Select from standard roles:
  - **analysis** - Requirements analysis
  - **technical_design** - Architecture and design
  - **implementation** - Code implementation
  - **testing** - Test creation and execution
  - **documentation** - Documentation writing
  - **integration** - External system integration

**Output Directory** (required)
- Where agent saves outputs
- Example: `security-review`
- Auto-populated when workflow role selected

**Root Document** (required)
- Main output filename
- Example: `security_report.md`
- Auto-populated when workflow role selected

**Success Status Code** (required)
- Status code on successful completion
- Examples:
  - `READY_FOR_DEVELOPMENT`
  - `READY_FOR_IMPLEMENTATION`
  - `TESTING_COMPLETE`

**Next Agent** (required)
- Which agent executes next
- Select from available agents or "(none - workflow ends)"

**Metadata Required**
- Check to require YAML frontmatter in outputs
- Recommended: Keep checked

#### Tab 3: Tools

**[SCREENSHOT: Agent Details dialog - Tools tab]**

**Agent Personas** (quick select)
- Pre-configured tool sets
- Options:
  - Analyst
  - Architect
  - Developer
  - Tester
  - Documenter
- Selecting persona checks appropriate tools

**Tool Selection**
- Check tools agent can use
- Available tools:
  - **bash** - Execute shell commands
  - **edit** - Create/modify files
  - **mcp_** tools - External integrations
  - **str_replace** - Text replacement
- At least one tool required

#### Tab 4: Skills

**[SCREENSHOT: Agent Details dialog - Skills tab with filtering and preview]**

**Skill Categories**
- Filter skills by category using dropdown
- Categories:
  - Testing
  - Security
  - Documentation
  - Performance
  - Code Quality
  - etc.

**Assigning Skills**
- Check boxes to assign skills to agent
- Skills provide specialized capabilities
- Examples:
  - Complexity Analysis
  - Security Assessment
  - Performance Optimization
  - Test Coverage Analysis

**Preview Skills Prompt**
- Shows complete skills section that will be injected
- Previews actual content agent will receive

**Skills Summary**
- Shows count of selected skills
- Updates as you check/uncheck

### Editing an Existing Agent

1. Select agent in Agent Manager
2. Click **Edit Selected** or double-click agent
3. Modify any settings across tabs
4. Click **Save Agent**

**What gets updated**:
- `agents.json` - Agent list
- `{agent-file}.md` - Agent markdown file
- `AGENT_CONTRACTS.json` - Contract definition

### Deleting an Agent

1. Select agent in Agent Manager
2. Click **Delete Selected**
3. Confirm deletion

**Warning**: This removes:
- Agent from `agents.json`
- Contract from `AGENT_CONTRACTS.json`
- Agent markdown file (`.claude/agents/{agent-file}.md`)

**Cannot be undone**.

---

## Skills System

### What are Skills?

**Skills** are reusable capability modules that enhance agent abilities. Skills:
- Provide specialized knowledge
- Add analysis capabilities
- Enable specific techniques
- Are injected into agent prompts
- Can be assigned to multiple agents

### Browsing Skills

**Menu**: Skills > Browse Skills...  
**Shortcut**: `Ctrl+K`

**[SCREENSHOT: Skills Viewer dialog showing skills list and details]**

The Skills Viewer shows:

**Left Panel - Skills List**
- All available skills in table
- Columns: Name, Category, Directory
- Click skill to view details

**Right Panel - Skill Details**
- **Skill name** and description
- **Content preview** - Full skill prompt
- **Agents Using This Skill** - Which agents have it assigned

**Filter by Category**
- Dropdown at top
- Categories:
  - Testing
  - Security
  - Documentation
  - Performance
  - Code Quality
  - AI Prompting
  - Architecture
  - And more...

### Viewing Agent Skills Summary

**Menu**: Skills > View Agent Skills...

Shows a text report of all agents and their assigned skills:

```
Requirements Analyst:
  • Requirements Validation (testing)
  • Scope Analysis (architecture)

Architect:
  • System Design (architecture)
  • Performance Analysis (performance)
  
...
```

Useful for understanding skill distribution across agents.

---

## Workflow Visualization

### Understanding Workflows

A **workflow** is the sequence of agents that process an enhancement:

```
Requirements Analyst → Architect → Implementer → Tester → Documenter
```

Each agent:
1. Receives input from previous agent
2. Performs its role
3. Produces outputs
4. Validates against contract
5. Chains to next agent (if auto-chain enabled)

### Viewing Active Workflows

**Menu**: Workflows > View Active Workflows...  
**Shortcut**: `Ctrl+W`

**[SCREENSHOT: Workflow State Viewer showing multiple active workflows]**

Shows visual progress for each enhancement being worked on.

#### Workflow Display

**[SCREENSHOT: Close-up of single workflow showing all agent states]**

**For each active enhancement**:

**Progress Bar**
- Shows percentage complete
- Example: "60% complete"
- Based on completed agents

**Agent Steps**
Each agent shows status with icon:
- **✓ Green** - Completed successfully
- **→ Orange** - Currently active
- **○ Blue** - Pending (not started)
- **✗ Red** - Failed
- **Gray** - Not started

**Agent Runtime**
- Shows execution time for completed agents
- Format: "(completed, 2m 30s)"

**Current Status**
- Overall workflow state:
  - **IN PROGRESS** - Agent currently executing
  - **WAITING** - Ready for next agent
  - **BLOCKED** - Failed task blocking progress
  - **COMPLETE** - All agents finished

**Next Agent**
- Shows which agent will execute next
- Only shown when workflow is waiting

#### Example Workflow View

```
Enhancement: user-authentication-system

60% complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Requirements Analyst (completed, 3m 15s)
✓ Architect (completed, 5m 42s)
✓ Implementer (completed, 12m 8s)
→ Tester (active)
○ Documenter

Status: IN PROGRESS - Tester
```

### Workflow States Explained

**READY**
- No agents have started yet
- Waiting for first task to be created

**IN PROGRESS**
- One or more agents are actively executing
- Workflow progressing normally

**WAITING**
- Previous agent completed
- Ready for next agent task to be created
- Requires manual action if auto-chain disabled

**BLOCKED**
- An agent task failed
- Workflow cannot continue
- Requires intervention (fix error, restart task)

**COMPLETE**
- All agents in workflow finished successfully
- Enhancement fully processed

---

## Workflow Template Management

### What are Workflow Templates?

**Workflow templates** are pre-configured workflow patterns that can be applied when creating tasks. Templates define:
- Starting agent
- Priority level
- Task type
- Whether auto-complete and auto-chain should be enabled

Templates make it quick to start common workflows without manually configuring each setting.

### Viewing Workflow Templates

**Menu**: Workflows > Manage Workflow Templates...

**[SCREENSHOT: Workflow Template Manager showing list of templates]**

The Workflow Template Manager shows all available templates:

| Column | Description |
|--------|-------------|
| **Name** | Template display name |
| **Slug** | Template identifier |
| **Icon** | Visual indicator (emoji) |
| **First Agent** | Which agent starts the workflow |

### Built-in Templates

CMAT includes several standard templates:

**📋 Full Feature**
- Starts with: Requirements Analyst
- Priority: High
- Type: Analysis
- Auto-complete: Yes
- Auto-chain: Yes
- Use for: Complete feature development from requirements through documentation

**🐛 Bug Fix**
- Starts with: Implementer
- Priority: High
- Type: Implementation
- Auto-complete: Yes
- Auto-chain: Yes (skips Requirements Analyst)
- Use for: Fixing bugs in existing code

**🔥 Hotfix**
- Starts with: Implementer
- Priority: Critical
- Type: Implementation
- Auto-complete: Yes
- Auto-chain: No (single agent only)
- Use for: Emergency fixes that need immediate deployment

**🔧 Refactoring**
- Starts with: Implementer
- Priority: Normal
- Type: Implementation
- Auto-complete: Yes
- Auto-chain: Yes (goes to Tester, skips Requirements/Architect)
- Use for: Code improvements without new features

### Creating a Custom Template

Click **Create New Template** in the Workflow Template Manager.

**[SCREENSHOT: Template Details dialog]**

#### Template Configuration

**Name** (required)
- Display name shown in UI
- Example: "Security Audit"

**Slug** (required)
- Unique identifier
- Lowercase with hyphens
- Example: `security-audit`

**Icon** (optional)
- Emoji to display with template
- Example: 🔒
- Makes templates visually distinct

**Description** (required)
- Explains when to use this template
- Shown as tooltip in task creation
- Example: "For security review and vulnerability assessment"

**First Agent** (required)
- Which agent starts this workflow
- Select from available agents
- Example: Implementer, Tester, etc.

**Priority** (required)
- Default priority for tasks using this template
- Options: Critical, High, Normal, Low

**Task Type** (required)
- Default task type
- Options: Analysis, Technical Analysis, Implementation, Testing, Documentation, Integration

**Auto Complete** (checkbox)
- Whether tasks auto-complete without user confirmation
- Recommended: Check for trusted workflows

**Auto Chain** (checkbox)
- Whether to automatically create next agent's task
- Recommended: Check for multi-agent workflows

### Editing a Template

1. Select template in Template Manager
2. Click **Edit Selected** or double-click template
3. Modify any settings
4. Click **Save Template**

**What gets updated**:
- `.claude/queues/workflow_templates.json`
- Template immediately available in task creation

### Deleting a Template

1. Select template in Template Manager
2. Click **Delete Selected**
3. Confirm deletion

**Note**: Built-in templates cannot be deleted (only custom templates).

### Using Templates in Task Creation

When creating a task:

1. Select a template from the **Quick Start Workflow** dropdown
2. Template auto-fills:
   - Agent field
   - Priority field
   - Task Type field
   - Auto-complete checkbox
   - Auto-chain checkbox
3. You can still override any auto-filled values
4. Add title, source file, and description as usual
5. Create task normally

**Benefit**: Saves time and ensures consistent workflow patterns across your project.

---

## Integration Dashboard

### What is Integration?

**Integration** manages synchronization with external systems:
- GitHub Issues
- Jira Tickets
- Confluence Pages
- Slack Notifications (future)

Integration tasks are automatically created for completed workflow stages.

### Opening Integration Dashboard

**Menu**: Integration > Integration Dashboard...  
**Shortcut**: `Ctrl+I`

**[SCREENSHOT: Integration Dashboard showing statistics and task sync status]**

### Dashboard Components

#### Statistics Bar

Shows counts:
- **Total** - All completed tasks
- **Synced** - Tasks linked to external systems (green)
- **Unsynced** - Tasks awaiting sync (orange)
- **Failed** - Sync failures (red)

#### Integration Table

Columns:

| Column | Description |
|--------|-------------|
| **Enhancement** | Enhancement name |
| **Task ID** | Task identifier |
| **Agent** | Which agent completed task |
| **Status** | Task completion status |
| **GitHub** | Issue number (#123) or — |
| **Jira** | Ticket ID (PROJ-456) or — |
| **Confluence** | Page status (✓) or — |
| **Sync Status** | Complete, Partial, Not Synced, Failed |

#### Row Color Coding

- **Light green** - Fully synced
- **Light yellow** - Not synced yet
- **Light red** - Sync failed

### Actions

**Sync Individual Task**:
1. Right-click task
2. Select "Sync to External Systems"
3. Creates integration task

**Sync All Unsynced**:
1. Click **Sync All Unsynced** button
2. Confirms action
3. Creates integration tasks for all unsynced completed tasks

**View External Links**:
1. Right-click task with external links
2. Select "Open GitHub Issue #123" or "Open Jira Ticket PROJ-456"
3. Opens in browser (requires URL configuration)

**Refresh**:
- Click **Refresh** to reload sync status
- Auto-updates when tasks complete

### Menu Option

**Menu**: Integration > Sync All Unsynced Tasks

Same as clicking **Sync All Unsynced** button in dashboard.

---

## Settings and Configuration

### Claude API Settings

**Menu**: Settings > Claude Settings

**[SCREENSHOT: Claude API Settings dialog]**

Configure Claude API for AI-powered features.

#### API Key Section

**Your Claude API key**:
1. Get key from [console.anthropic.com](https://console.anthropic.com)
2. Paste into API Key field
3. Check **Show API Key** to reveal characters
4. Uncheck to hide (shows • • •)

**Security**: API key stored locally in `~/.claude_queue_ui/settings.json`

#### Model Selection

**Choose which Claude model to use**:

Available models:

| Model | Description | Max Tokens | Speed |
|-------|-------------|------------|-------|
| **Claude Opus 4** | Most capable | 16,384 | Slower |
| **Claude Sonnet 4.5** | Smartest, efficient | 8,192 | Fast |
| **Claude Sonnet 4** | Balanced | 8,192 | Fast |
| **Claude Haiku 4** | Most cost-effective | 8,192 | Fastest |

**Recommendation**: 
- Use **Sonnet 4.5** for most tasks (default)
- Use **Opus 4** for complex enhancement generation
- Use **Haiku 4** for simple, quick generations

#### Output Token Limit

**Maximum tokens for Claude's response**:
- Default: Model maximum
- Lower values: Shorter responses, faster, cheaper
- Higher values: Longer responses, may timeout

**Display shows**: "(Maximum for this model: 8,192)"

**Auto-adjustment**: Changing model updates max tokens to model's maximum

#### Request Timeout

**Maximum time to wait for response**:
- Default: 90 seconds
- Minimum: 10 seconds
- Complex enhancements may need 120-180 seconds

**Warning**: Very long timeouts (300s+) may cause UI to appear frozen

#### Actions

**Save Settings**:
- Saves all configuration
- Enables AI-powered features
- Takes effect immediately

**Reset to Defaults**:
- Resets model to Sonnet 4.5
- Resets max tokens to 8,192
- Resets timeout to 90 seconds
- Does NOT change API key

**Cancel**:
- Discards changes
- Closes dialog

### Auto-Refresh Setting

**Menu**: Settings > Auto Refresh Task List

**Toggle**: Check/uncheck to enable/disable

**When enabled**:
- Task queue refreshes automatically every 3 seconds
- Status bar shows: `Auto-refresh: ✓ ON (3s)`
- Useful for monitoring active tasks

**When disabled**:
- Task queue updates only when you click Refresh or press F5
- Status bar shows: `Auto-refresh: OFF`
- Reduces system load

**Recommendation**: Enable when running tasks, disable otherwise

---

## Keyboard Shortcuts

### Global Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Connect to project |
| `Ctrl+Q` | Quit application |
| `F5` | Refresh task list |
| `Escape` | Close active dialog |

### Task Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | Create new task |
| `Enter` | Start selected pending task |
| `Delete` | Cancel selected task |
| `Double-click` | View task details |

### Feature Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+E` | Generate new enhancement |
| `Ctrl+K` | Browse skills |
| `Ctrl+W` | View active workflows |
| `Ctrl+I` | Integration dashboard |
| `Ctrl+L` | View operations log |

### Context Menu

**Right-click anywhere**:
- On task: Task-specific actions
- On empty space: Create task, refresh

---

## Common Workflows

### Complete Feature Development Workflow

**Goal**: Develop a new feature from idea to documented code.

**Steps**:

1. **Generate Enhancement**
   - Press `Ctrl+E`
   - Enter title: "User Profile Management"
   - Write description of feature
   - Add reference files if available
   - Click **Generate with Claude**
   - Review and save

2. **Create Initial Task**
   - Press `Ctrl+N`
   - Title: "Analyze User Profile Requirements"
   - Agent: Requirements Analyst
   - Priority: High
   - Task Type: Analysis
   - Source: `enhancements/user-profile-management/user-profile-management.md`
   - Click **Generate with Claude** for description
   - Check **Auto Complete**
   - Check **Auto Chain**
   - Click **Create & Start**

3. **Monitor Progress**
   - Press `Ctrl+W` to view workflows
   - Watch agents progress:
     - Requirements Analyst ✓
     - Architect →
     - Implementer (pending)
     - Tester (pending)
     - Documenter (pending)

4. **Check Results**
   - Double-click completed tasks
   - View outputs in task details
   - Open output folders
   - Review logs

5. **Integration** (optional)
   - Press `Ctrl+I` for integration dashboard
   - Sync to GitHub/Jira if configured

**Duration**: 15-45 minutes depending on complexity

### Quick Bug Fix Workflow

**Goal**: Fix a bug without full workflow.

**Steps**:

1. **Create Task**
   - Press `Ctrl+N`
   - Quick Start Workflow: **🐛 Bug Fix**
   - Title: "Fix Login Validation Error"
   - Auto-fills: Implementer agent, High priority
   - Source: Point to relevant enhancement or documentation
   - Write description
   - Check **Auto Complete**
   - Uncheck **Auto Chain** (single agent)
   - Click **Create & Start**

2. **Monitor**
   - Task goes to Active
   - Implementer fixes issue
   - Task completes

3. **Verify**
   - View task details
   - Check outputs
   - Review fix in output folder

**Duration**: 5-15 minutes

### Adding a Custom Agent

**Goal**: Create a specialized agent for your needs.

**Steps**:

1. **Open Agent Manager**
   - Menu: Agents > Manage Agents...

2. **Create Agent**
   - Click **Create New Agent**

3. **Basic Info Tab**
   - Name: "API Integration Specialist"
   - Description: "Integrates with external APIs"
   - Click **Generate with Claude** for role definition
   - Edit as needed

4. **Workflow Tab**
   - Workflow Role: integration
   - Output Directory: api-integration
   - Root Document: integration_report.md
   - Success Status: INTEGRATION_COMPLETE
   - Next Agent: (none - workflow ends)

5. **Tools Tab**
   - Select persona: Developer
   - Additional tools: mcp_* tools for API access

6. **Skills Tab**
   - Assign relevant skills:
     - API Design
     - Error Handling
     - Integration Testing
   - Preview skills prompt

7. **Save**
   - Click **Save Agent**
   - Agent now available in task creation

### Monitoring Multiple Enhancements

**Goal**: Track progress across several features.

**Steps**:

1. **Generate Multiple Enhancements**
   - Create enhancement for Feature A
   - Create enhancement for Feature B
   - Create enhancement for Feature C

2. **Start All Workflows**
   - Create initial task for each
   - All with Auto Complete and Auto Chain enabled
   - Start all tasks

3. **View Workflows**
   - Press `Ctrl+W`
   - See all three workflows
   - Progress bars show completion percentage
   - Agent status shows current step

4. **Check Task Queue**
   - Main window shows all active tasks
   - Filter by enhancement (in title)
   - Double-click to view details

5. **Integration Dashboard**
   - Press `Ctrl+I`
   - See sync status across all enhancements
   - Sync all when complete

---

## Troubleshooting

### Connection Issues

#### "Not a valid CMAT project"

**Cause**: Directory structure doesn't match CMAT v3.0 requirements.

**Solutions**:
1. Verify you're selecting **project root**, not `.claude/` directory
2. Check that `.claude/scripts/cmat.sh` exists
3. Run `ls -la .claude/` to verify structure
4. If v2.0 or earlier, upgrade template first

#### "CMAT script not found"

**Cause**: Path to `cmat.sh` is invalid.

**Solutions**:
1. Use File > Connect... to browse for project
2. Don't manually edit connection path
3. Verify `cmat.sh` has execute permissions: `chmod +x .claude/scripts/cmat.sh`

### Task Issues

#### Tasks not showing

**Solutions**:
1. Click **Refresh** or press `F5`
2. Check connection status in header
3. Verify queue file exists: `.claude/queues/task_queue.json`
4. Enable auto-refresh: Settings > Auto Refresh Task List

#### Cannot start task

**Symptoms**: Start task option grayed out.

**Solutions**:
1. Task must be in "Pending" status
2. Active tasks cannot be restarted
3. Cancel task first, then recreate if needed

#### Task stuck in "Active"

**Cause**: Agent execution failed without updating status.

**Solutions**:
1. Check task log for errors
2. Cancel task
3. Fix issue in source file
4. Create new task

### AI Generation Issues

#### "No API Key" error

**Cause**: Claude API key not configured.

**Solutions**:
1. Menu: Settings > Claude Settings
2. Enter API key from console.anthropic.com
3. Save settings
4. Try generation again

#### Generation timeout

**Cause**: Complex request taking too long.

**Solutions**:
1. Settings > Claude Settings
2. Increase timeout (try 120-180 seconds)
3. Switch to faster model (Sonnet 4.5 or Haiku 4)
4. Simplify input (shorter description, fewer reference files)

#### Poor quality generation

**Solutions**:
1. Use Claude Opus 4 for complex tasks
2. Provide more detailed description
3. Add relevant reference files
4. Regenerate with different wording

### Skills Issues

#### Skills not showing for agent

**Cause**: Agent has no skills assigned.

**Solutions**:
1. Agents > Manage Agents...
2. Edit agent
3. Go to Skills tab
4. Assign skills
5. Save agent

#### "Skills system not available"

**Cause**: Missing `skills.json` file.

**Solutions**:
1. Verify file exists: `.claude/skills/skills.json`
2. If missing, reinstall CMAT template
3. Check file permissions

### Performance Issues

#### UI freezing during generation

**Cause**: Long-running API call.

**This is normal**:
- Complex enhancements take 30-60 seconds
- Watch working animation to confirm it's processing
- Don't close window, wait for completion

#### Slow refresh

**Solutions**:
1. Disable auto-refresh if not needed
2. Close other resource-intensive applications
3. Reduce number of active tasks
4. Clear finished tasks: Tasks > Clear Finished...

### Installation Issues

#### Download timeout

**Cause**: Network slow or GitHub unavailable.

**Solutions**:
1. Check internet connection
2. Try again later
3. Use VPN if GitHub blocked
4. Download template manually from GitHub

#### Permission denied during install

**Cause**: No write access to target directory.

**Solutions**:
1. Choose directory you own
2. Check directory permissions
3. Don't install to system directories
4. Try different location

---

## Getting Help

### Resources

1. **This User Guide** - Comprehensive usage instructions
2. **README.md** - Project overview and installation
3. **QUICKSTART.md** - Quick getting started guide
4. **Operations Log** (`Ctrl+L`) - Debugging tool
5. **Task Logs** - Detailed execution information

### Common Questions

**Q: How do I upgrade from CMAT v2.0?**  
A: Install CMAT template in new location, migrate enhancements manually, or follow migration guide in CMAT documentation.

**Q: Can I use without Claude API?**  
A: Yes! All features work except AI-powered generation. You'll write descriptions manually.

**Q: How much do API calls cost?**  
A: Varies by model. Sonnet 4.5 is most economical. Check Anthropic pricing for current rates.

**Q: Can I run multiple agents in parallel?**  
A: No, agents run sequentially in workflow. But multiple workflows can run simultaneously.

**Q: Where are my outputs saved?**  
A: In `enhancements/{enhancement-name}/{agent-output-dir}/`

**Q: Can I customize the workflow order?**  
A: Yes, edit `AGENT_CONTRACTS.json` to change agent chaining.

---

**For additional help, check project documentation or open an issue on GitHub.**