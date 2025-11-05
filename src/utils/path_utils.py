"""
Path utility functions.
"""

from pathlib import Path
from typing import Union


class PathUtils:
    """Utilities for working with file paths."""
    
    @staticmethod
    def relative_to_project(file_path: Union[str, Path], 
                           project_root: Union[str, Path]) -> str:
        """
        Get path relative to project root, or fallback to absolute/name.
        
        Args:
            file_path: File path to convert
            project_root: Project root directory
        
        Returns:
            Relative path if possible, otherwise absolute path
        
        Examples:
            >>> PathUtils.relative_to_project("/home/user/project/src/file.py", "/home/user/project")
            'src/file.py'
            
            >>> PathUtils.relative_to_project("/other/file.py", "/home/user/project")
            '/other/file.py'
        """
        file_path = Path(file_path)
        project_root = Path(project_root)
        
        try:
            return str(file_path.relative_to(project_root))
        except ValueError:
            return str(file_path)
    
    @staticmethod
    def relative_or_name(file_path: Union[str, Path], 
                        project_root: Union[str, Path]) -> str:
        """
        Get path relative to project root, or just the filename.
        
        Args:
            file_path: File path to convert
            project_root: Project root directory
        
        Returns:
            Relative path if possible, otherwise just the filename
        
        Examples:
            >>> PathUtils.relative_or_name("/home/user/project/src/file.py", "/home/user/project")
            'src/file.py'
            
            >>> PathUtils.relative_or_name("/other/location/file.py", "/home/user/project")
            'file.py'
        """
        file_path = Path(file_path)
        project_root = Path(project_root)
        
        try:
            return str(file_path.relative_to(project_root))
        except ValueError:
            return file_path.name
