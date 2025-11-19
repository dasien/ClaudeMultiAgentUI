# Quick Start Guide

This document describes the process to get up and running with the Multi-Agent Task Queue Manager v1.2.0 (CMAT v5.0).

## Prerequisites

- Python 3.7 or higher
- Tkinter (usually included with Python)
- A CMAT v5.0 project (or you can install one via the UI)

## Step 1: Verify Python Installation

```bash
python3 --version
# Should be Python 3.7 or higher

# Verify Tkinter is available
python3 -m tkinter
# Should open a small test window
```

## Step 2: Launch the Application

```bash
cd ~/repos/ClaudeMultiAgentUI

# Method 1: Using the launcher script (recommended)
./run.py

# Method 2: Using Python module
python3 -m src.main

# Method 3: Direct execution
python3 run.py
```

The application window opens.

## Step 3: Connect to a CMAT Project

You can either install a new CMAT project or connect to an existing one.

### Option A: Install CMAT Template (Recommended for New Users)

If you don't have a CMAT project yet:

1. Click **File > Install...**
2. Select a directory where you want to install CMAT
   - Example: `~/repos/MyNewProject/`
   - A `.claude/` folder will be created here
3. Click **Install**
4. Watch the progress bar as CMAT is downloaded from GitHub
5. When complete, click **Connect Now** to immediately connect

The installer will:
- Download the latest CMAT template from GitHub
- Create a `.claude/` folder with all necessary files
- Validate the installation for security and completeness

### Option B: Connect to Existing Project

If you already have a CMAT v5.0 project:

1. Click **File > Connect...** (or press `Ctrl+O`)
2. Click **Browse...**
3. Navigate to your CMAT project root directory
   - Example: `~/repos/MyProject/` (the directory containing `.claude/`)
4. Select the project root folder
5. Verify the validation checkmarks:
   - ✓ CMAT script (`.claude/scripts/cmat.sh`)
   - ✓ Task queue (`.claude/queues/task_queue.json`)
   - ✓ Workflow templates (`.claude/queues/workflow_templates.json`)
   - ✓ Skills system (`.claude/skills/skills.json`)
   - ✓ Agents (`.claude/agents/agents.json`)
6. Should show: **✓ Valid CMAT Project**
7. Click **Connect**

The header bar now shows: `Connected: /path/to/your/project` and `CMAT v5.0`

## Step 4: Configure Claude API (Optional)

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

## Step 5: Try Core Features!

### Create an Enhancement 

1. Press `Ctrl+E` or click **Enhancements > Generate...**
2. Fill in:
   - **Title**: "Add Login Feature"
   - **Filename**: Auto-generated as `add-login-feature`
   - **Description**: "I want to add user authentication with email and password"
3. Click **Generate with Claude**
4. Wait for generation (watch the fun animation! "Bedazzling...", "Cogitating...")
5. Review the generated enhancement specification
6. Click **💾 Save**

Enhancement saved to: `enhancements/add-login-feature/add-login-feature.md`

### Start a Workflow 

The easiest way to process an enhancement:

1. Press `Ctrl+Shift+W` or click **Workflows > Start Workflow...**
2. Select workflow: **📋 New Feature Development**
3. Click **Browse Existing...** and select your enhancement file
   - Or click **Create New...** to generate one now
4. Pre-flight checks validate everything:
   - ✓ Workflow template is valid
   - ✓ All agents are available
   - ✓ Enhancement spec file exists
   - ✓ No conflicts
5. Click **Start Workflow**
6. First task automatically created and started!
7. Watch progress in main task view

The workflow will automatically chain through all 5 agents:
Requirements Analyst → Architect → Implementer → Tester → Documenter

### Create a Task (Manual Method)

If you prefer manual control:

1. Press `Ctrl+N` or right-click → **Create Task...**
2. **Quick Start**: Select **📋 Full Feature** from workflow dropdown
   - This pre-fills agent, priority, and automation settings
