"""
Dialog windows for the Task Queue Manager v3.0.
Enhanced with Skills, Workflows, and Integration features.
"""

# Existing dialogs
from .connect_dialog import ConnectDialog
from .operations_log_dialog import OperationsLogDialog
from .about_dialog import AboutDialog
from .agent_manager_dialog import AgentManagerDialog

# Enhanced v3.0 dialogs
from .skills_viewer_dialog import SkillsViewerDialog
from .enhanced_task_details import EnhancedTaskDetailsDialog
from .create_task_enhanced import CreateTaskDialog
from .enhanced_agent_manager import EnhancedCreateEditAgentDialog
from .workflow_viewer import WorkflowStateViewer
from .integration_dashboard import IntegrationDashboard

__all__ = [
    # Original dialogs
    'ConnectDialog',
    'OperationsLogDialog',
    'AboutDialog',
    'AgentManagerDialog',

    # Enhanced v3.0 dialogs
    'SkillsViewerDialog',
    'EnhancedTaskDetailsDialog',
    'CreateTaskDialog',
    'EnhancedCreateEditAgentDialog',
    'WorkflowStateViewer',
    'IntegrationDashboard',
]