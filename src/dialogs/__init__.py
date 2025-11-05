"""
Dialog windows for the Task Queue Manager v3.0.
Enhanced with Skills, Workflows, and Integration features.
"""

# Dialogs
from .connect_dialog import ConnectDialog
from .operations_log_dialog import OperationsLogDialog
from .about_dialog import AboutDialog
from .agent_manager_dialog import AgentManagerDialog
from .skills_viewer_dialog import SkillsViewerDialog
from .enhanced_task_details import EnhancedTaskDetailsDialog
from .create_task_enhanced import CreateTaskDialog
from .enhanced_agent_manager import EnhancedCreateEditAgentDialog
from .workflow_viewer import WorkflowStateViewer
from .integration_dashboard import IntegrationDashboard
from .enhancement_generator_dialog import EnhancementGeneratorDialog
from .claude_working_dialog import ClaudeWorkingDialog
from .claude_settings_dialog import ClaudeSettingsDialog

__all__ = [
    'ConnectDialog',
    'OperationsLogDialog',
    'AboutDialog',
    'AgentManagerDialog',
    'SkillsViewerDialog',
    'EnhancedTaskDetailsDialog',
    'CreateTaskDialog',
    'EnhancedCreateEditAgentDialog',
    'WorkflowStateViewer',
    'IntegrationDashboard',
    'EnhancementGeneratorDialog',
    'ClaudeWorkingDialog',
    'ClaudeSettingsDialog',
]