3. Fill in:
   - **Title**: "Analyze Login Feature"
   - **Source File**: Browse to your enhancement file
   - **Description**: Click **Generate with Claude** for AI-assisted description
4. Auto-filled settings:
   - Agent: Requirements Analyst
   - Priority: High
   - Auto Complete: ✓
   - Auto Chain: ✓
5. Click **Create & Start**

### View Workflow Progress

1. Press `Ctrl+W` or click **Workflows > View Active Workflows...**
2. See progress bar for your enhancement
3. See which agents are complete (✓), active (→), or pending (○)
4. Track workflow status in real-time
5. Works with custom workflows of any length!

### Browse Skills

1. Press `Ctrl+K` or click **Skills > Browse Skills...**
2. Filter by category
3. Click a skill to see:
   - Full skill content
   - Which agents use it
   - Description and category

### View Logs

1. Press `Ctrl+L` or click **Logs > View Operations Log**
2. See all queue operations
3. Search for specific entries
4. Useful for debugging

## Common First-Time Issues

### "Not a valid CMAT project"
- Make sure you're selecting the **project root**, not a subdirectory
- The project root contains `.claude/` folder
- CMAT v5.0 has `workflow_templates.json` not `WORKFLOW_STATES.json`
- If you have v4.x, most features will work but workflows may need updating

### "No such file or directory"
- Make sure you're in: `cd ~/repos/ClaudeMultiAgentUI`
- Verify file exists: `ls run.py`

### "Python module not found"
- Use `python3` instead of `python`
- Or run: `./run.py` directly (after `chmod +x run.py`)

### Window doesn't appear
- Check Tkinter: `python3 -m tkinter`
- On Linux: `sudo apt-get install python3-tk`
- On macOS: Tkinter included with Python
- On Windows: Reinstall Python with Tkinter option checked

### "Generate with Claude" button disabled
- Configure API key: **Settings > Claude Settings**
- API key required for AI features
- Free tier available at console.anthropic.com

### Generation takes too long
- Normal! Complex content takes 30-60 seconds
- Watch the working animation - it's still processing
- Opus 4 is slower but more comprehensive
- Sonnet 4.5 is faster for most tasks

### "Workflows not loading in task create"
- Verify `workflow_templates.json` exists
- Check file has valid JSON format
- Workflows > Manage Templates to verify templates exist
- Create a workflow template if none exist

## What's Next?

### Explore v5.0 Features
- Try the Workflow Starter (`Ctrl+Shift+W`)
- Create a custom workflow template
- Edit workflow input/output patterns
- Manage status transitions visually

### Explore Other Features
- Try the Enhancement Generator (`Ctrl+E`)
- Browse available skills (`Ctrl+K`)
- View workflow progress (`Ctrl+W`)
- Check integration status (`Ctrl+I`)

### Learn Workflows
- Create enhancement → Generate spec
- Start workflow → Watch auto-chain through agents
- View results in task details
- See workflow context in tasks

### Manage Agents
- **Agents > Manage Agents...**
- Create custom agents
- Assign skills to agents
- No workflow configuration needed (moved to templates)

### Customize Workflows
- **Workflows > Manage Templates...**
- Create custom workflow templates
- Configure input patterns with placeholders
- Set output filenames per step
- Manage status transitions
- Validate before saving

### Customize Settings
- **Settings > Claude Settings**
- Choose your preferred model
- Adjust token limits
- Configure timeout for generations
- Enable/disable auto-refresh

## Quick Reference Card

### Most Used Shortcuts
- `Ctrl+O` - Connect to project
- `Ctrl+E` - Generate enhancement
- `Ctrl+N` - Create task
- `Ctrl+Shift+W` - **Start workflow** (NEW!)
- `Ctrl+W` - View workflows
- `F5` - Refresh
- `Escape` - Close dialog

