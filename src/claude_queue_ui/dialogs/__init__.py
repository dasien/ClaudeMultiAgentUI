"""
Dialog windows for the Task Queue Manager.
"""

from .connect_dialog import ConnectDialog
from .create_task_dialog import CreateTaskDialog
from .task_details_dialog import TaskDetailsDialog
from .operations_log_dialog import OperationsLogDialog
from .about_dialog import AboutDialog

__all__ = [
    'ConnectDialog',
    'CreateTaskDialog',
    'TaskDetailsDialog',
    'OperationsLogDialog',
    'AboutDialog'
]