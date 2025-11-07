"""Setup script for Multi-Agent Task Queue Manager."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="claude-queue-ui",
    version="1.0.4",
    author="Claude Multi-Agent Template Project",
    description="A graphical interface for managing multi-agent development workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ClaudeMultiAgentUI",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses Python standard library only!
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "claude-queue-ui=claude_queue_ui.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: User Interfaces",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords="claude ai agent multi-agent workflow queue task-manager ui",
)