### Most Used Menus
- **File > Install...** - Install new CMAT project
- **File > Connect...** - Switch projects
- **Enhancements > Generate...** - Create enhancement files
- **Tasks > Create Task...** - Create new task
- **Workflows > Start Workflow...** - **Quick workflow launcher** (NEW!)
- **Workflows > Manage Templates...** - **Edit workflow templates** (NEW!)
- **Settings > Claude Settings** - Configure API

### Quick Workflow (v5.0)
1. Generate enhancement (`Ctrl+E`)
2. Start workflow (`Ctrl+Shift+W`)
3. Select workflow template
4. Browse to your enhancement file
5. Click **Start Workflow**
6. Watch it auto-chain through all agents! (`Ctrl+W`)

### Alternative: Manual Task Creation
1. Generate enhancement (`Ctrl+E`)
2. Create task from it (`Ctrl+N`)
3. Select workflow from dropdown (loads your custom workflows!)
4. Browse and select the enhancement file
5. Generate description with Claude
6. Check **Auto Complete** and **Auto Chain**
7. Click **Create & Start**
8. Watch it go! View progress with `Ctrl+W`

## Example: Complete Workflow

Here's a complete example from idea to implementation:

### Using Workflow Starter (v5.0 - Easiest!)

```
1. Press Ctrl+Shift+W
   Workflow: 📋 New Feature Development
   Enhancement: Click [Create New...]
     Title: "Add Dark Mode Theme"
     Description: "Toggle-able dark mode for the UI"
     [Generate with Claude] → [Save]
   Pre-flight checks: All ✓
   [Start Workflow]

2. Monitor Progress (Ctrl+W)
   See: Requirements ✓ → Architect ✓ → Implementer → ...

3. View Results
   Double-click any completed task
   See workflow context, outputs, skills used
```

### Using Manual Task Creation (More Control)

```
1. Generate Enhancement
   Ctrl+E
   Title: "Add Dark Mode Theme"
   Description: "I want to add a dark mode theme that users can toggle"
   [Generate with Claude]
   [Save]

2. Create Requirements Task
   Ctrl+N
   Quick Start: 📋 Full Feature (pre-fills everything!)
   Title: "Analyze Dark Mode Requirements"
   Source: enhancements/add-dark-mode-theme/add-dark-mode-theme.md
   [Generate with Claude] for description
   Auto Complete: ✓
   Auto Chain: ✓
   [Create & Start]

3. Monitor Progress
   Ctrl+W (View workflows)
   See: Requirements Analyst ✓ → Architect → ...

4. View Results
   Double-click completed task
   See analysis output, workflow context
   View next agent suggestion

5. Continue Workflow
   Auto-chain creates next task automatically!
   - Architect task created
   - Implementer task created
   - And so on...
```

---

## Need Help?

- Check [README.md](README.md) for detailed documentation
- See [USER_GUIDE.md](USER_GUIDE.md) for comprehensive feature documentation
- Look at context menus (right-click anywhere)
- Press `F5` to refresh if tasks aren't showing
- Press `Escape` to close any dialog
- Check operations log (`Ctrl+L`) for debugging

## Pro Tips

💡 **Use Workflow Starter** - Fastest way to start multi-agent workflows

💡 **Use keyboard shortcuts** - Much faster than menus

💡 **Enable auto-chain** - Tasks automatically progress through workflow

💡 **Dynamic workflow loading** - Create custom workflows and they appear everywhere!

💡 **Reference files** - Add related docs when generating enhancements

💡 **Model selection** - Use Opus 4 for complex enhancements, Sonnet 4.5 for tasks

💡 **Preview before save** - All generators show preview, edit if needed

💡 **Workflow validation** - Use "Validate Workflow" before saving templates

💡 **Transition editing** - Double-click transitions to edit after adding more steps

---

**That's it! You're ready to manage your multi-agent workflows visually with v5.0 features.** 🚀