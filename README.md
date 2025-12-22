# Claude Multi-Agent Workflow Manager

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

A graphical user interface for managing multi-agent development workflows using the Claude Multi-Agent Development Template (CMAT) v8.2+.

I created this tool to make the creation and management of CMAT-based projects easier. Rather than using the cmat.sh script directly, users can leverage a comprehensive GUI to create tasks, manage agents with their skills, configure workflow templates, and generate enhancements for their projects.

Once installed and connected to a CMAT project, users can create 'enhancements' - well-structured specification files that include user stories, requirements, constraints, and acceptance criteria. These enhancements can then be processed through customizable multi-agent workflows, with each agent contributing its expertise to deliver comprehensive results.

Default workflows are provided for common tasks, but users can create custom workflows to suit their needs.
## Features

### Core Features
- 📋 **Task Management** - Create, start, cancel, and monitor tasks
- 🎭 **Agent Management** - Create and edit agents with visual skills assignment (simplified in v5.0)
- 🎯 **Skills Management** - Browse skills, view agent skills, preview skills prompts
- 📝 **Enhancement Generator** - AI-assisted creation of enhancement specification files
- 🤖 **AI-Powered Generation** - Generate task descriptions and enhancement specs using Claude API
- 📋 **Workflow Template Management** - Create and manage reusable workflow templates with visual editors
- 🚀 **Workflow Launcher** - Quick workflow launcher with pre-flight validation
- 🔗 **Integration Dashboard** - Monitor GitHub/Jira/Confluence sync status
- ⚙️ **Advanced Settings** - Configure Claude model, API key, and token limits
- 🎯 **Multi-Project Support** - Connect to different CMAT projects
- 🚀 **Zero External Dependencies** - Uses only Python standard library

### v2.0 Features (CMAT v8.2+ Integration)
- 🧠 **Learnings Management** - Browse, filter, add, and manage RAG system learnings
- 🤖 **Model Configuration** - Configure Claude models, pricing, and set default model
- 🔗 **Direct Python Integration** - Native Python CMAT API integration (no subprocess overhead)
- 📚 **RAG System Support** - Full support for CMAT's learning extraction and retrieval

### v1.x Features
- 🔧 **Modular Workflow Architecture** - Agents are now reusable components, workflows define orchestration
- ⚡ **Visual Workflow Template Editor** - Configure input patterns, output files, and status transitions through UI
- 🎨 **Transition Management** - Visually manage what happens when agents output specific status codes
- 📊 **Dynamic Workflow Loading** - Task creation automatically loads all user-defined workflows
- 🔍 **Workflow Context Display** - Tasks show their position in workflows with expected inputs/outputs
- ✅ **Real-time Workflow Validation** - Validates workflows before starting with clear feedback

## Requirements

- Python 3.7 or higher
- Tkinter (included with Python)
- A project using the Claude Multi-Agent Development Template v8.2+ (can be installed directly or connected to an existing project)
- Claude API key (optional, for AI-powered features)
- PyYAML (for CMAT v8.2+ Python integration)

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

<img src="assets/docs_img_task_list.png" width="80%" alt="Main Task List">

### 1. Launch the Application

```bash
python3 -m src.main
# OR
./run.py
```

### 2. Get a CMAT Project

You can either connect to an existing CMAT project or install to your project.

#### Option A: Install CMAT Template

<img src="assets/docs_img_install.png" width="80%" alt="CMAT Installer">

If you don't have a CMAT project yet, you can install one directly:

The installer:
- Downloads the latest CMAT template from GitHub
- Creates a `.claude/` folder with all necessary files
- Creates a backup if overwriting an existing installation
- Validates the installation for security and completeness

1. Click **File > Install CMAT Template...**
2. Select or enter the directory where you want to install CMAT
3. The dialog validates the directory and warns if `.claude/` already exists
4. Click **Install** to download and install CMAT from GitHub
5. Files are downloaded from the CMAT GitHub repo and installed
6. When complete, click **Connect Now** to immediately connect to the new project

