"""
Multi-Agent Task Queue Manager

A graphical interface for managing multi-agent development workflows
using the Claude Multi-Agent Development Template.
"""

__version__ = "1.4.0"
__author__ = "Brian Gentry"

from .main import main, MainView
from .config import Config

__all__ = ['main', 'MainView', 'Config']