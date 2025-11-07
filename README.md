# Multi-Agent Task Queue Manager

A graphical user interface for managing multi-agent development workflows using the Claude Multi-Agent Development Template (CMAT).

![Version](https://img.shields.io/badge/version-1.0.3-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## Features

### Core Features
- 📋 **Task Management** - Create, start, cancel, and monitor tasks
- 🤖 **AI-Powered Generation** - Generate task descriptions and enhancement specs using Claude API
- ⚡ **Quick Actions** - Create & Start button for immediate task execution
- 🔧 **Auto Complete & Chain** - Automated task completion and chaining workflows
- 🔄 **Auto-Refresh** - Real-time updates of task status
- 🎯 **Multi-Project Support** - Connect to different CMAT projects
- 📊 **Operations Log Viewer** - Track all queue operations
- 🎨 **Clean UI** - Simple, intuitive Tkinter interface
- 🚀 **Zero External Dependencies** - Uses only Python standard library

###  Enhanced Features
- 🎯 **Skills Management** - Browse skills, view agent skills, preview skills prompts
- 📝 **Enhancement Generator** - AI-assisted creation of enhancement specification files
- 🔄 **Workflow Visualization** - View active workflows and their progress
- 🔗 **Integration Dashboard** - Monitor GitHub/Jira/Confluence sync status
- ⚙️ **Advanced Settings** - Configure Claude model, API key, and token limits
- 🎭 **Agent Management** - Create, edit, and delete agents with visual skills assignment
- ✨ **Whimsical Working Indicators** - Fun "Claudeifying..." animations during API calls

## Screenshots

### Main Window
The main window shows all tasks across all statuses (pending, active, completed, failed) in a single table view.

![Main Window](assets/docs_img_main.png)

### Create Task
Create new tasks with AI-powered description generation, agent selection, and automated workflow options.

![Create Task Dialog](assets/docs_img_create_task.png)

### Task Details
Double-click any task to view complete details including description, timestamps, and access to logs.

![Task Details](assets/docs_img_task_details.png)

## Requirements

- Python 3.7 or higher
- Tkinter (included with Python)
- A project using the Claude Multi-Agent Development Template  (or install one via the UI)
- Claude API key (optional, for AI-powered features)

## Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/ClaudeMultiAgentUI.git
cd ClaudeMultiAgentUI

# Run directly
python3 -m src.main

# Or use the launcher script
./run.py
```

## Usage

### 1. Launch the Application

```bash
python3 -m src.main
# OR
./run.py
```

### 2. Get a CMAT Project

You can either connect to an existing CMAT project or install a new one.

#### Option A: Install CMAT Template (NEW!)

If you don't have a CMAT project yet, you can install one directly:

1. Click **File > Install CMAT Template...**
2. Select or enter the directory where you want to install CMAT
3. The dialog validates the directory and warns if `.claude/` already exists
4. Click **Install** to download and install CMAT from GitHub
5. Watch the progress bar as files are downloaded and installed
6. When complete, click **Connect Now** to immediately connect to the new project

The installer:
- Downloads the latest CMAT template from GitHub
- Creates a `.claude/` folder with all necessary files
- Creates a backup if overwriting an existing installation
- Validates the installation for security and completeness

#### Option B: Connect to Existing Project

If you already have a CMAT project:

1. Click **File > Connect...**
2. Click **Browse...**
3. Navigate to your CMAT project root directory
4. Select the project root (containing `.claude/` folder)
5. The UI will validate the  project structure
6. Click **Connect**

The validation checks for:
- ✓ CMAT script (`.claude/scripts/cmat.sh`)
- ✓ Task queue (`.claude/queues/task_queue.json`)
- ✓ Agent contracts (`.claude/AGENT_CONTRACTS.json`)
- ✓ Skills system (`.claude/skills/skills.json`)
- ✓ Agents (`.claude/agents/agents.json`)

### 3. Configure Claude API (Optional but Recommended)

For AI-powered features (enhancement generation, task descriptions, agent role definitions):

1. Click **Settings > Claude Settings**
2. Enter your Claude API key (get one at console.anthropic.com)
3. Choose your preferred model:
   - **Claude Opus 4** - Most capable, 16K output (best for long enhancements)
   - **Claude Sonnet 4.5** - Smartest, efficient, 8K output (recommended default)
   - **Claude Sonnet 4** - Balanced performance, 8K output
   - **Claude Haiku 4** - Fastest and most cost-effective, 8K output
4. Set max tokens (defaults to model maximum)
5. Click **Save Settings**

### 4. Managing Tasks

#### Create a Task
- **Method 1**: Right-click in empty space → **Create Task...**
- **Method 2**: Press `Ctrl+N`
- **Method 3**: Menu: **Tasks > Create Task...**

**Fill in the form:**
- **Title**: Short description of the task
- **Quick Start Workflow** (optional): Select a pre-configured workflow
  - 📋 Full Feature
  - 🐛 Bug Fix
  - 🔥 Hotfix
  - 🔧 Refactoring
- **Agent**: Select from available agents (shows agent's skills)
- **Priority**: Critical, High, Normal, or Low
- **Task Type**: Analysis, Technical Analysis, Implementation, Testing, Documentation, or Integration
- **Source File**: Browse to select (usually a markdown enhancement file)
- **Description**: Task details
  - Click **Generate with Claude** for AI-assisted creation
  - Includes agent skills and source file content in context
- **Automation Options**:
  - **Auto Complete**: Complete without prompting
  - **Auto Chain**: Automatically progress to next agent

**Choose an action:**
- **Create Task**: Add to queue as pending
- **Create & Start**: Add and immediately execute
- **Cancel** or **Escape**: Discard

#### Start a Task
- Right-click on a pending task → **Start Task**
- Or: Select a task and press `Enter`
- The agent executes in background
- Task status updates automatically

#### Cancel a Task
- Right-click on a pending/active task → **Cancel Task**
- Or: Select a task and press `Delete`
- Confirm the cancellation

#### View Task Details
- Double-click any task
- Or: Right-click → **View Details...**
- Shows:
  - Complete task information
  - Skills available vs. skills applied
  - Contract validation status
  - Expected outputs
  - External integration (GitHub/Jira)
  - Access to task logs

#### Cancel All Tasks
- Right-click in empty space → **Cancel All Tasks**
- Confirms before cancelling all pending and active tasks

### 5. Enhancement Generator (NEW!)

Create well-structured enhancement specification files with Claude's help:

1. Click **Enhancements > Generate...** or press `Ctrl+E`
2. Fill in the form:
   - **Enhancement Title**: What you're building
   - **Filename**: Auto-generated from title (lowercase-with-hyphens)
   - **Output Directory**: Where to save (defaults to `enhancements/`)
   - **Reference Files** (optional): Add related docs for context
   - **Description**: Describe what you want (3-4 sentences)
3. Click **Generate with Claude**
4. Watch the whimsical working indicator ("Bedazzling...", "Cogitating...")
5. Preview the generated enhancement specification
6. Edit if needed, then click **💾 Save**

The generated file includes:
- Overview and user stories
- Requirements (functional, non-functional, MVP)
- Constraints and limitations
- Success criteria and acceptance tests
- Testing strategy
- Implementation guidance for agents

### 6. Agent Management

**View and Manage Agents:**
- Click **Agents > Manage Agents...**
- See all agents with skill counts
- Double-click to edit

**Create New Agent:**
- Click **Create New Agent**
- Fill in:
  - Agent Name (auto-generates filename slug)
  - Description
  - Role Definition (use **Generate with Claude**)
- Assign workflow role, tools, and skills
- Set outputs and status codes
- Save to create agent files and update contracts

**Edit Agent:**
- Select agent → **Edit Selected**
- Modify configuration
- Save changes

**Delete Agent:**
- Select agent → **Delete Selected**
- Confirms before removing from all files

### 7. Skills System

**Browse All Skills:**
- Click **Skills > Browse Skills...** or press `Ctrl+K`
- Filter by category
- View skill content and descriptions
- See which agents use each skill

**View Agent Skills:**
- Click **Skills > View Agent Skills...**
- See summary of all agents and their assigned skills

### 8. Workflows

**Visualize Active Workflows:**
- Click **Workflows > View Active Workflows...** or press `Ctrl+W`
- See progress for each enhancement
- View which agents are complete/active/pending
- Track workflow status

Standard workflow: Requirements Analyst → Architect → Implementer → Tester → Documenter

### 9. Integration Dashboard

**Monitor External System Sync:**
- Click **Integration > Integration Dashboard...** or press `Ctrl+I`
- View GitHub issues, Jira tickets, Confluence pages
- See sync status for each task
- Sync tasks to external systems

### 10. Logs

**Operations Log:**
- Click **Logs > View Operations Log** or press `Ctrl+L`
- View all queue operations
- Search through logs
- Useful for debugging

**Task Logs:**
- Right-click task → **View Task Log...**
- Or: Task Details → **View Log** button
- Search within log
- See detailed agent execution

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Connect to project |
| `Ctrl+N` | Create new task |
| `Ctrl+E` | Generate new enhancement |
| `Ctrl+K` | Browse skills |
| `Ctrl+W` | View active workflows |
| `Ctrl+I` | Integration dashboard |
| `Ctrl+L` | View operations log |
| `F5` | Refresh task list |
| `Ctrl+Q` | Quit application |
| `Delete` | Cancel selected task |
| `Enter` | Start selected task (if pending) |
| `Escape` | Close active dialog |

## Menu Structure

- **File**
  - Install CMAT Template... ⭐ NEW
  - Connect... (`Ctrl+O`)
  - Quit (`Ctrl+Q`)

- **Tasks**
  - Create Task... (`Ctrl+N`)
  - Cancel All Tasks
  - Refresh List (`F5`)

- **Agents**
  - Manage Agents...

- **Skills**
  - Browse Skills... (`Ctrl+K`)
  - View Agent Skills...

- **Enhancements** ⭐ NEW
  - Generate... (`Ctrl+E`)

- **Workflows**
  - View Active Workflows... (`Ctrl+W`)

- **Integration**
  - Integration Dashboard... (`Ctrl+I`)
  - Sync All Unsynced Tasks

- **Logs**
  - View Operations Log (`Ctrl+L`)

- **Settings**
  - Claude Settings
  - Auto Refresh Task List

- **About**
  - About Task Queue UI

## Configuration

### Application Settings

The application uses sensible defaults in `src/config.py`:

- **Auto-refresh interval** - Default: 3 seconds
- **Max log lines** - Default: 1000 lines
- **Window size** - Default: 1200x750
- **Status colors** - Blue (pending), Orange (active), Green (completed), Red (failed)
- **Priority colors** - Red (critical), Orange (high), Black (normal), Gray (low)

### Claude API Settings

Configure via **Settings > Claude Settings**:

- **API Key** - Your Claude API key from console.anthropic.com
- **Model** - Choose from Opus 4, Sonnet 4.5, Sonnet 4, or Haiku 4
- **Max Tokens** - Output token limit (defaults to model maximum)

Settings are persisted to `~/.claude_queue_ui/settings.json`

## Architecture

### Modern Object-Oriented Design

The application uses a clean, Pythonic architecture:

- **Abstract Base Classes** - All dialogs inherit from `BaseDialog` (ABC)
- **Mixins** - `ClaudeGeneratorMixin` for AI-powered dialogs
- **Utilities** - Shared functions for common operations
- **Single Source of Truth** - Centralized configuration
- **Type Safety** - Abstract methods enforce contracts

### Project Structure

```
ClaudeMultiAgentUI/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Main application
│   ├── config.py                  # Configuration + ClaudeConfig
│   ├── queue_interface.py         # CMAT interface
│   ├── settings.py                # Settings persistence
│   ├── utils/                     # Utility modules
│   │   ├── __init__.py
│   │   ├── claude_api_client.py   # Centralized API client
│   │   ├── text_utils.py          # Slug conversion, validation
│   │   ├── path_utils.py          # Path utilities
│   │   └── time_utils.py          # Time formatting
│   ├── models/                    # Data models
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── agent.py
│   │   ├── queue_state.py
│   │   └── ...
│   └── dialogs/                   # Dialog windows
│       ├── __init__.py
│       ├── base_dialog.py         # ABC base class
│       ├── mixins/                # Dialog mixins
│       │   ├── __init__.py
│       │   └── claude_generator_mixin.py
│       ├── connect_dialog.py
│       ├── create_task_enhanced.py
│       ├── enhancement_generator_dialog.py
│       ├── claude_settings_dialog.py
│       ├── claude_working_dialog.py
│       └── ...
├── tests/                         # Unit tests
├── assets/                        # Images, icons
├── README.md
├── QUICKSTART.md
├── requirements.txt
├── setup.py
└── LICENSE
```

## Multi-Project Workflow

The UI supports managing multiple CMAT projects:

1. **Connect** to Project A
2. Work with Project A (tasks, agents, enhancements)
3. **File > Connect...** to switch to Project B
4. Work with Project B
5. Switch back anytime

The last connection is saved and auto-reconnects on launch.

## Troubleshooting

### "CMAT script not found"
- Ensure you're selecting the project root directory
- Path should contain: `.claude/scripts/cmat.sh`
- This is a CMAT project structure

### "Not a valid CMAT project"
- Check that `.claude/scripts/cmat.sh` exists
- Verify `.claude/AGENT_CONTRACTS.json` exists
- Verify `.claude/skills/skills.json` exists
- If you have v2.0 or earlier, upgrade your template first

### Tasks not showing
- Click **Refresh** or press `F5`
- Check connection status in header bar
- Enable auto-refresh: **Settings > Auto Refresh Task List**

### Agent not starting
- Starting a task launches the agent via `cmat.sh` in background
- Task shows "Active" status immediately
- Agent execution may take several minutes
- Task status updates automatically when complete
- Check the operations log (`Ctrl+L`) for errors

### "Generate with Claude" not working
- Configure API key: **Settings > Claude Settings**
- Get API key from: console.anthropic.com
- Check internet connection
- Verify API key is valid

### Enhancement Generator timeout
- Long enhancements may take 30-60 seconds
- Opus 4 is slower but generates longer content
- Sonnet 4.5 is faster for most tasks
- Watch the working animation - it's still processing!

### Cross-Platform Issues

**macOS**: 
- Right-click may require `Ctrl+Click` or two-finger tap
- File dialogs use native macOS interface

**Windows**: 
- Ensure Git Bash or WSL is installed for bash script execution
- File paths may need forward slashes

**Linux**: 
- Should work out of the box
- If Tkinter not found: `sudo apt-get install python3-tk`

## Advanced Features

### Quick Start Workflows

Use pre-configured workflows when creating tasks:

- **📋 Full Feature** - Complete development workflow (all agents)
- **🐛 Bug Fix** - Skip documentation phase
- **🔥 Hotfix** - Emergency fix, skip analysis
- **🔧 Refactoring** - Code improvement, skip requirements

These automatically set agent, priority, and enable auto-chain.

### Agent Personas

When creating agents, use quick select personas:
- Analyst
- Architect  
- Developer
- Tester
- Documenter

Each persona pre-selects appropriate tools.

### Skills Assignment

Assign skills to agents for specialized capabilities:
- Filter skills by category
- Preview skills prompt before assigning
- See which agents use each skill
- Skills are automatically included in agent prompts

## API Integration

### Claude API Features

With Claude API configured, you can:

1. **Generate Enhancement Specs** - Create detailed enhancement files from brief descriptions
2. **Generate Task Descriptions** - Create comprehensive task descriptions from title and source file
3. **Generate Agent Roles** - Create agent role definitions from name and description

All features use configurable model and token settings.

### Cost Management

Control API costs via **Settings > Claude Settings**:
- Choose faster/cheaper models (Haiku 4) for simple tasks
- Choose more capable models (Opus 4) for complex enhancements
- Adjust max tokens to limit response length
- Default: Sonnet 4.5 with 8K tokens (good balance)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development

The codebase follows modern Python best practices:

- **Abstract Base Classes** for type safety
- **Mixins** for cross-cutting concerns
- **Utilities** for shared functionality
- **Single Responsibility Principle**
- **DRY (Don't Repeat Yourself)**

See `src/dialogs/base_dialog.py` for the dialog architecture pattern.

## License

MIT License - see LICENSE file for details

## Related Projects

- [Claude Multi-Agent Template ](https://github.com/yourusername/ClaudeMultiAgentTemplate) - The multi-agent system this UI manages

## Changelog

### Version 1.0.3 (2025-01-XX)
- Added Install CMAT Template dialog with GitHub download
- Added Enhancement Generator with AI assistance
- Added Claude Settings dialog with model selection
- Added Skills viewer and management
- Added Workflow state visualization
- Added Integration dashboard
- Refactored all dialogs to use BaseDialog ABC
- Added ClaudeGeneratorMixin for AI features
- Added whimsical working indicators
- Added utilities (ClaudeAPIClient, PathUtils, TimeUtils, TextUtils)
- Updated to CMAT compatibility
- Improved menu structure
- Added Escape key to close dialogs
- Improved keyboard shortcuts

### Version 1.0.0 (2025-01-XX)
- Initial release
- Task management (create, start, cancel)
- Multi-project support via connection dialog
- Operations log viewer
- Task details viewer
- Auto-refresh functionality
- Context menus and keyboard shortcuts

---

**Built with ❤️ for the Claude Multi-Agent Development Template**