#### Option B: Connect to Existing Project

If you already have a CMAT project:

1. Click **File > Connect...** (or press `Ctrl+O`)
2. Click **Browse...**
3. Navigate to your CMAT project root directory
4. Select the project root (containing `.claude/` folder)
5. The UI will validate the project structure
6. Click **Connect**

The validation checks for:
- ✓ CMAT script (`.claude/scripts/cmat.sh`)
- ✓ Task queue (`.claude/queues/task_queue.json`)
- ✓ Workflow templates (`.claude/queues/workflow_templates.json`)
- ✓ Skills system (`.claude/skills/skills.json`)
- ✓ Agents (`.claude/agents/agents.json`)

### 3. Configure Claude API (Optional but Recommended)

<img src="assets/docs_img_settings.png" width="80%" alt="Claude Settings">

For AI-powered features (highly recommended):

1. Get a Claude API key from [console.anthropic.com](https://console.anthropic.com)
2. Click **Settings > Claude Settings**
3. Enter your API key
4. Choose model (default: **Claude Sonnet 4.5** - recommended)
5. Set max tokens (default: 8192 - fine for most tasks)
6. Click **Save Settings**

You can now use:
- **Generate with Claude** in task creation
- **Enhancement Generator** for creating specs
- **Agent instructions generation** when creating agents

See the [User Guide](USER_GUIDE.md) for more detailed instructions on system operation.

### Task Management

<img src="assets/docs_img_task_create.png" width="80%" alt="Create Task">

Create standalone tasks with optional source files. Tasks auto-complete but don't auto-chain to other agents.

<img src="assets/docs_img_task_details_general.png" width="80%" alt="Task Details">

View comprehensive task details including workflow context, skills used, and full prompts sent to Claude.

## What's New in v5.0

### Architecture Changes

**v4.x**: Agents defined their own orchestration (inputs, outputs, next agents)
**v5.0**: Workflows define orchestration, agents are reusable components

### Key Benefits

- **Agent Reusability** - Same agent can work in multiple workflows with different configurations
- **Flexible Workflows** - Change workflow orchestration without modifying agents
- **Visual Workflow Editing** - Configure input patterns, outputs, and transitions through UI
- **Dynamic Workflow Loading** - Create custom workflows and they appear everywhere automatically

### New Features

1. **Workflow Template Editor** - Full visual editor for creating/editing workflows
   - Configure input patterns with placeholders
   - Set required output filenames
   - Manage status transitions visually
   - Validate workflows before saving

2. **Workflow Starter Dialog** - Quick launcher for starting workflows
   - Select workflow template
   - Choose or create enhancement spec
   - Pre-flight validation checks
   - One-click start

3. **Simplified Agent Management** - Agents are now just capabilities
   - No workflow orchestration in agent definition
   - Focus on tools and skills
   - Workflow behavior configured separately

4. **Enhanced Task Details** - Shows workflow context
   - Current step in workflow
   - Expected inputs/outputs
   - Expected status codes
   - Workflow name and position

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
- **Timeout** - Request timeout in seconds (default: 90)

Settings are persisted to `~/.claude_queue_ui/settings.json`

## Project Structure

```
ClaudeMultiAgentUI/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Main application
│   ├── config.py                  # Configuration + ClaudeConfig
│   ├── settings.py                # Settings persistence
│   ├── utils/                     # Utility modules
│   │   ├── __init__.py
│   │   ├── claude_api_client.py   # Centralized API client
│   │   ├── cmat_interface.py      # CMAT interface (v5.0)
│   │   ├── cmat_installer.py      # CMAT template installer
│   │   ├── workflow_migration_utils.py  # v4.x → v5.0 migration tools
│   │   ├── text_utils.py          # Slug conversion, validation
│   │   ├── path_utils.py          # Path utilities
│   │   └── time_utils.py          # Time formatting
│   ├── models/                    # Data models
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── agent.py
│   │   ├── workflow_template.py   # v5.0 workflow models
│   │   ├── queue_state.py
│   │   └── ...
│   └── dialogs/                   # Dialog windows
│       ├── __init__.py
│       ├── base_dialog.py         # ABC base class
│       ├── mixins/                # Dialog mixins
│       │   ├── __init__.py
│       │   └── claude_generator_mixin.py
│       ├── connect.py
│       ├── task_create.py         # v5.0 - dynamic workflows
│       ├── task_details.py        # v5.0 - workflow context
│       ├── agent_details.py       # v5.0 - simplified
│       ├── enhancement_create.py
│       ├── workflow_template_manager.py
│       ├── workflow_template_editor.py  # v5.0 - full visual editor
│       ├── workflow_step_editor.py      # v5.0 - NEW
│       ├── workflow_transition_manager.py  # v5.0 - NEW
│       ├── workflow_starter.py          # v5.0 - NEW
│       ├── workflow_viewer.py           # v5.0 - uses templates
│       ├── claude_settings.py
│       ├── working.py
│       └── ...
├── tests/                         # Unit tests
├── assets/                        # Images, icons
├── README.md
├── QUICKSTART.md
├── USER_GUIDE.md
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

## Workflow Management (v5.0)

### Creating Workflow Templates

Workflows define how agents work together to process enhancements:

1. **Workflows > Manage Templates...** → "Create New Template"
2. Enter template name and description
3. Add steps:
   - Select agent for each step
   - Configure input pattern (where step reads from)
   - Set output filename (what step creates)
   - Manage transitions (what happens on each status)
4. Save template

### Starting Workflows

Two methods to start workflows:

**Method 1: Workflow Starter (Recommended)**
1. **Workflows > Start Workflow...** (`Ctrl+Shift+W`)
2. Select workflow template from dropdown
3. Choose existing enhancement or create new one
4. Pre-flight checks validate everything
5. Click **Start Workflow**

**Method 2: Quick Start in Task Create**
1. **Tasks > Create Task...** (`Ctrl+N`)
2. Select workflow from dropdown (loads dynamically)
3. First agent and settings pre-filled
4. Enter details and create

### Monitoring Workflows

**Workflows > View Active Workflows...** (`Ctrl+W`)

- See real-time progress of all workflows
- Progress bars show completion percentage
- Agent status indicators (✓ completed, → active, ○ pending)
- Uses actual workflow templates (not hardcoded)
- Works with custom workflows of any length

## Troubleshooting

### Connection Issues

#### "Not a valid CMAT project"

**Cause**: Directory structure doesn't match CMAT v5.0 requirements.

**Solutions**:
1. Verify you're selecting **project root**, not `.claude/` directory
2. Check that `.claude/scripts/cmat.sh` exists
3. Check that `.claude/queues/workflow_templates.json` exists
4. Run `ls -la .claude/` to verify structure
5. If v4.x or earlier, workflows will load but may need updating

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

### Workflow Issues (v5.0)

#### Workflow not in dropdown

**Cause**: Workflow template not saved properly.

**Solutions**:
1. **Workflows > Manage Templates...**
2. Verify template exists in list
3. Edit template and save
4. Refresh task creation dialog

#### Step transitions not working

**Cause**: Status transitions not configured.

**Solutions**:
1. Edit workflow template
2. Edit the step that's not chaining
3. Click "Manage Transitions"
4. Add transition for the status code agent outputs
5. Save changes

#### Workflow validation errors

**Solutions**:
1. Edit workflow template
2. Click "Validate Workflow"
3. Review error messages
4. Fix missing input/output configurations
5. Ensure transition targets exist

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

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Related Projects

- [Claude Multi-Agent Template](https://github.com/dasien/ClaudeMultiAgentTemplate) - The multi-agent system this UI manages

---

**Built with ❤️ for the Claude Multi-Agent Development Template**