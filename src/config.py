"""
Configuration settings for the Task Queue Manager.
"""


class Config:
    """Application configuration."""

    # Application info
    APP_NAME = "Claude Multi-Agent Manager"
    VERSION = "1.0.3"

    # Auto-refresh settings
    AUTO_REFRESH_INTERVAL = 3  # seconds
    AUTO_REFRESH_ENABLED_DEFAULT = True

    # Operations log settings
    MAX_LOG_LINES = 1000

    # UI settings
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 700
    MIN_WINDOW_WIDTH = 800
    MIN_WINDOW_HEIGHT = 500

    # Status colors
    STATUS_COLORS = {
        'pending': '#2196F3',    # Blue
        'active': '#FF9800',     # Orange
        'completed': '#4CAF50',  # Green
        'failed': '#F44336'      # Red
    }

    # Priority colors
    PRIORITY_COLORS = {
        'critical': '#F44336',   # Red
        'high': '#FF9800',       # Orange
        'normal': '#000000',     # Black
        'low': '#9E9E9E'         # Gray
    }

    # Row background colors (subtle)
    ROW_COLORS = {
        'pending': '#FFFFFF',    # White
        'active': '#FFF9E6',     # Light yellow
        'completed': '#E8F5E9',  # Light green
        'failed': '#FFEBEE'      # Light red
    }