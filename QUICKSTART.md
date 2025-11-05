# Quick Start Guide

This document describes the process to get up and running with the Multi-Agent Task Queue Manager v1.0.3.

## Prerequisites

- Python 3.7 or higher
- Tkinter (usually included with Python)
- A CMAT v3.0 project

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

## Step 3: Connect to Your CMAT v3.0 Project

1. Click **File > Connect...** (or press `Ctrl+O`)
2. Click **Browse...**
3. Navigate to your CMAT project root directory
   - Example: `~/repos/MyProject/` (the directory containing `.claude/`)
4. Select the project root folder
5. Verify the validation checkmarks:
   - ✓ CMAT script (`.claude/scripts/cmat.sh`)
   - ✓ Task queue (`.claude/queues/task_queue.json`)
   - ✓ Agent contracts (`.claude/AGENT_CONTRACTS.json`)
   - ✓ Skills system (`.claude/skills/skills.json`)
   - ✓ Agents (`.claude/agents/agents.json`)
6. Should show: **✓ Valid CMAT v3.0 Project**
7. Click **Connect**

The header bar now shows: `Connected: /path/to/your/project` and `CMAT v3.0.0`

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
- **Agent role generation** when creating agents

## Step 5: Try Core Features!

### Create an Enhancement (NEW in v1.0.3!)

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

### Create a Task

1. Press `Ctrl+N` or right-click → **Create Task...**
2. Fill in:
   - **Title**: "Analyze Login Feature"
   - **Agent**: "Requirements Analyst"
   - **Priority**: "High"
   - **Task Type**: "Analysis"
   - **Source File**: Browse to your enhancement file (from previous step)
   - **Description**: Click **Generate with Claude** for AI-assisted description
     - Or type manually: "Analyze the login feature requirements"
   - **Optional**: Check **Auto Complete** and **Auto Chain**
3. Choose:
   - **Create Task** - Adds to queue
   - **Create & Start** - Adds and immediately executes

### View Task Progress

- Task appears in main table
- Status shows: Pending → Active → Completed
- Double-click to view full details
- See skills applied, outputs created, contract validation

### View Active Workflows

1. Press `Ctrl+W` or click **Workflows > View Active Workflows...**
2. See progress bar for each enhancement
3. See which agents are complete (✓), active (→), or pending (○)
4. Track workflow status

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

### "Not a valid CMAT v3.0 project"
- Make sure you're selecting the **project root**, not a subdirectory
- The project root contains `.claude/` folder
- CMAT v3.0 has `cmat.sh` not `queue_manager.sh`
- If you have v2.0 or earlier, upgrade your template

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

## What's Next?

### Explore Features
- Try the Enhancement Generator (`Ctrl+E`)
- Browse available skills (`Ctrl+K`)
- View workflow progress (`Ctrl+W`)
- Check integration status (`Ctrl+I`)

### Learn Workflows
- Create enhancement → Generate spec
- Create task from enhancement
- Start task → Watch it execute
- View results in task details

### Manage Agents
- **Agents > Manage Agents...**
- Create custom agents
- Assign skills to agents
- Configure workflow roles

### Customize Settings
- **Settings > Claude Settings**
- Choose your preferred model
- Adjust token limits
- Enable/disable auto-refresh

## Quick Reference Card

### Most Used Shortcuts
- `Ctrl+O` - Connect to project
- `Ctrl+E` - Generate enhancement
- `Ctrl+N` - Create task
- `Ctrl+W` - View workflows
- `F5` - Refresh
- `Escape` - Close dialog

### Most Used Menus
- **File > Connect...** - Switch projects
- **Enhancements > Generate...** - Create enhancement files
- **Tasks > Create Task...** - Create new task
- **Settings > Claude Settings** - Configure API

### Quick Workflow
1. Generate enhancement (`Ctrl+E`)
2. Create task from it (`Ctrl+N`)
3. Browse and select the enhancement file
4. Generate description with Claude
5. Check **Auto Complete** and **Auto Chain**
6. Click **Create & Start**
7. Watch it go! View progress with `Ctrl+W`

## Example: Complete Workflow

Here's a complete example from idea to implementation:

### 1. Generate Enhancement
```
Ctrl+E
Title: "Add Dark Mode Theme"
Description: "I want to add a dark mode theme that users can toggle"
[Generate with Claude]
[Save]
```

### 2. Create Requirements Task
```
Ctrl+N
Title: "Analyze Dark Mode Requirements"
Agent: Requirements Analyst
Source: enhancements/add-dark-mode-theme/add-dark-mode-theme.md
[Generate with Claude] for description
Auto Complete: ✓
Auto Chain: ✓
[Create & Start]
```

### 3. Monitor Progress
```
Ctrl+W (View workflows)
See: Requirements Analyst ✓ → Architect → ...
```

### 4. View Results
```
Double-click completed task
See analysis output
Check contract validation
View next agent suggestion
```

### 5. Continue Workflow
The auto-chain creates the next task automatically!
- Architect task created
- Implementer task created
- And so on...

---

## Need Help?

- Check [README.md](README.md) for detailed documentation
- Look at context menus (right-click anywhere)
- Press `F5` to refresh if tasks aren't showing
- Press `Escape` to close any dialog
- Check operations log (`Ctrl+L`) for debugging

## Pro Tips

💡 **Use keyboard shortcuts** - Much faster than menus

💡 **Enable auto-chain** - Tasks automatically progress through workflow

💡 **Use Quick Start Workflows** - Pre-configured task templates

💡 **Reference files** - Add related docs when generating enhancements

💡 **Model selection** - Use Opus 4 for complex enhancements, Sonnet 4.5 for tasks

💡 **Preview before save** - All generators show preview, edit if needed

---

**That's it! You're ready to manage your multi-agent workflows visually.** 🚀