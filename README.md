# Multi-Agent Task Queue Manager

![Version](https://img.shields.io/badge/version-1.0.8-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

A graphical user interface for managing multi-agent development workflows using the Claude Multi-Agent Development Template (CMAT).

I created this tool as a way to make the creation and management of CMAT based projects easier.  Rather than using the 
cmat.sh script directly, I wanted to have a GUI that would allow users to create tasks, manage agents (and their skills), and create enhancements for a user's project.

Once installed and connected to a CMAT project, the first thing a user might do is create an 'enhancement.'  This is a well-structured specification file that includes the user story, requirements, constraints, and acceptance criteria.  The user can then use this file to create a task in the queue.
With the task created, the user can start the task and a series of agents will work on the task.  The user can monitor the progress of the task in the task viewer (the main screen).
As each agent completes its work, it will output a log file and documentation according to agent's role and workflow.


## Features

### Core Features
- 📋 **Task Management** - Create, start, cancel, and monitor tasks
- 🎭 **Agent Management** - Create, edit, and delete agents with visual skills assignment
- 🎯 **Skills Management** - Browse skills, view agent skills, preview skills prompts
- 📝 **Enhancement Generator** - AI-assisted creation of enhancement specification files
- 🤖 **AI-Powered Generation** - Generate task descriptions and enhancement specs using Claude API
- 🔄 **Workflow Visualization** - View active workflows and their progress
- 🔗 **Integration Dashboard** - Monitor GitHub/Jira/Confluence sync status
- ⚙️ **Advanced Settings** - Configure Claude model, API key, and token limits
- 🎯 **Multi-Project Support** - Connect to different CMAT projects
- 🚀 **Zero External Dependencies** - Uses only Python standard library

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
- A project using the Claude Multi-Agent Development Template  (can be installed directly or connected to an existing project)
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

You can either connect to an existing CMAT project or install to your project.

#### Option A: Install CMAT Template (NEW!)

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
3. Choose your preferred model
4. Set max tokens (defaults to model maximum)
5. Click **Save Settings**

See the [User Guide](USER_GUIDE.md) for more detailed instructions on system operation.


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
│   │   ├── cmat_interface.py      # CMAT interface
│   │   ├── cmat_installer.py      # CMAT template installer
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

## License

MIT License - see LICENSE file for details

## Related Projects

- [Claude Multi-Agent Template ](https://github.com/dasien/ClaudeMultiAgentTemplate) - The multi-agent system this UI manages

---

**Built with ❤️ for the Claude Multi-Agent Development Template**