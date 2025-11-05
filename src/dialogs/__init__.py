"""
Dialog windows for the Task Queue Manager v3.0.
Enhanced with Skills, Workflows, and Integration features.
"""

# Dialogs
from .connect import ConnectDialog
from .log_viewer import LogViewerDialog
from .about import AboutDialog
from .agent_list import AgentListDialog
from .skills_list import SkillsViewerDialog
from .task_details import TaskDetailsDialog
from .task_create import CreateTaskDialog
from .agent_details import AgentDetailsDialog
from .workflow_viewer import WorkflowStateViewer
from .integration_dashboard import IntegrationDashboardDialog
from .enhancement_create import CreateEnhancementDialog
from .working import WorkingDialog
from .claude_settings import ClaudeSettingsDialog

__all__ = [
    'ConnectDialog',
    'LogViewerDialog',
    'AboutDialog',
    'AgentListDialog',
    'SkillsViewerDialog',
    'TaskDetailsDialog',
    'CreateTaskDialog',
    'AgentDetailsDialog',
    'WorkflowStateViewer',
    'IntegrationDashboardDialog',
    'CreateEnhancementDialog',
    'WorkingDialog',
    'ClaudeSettingsDialog',
]