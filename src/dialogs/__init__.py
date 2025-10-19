"""
Dialog windows for the Task Queue Manager.
"""

from .connect_dialog import ConnectDialog
from .create_task_dialog import CreateTaskDialog
from .task_details_dialog import TaskDetailsDialog
from .operations_log_dialog import OperationsLogDialog
from .about_dialog import AboutDialog
from .agent_manager_dialog import AgentManagerDialog
from .create_edit_agent_dialog import CreateEditAgentDialog

__all__ = [
    'ConnectDialog',
    'CreateTaskDialog',
    'TaskDetailsDialog',
    'OperationsLogDialog',
    'AboutDialog',
    'AgentManagerDialog',
    'CreateEditAgentDialog'
]