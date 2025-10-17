"""
Data models for the Task Queue Manager.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum
from pathlib import Path


class ConnectionState(Enum):
    """Connection state enum."""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class Task:
    """Task data model."""
    id: str
    title: str
    assigned_agent: str
    priority: str
    task_type: str
    description: str
    source_file: str
    created: str
    status: str
    started: Optional[str] = None
    completed: Optional[str] = None
    result: Optional[str] = None


@dataclass
class AgentStatus:
    """Agent status data model."""
    name: str
    status: str  # idle, active, blocked, error
    current_task: Optional[str] = None
    last_activity: Optional[str] = None


@dataclass
class QueueState:
    """Queue state data model."""
    pending_tasks: List[Task]
    active_workflows: List[Task]
    completed_tasks: List[Task]
    failed_tasks: List[Task]
    agent_status: Dict[str, AgentStatus]


@dataclass
class QueueUIState:
    """UI state data model."""
    connection_state: ConnectionState = ConnectionState.DISCONNECTED
    queue_manager_path: Optional[Path] = None
    project_root: Optional[Path] = None
    queue_file: Optional[Path] = None
    logs_dir: Optional[Path] = None
    selected_task: Optional[Task] = None
    auto_refresh_enabled: bool = True
    auto_refresh_interval: int = 3  # seconds
    last_refresh: float = 0.0
    error_message: str = ""