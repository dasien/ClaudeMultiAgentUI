# Quick Start Guide

This document describes the process to get up and running with the Multi-Agent Task Queue Manager.

## Step 1: Verify Python Installation

```bash
python3 --version
# Should be Python 3.7 or higher
```

## Step 2: Launch the Application

```bash
cd ~/repos/ClaudeMultiAgentUI

# Method 1: Using the launcher script
./run.py

# Method 2: Using Python module
python3 -m src.claude_queue_ui.main

# Method 3: Direct execution
python3 run.py
```

## Step 3: Connect to Your Project

1. The application window opens
2. Click **File > Connect...**
3. Click **Browse...**
4. Navigate to your Claude multi-agent project
5. Select `.claude/queues/queue_manager.sh`
6. Verify the validation checkmarks are green
7. Click **Connect**

## Step 4: Try It Out!

### View Existing Tasks
- Tasks appear in the main table
- See pending, active, completed, and failed tasks

### Create a New Task
- Right-click in empty space
- Select **Create Task...**
- Fill in the form:
  - Title: "Test Task"
  - Agent: Select from dropdown
  - Priority: "High"
  - Task Type: "Analysis"
  - Source File: Browse to an enhancement .md file
  - Prompt: Click **Generate** for AI-assisted description.  If you have set a Claude API key in settings then Claude 
  will generate the prompt, if no Claude API key is present, the system will attempt to generate one from a template based
  on your choices.  You can also type the prompt yourself.
  - Optional: Check **Auto Complete** or **Auto Chain** for automated workflows
- Choose an action:
  - **Create Task**: Add to queue as pending
  - **Create & Start**: Add and immediately execute
  - **Cancel**: Discard

### View Task Details
- Double-click any task
- See complete information
- View logs (if available)

### Start a Task (Optional)
- Right-click a pending task
- Select **Start Task**
- Wait for agent to complete
- Task status updates automatically

## Common First-Time Issues

### "No such file or directory"
- Make sure you're in the correct directory: `cd ~/repos/ClaudeMultiAgentUI`

### "Queue manager not found"
- Ensure you're selecting `queue_manager.sh` from your project's `.claude/queues/` directory
- Not all projects have this file - you need a project using the multi-agent template

### "Python module not found"
- Use `python3` instead of `python`
- Or run: `./run.py` directly

### Window doesn't appear
- Check if Tkinter is installed: `python3 -m tkinter`
- On Linux, install: `sudo apt-get install python3-tk`

## What's Next?

- Read the full [README.md](README.md) for all features
- Explore keyboard shortcuts (Ctrl+O, Ctrl+N, F5, etc.)
- Try the operations log (Ctrl+L)
- Connect to multiple projects

## Need Help?

- Check [README.md](README.md) for detailed documentation
- Look at the context menus (right-click anywhere)
- Press F5 to refresh if tasks aren't showing

## Test with Example Project

If you have the ClaudeMultiAgentTemplate, here's a complete walkthrough:

### Step 1: Launch the UI

```bash
cd ~/repos/ClaudeMultiAgentUI
./run.py
```

### Step 2: Connect to the Template Project

1. In the UI, click **File > Connect...**
2. Click **Browse...**
3. Navigate to: `~/repos/ClaudeMultiAgentTemplate/.claude/queues/`
4. Select `queue_manager.sh`
5. Verify the validation checkmarks are green
6. Click **Connect**

### Step 3: Create a Demo Task

1. Right-click in the empty space
2. Select **Create Task...**
3. Fill in the form:
   - **Title**: "Demo Test Task"
   - **Agent**: Select "Requirements Analyst" from dropdown
   - **Priority**: "High"
   - **Task Type**: "Analysis"
   - **Source File**: Click **Browse...** and navigate to:
     - `~/repos/ClaudeMultiAgentTemplate/enhancements/demo-test/`
     - Select `demo-test.md`
   - **Prompt**: Click **Generate** to create an AI-assisted prompt
     - Or manually enter: "Analyze the demo test requirements and provide a detailed assessment"
   - **Optional**: Check **Auto Complete** if you want the task to automatically mark as complete
4. Click **Create Task** to add to queue, or **Create & Start** to execute immediately

### Step 4: View and Monitor

- The task appears in the main table with "Pending" status
- If you started it, status changes to "Active"
- Double-click to view details
- Task will complete automatically and show as "Completed" when done

### Expected Result

You should see the Requirements Analyst process the demo-test.md file and provide analysis output. Check the operations log (Ctrl+L) to see detailed execution information.

---

**That's it! You're ready to manage your multi-agent workflows visually.**