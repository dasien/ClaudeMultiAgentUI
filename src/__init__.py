"""
Multi-Agent Task Queue Manager

A graphical interface for managing multi-agent development workflows
using the Claude Multi-Agent Development Template.
"""

__version__ = "1.1.0"
__author__ = "Claude Multi-Agent Template Project"

from .main import main, TaskQueueUI
from .config import Config

__all__ = ['main', 'TaskQueueUI', 'Config']