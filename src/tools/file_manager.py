"""File management tool for CRUD operations."""
import aiofiles
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import glob
from ..utils.config import config

class FileManagerTool:
    """Tool for file operations."""
    
    def __init__(self):
        self.base_dir = config.DATA_DIR
        self.base_dir.mkdir(exist_ok=True)
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve and validate file path."""
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = self.base_dir / file_path
        return file_path
    
    async def create_file(self, path: str, content: str) -> Dict[str, Any]:
        """
        Create a new file with content.
        
        Args:
            path: File path (relative to data directory or absolute)
            content: File content
            
        Returns:
            Result dictionary
        """
        try:
            file_path = self._resolve_path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(content)
            
            return {
                "success": True,
                "path": str(file_path),
                "message": f"File created: {file_path.name}",
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "path": path,
                "message": None,
                "error": f"Error creating file: {str(e)}"
            }
    
    async def read_file(self, path: str) -> Dict[str, Any]:
        """
        Read file content.
        
        Args:
            path: File path
            
        Returns:
            File content and metadata
        """
        try:
            file_path = self._resolve_path(path)
            
            if not file_path.exists():
                return {
                    "success": False,
                    "path": str(file_path),
                    "content": None,
                    "error": "File not found"
                }
            
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
            
            return {
                "success": True,
                "path": str(file_path),
                "content": content,
                "size": file_path.stat().st_size,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "path": path,
                "content": None,
                "error": f"Error reading file: {str(e)}"
            }
    
    async def update_file(self, path: str, content: str) -> Dict[str, Any]:
        """Update existing file content."""
        return await self.create_file(path, content)
    
    async def delete_file(self, path: str) -> Dict[str, Any]:
        """
        Delete a file.
        
        Args:
            path: File path
            
        Returns:
            Result dictionary
        """
        try:
            file_path = self._resolve_path(path)
            
            if not file_path.exists():
                return {
                    "success": False,
                    "path": str(file_path),
                    "error": "File not found"
                }
            
            file_path.unlink()
            
            return {
                "success": True,
                "path": str(file_path),
                "message": f"File deleted: {file_path.name}",
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "path": path,
                "error": f"Error deleting file: {str(e)}"
            }
    
    async def search_files(
        self, 
        directory: str = ".", 
        pattern: str = "*"
    ) -> Dict[str, Any]:
        """
        Search for files matching a pattern.
        
        Args:
            directory: Directory to search (relative or absolute)
            pattern: Glob pattern (e.g., "*.txt", "data_*")
            
        Returns:
            List of matching files
        """
        try:
            search_dir = self._resolve_path(directory)
            
            if not search_dir.exists():
                return {
                    "success": False,
                    "directory": str(search_dir),
                    "files": [],
                    "error": "Directory not found"
                }
            
            files = []
            for file_path in search_dir.glob(f"**/{pattern}"):
                if file_path.is_file():
                    files.append({
                        "path": str(file_path),
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime
                    })
            
            return {
                "success": True,
                "directory": str(search_dir),
                "pattern": pattern,
                "files": files,
                "count": len(files),
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "directory": directory,
                "files": [],
                "error": f"Error searching files: {str(e)}"
            }
    
    async def list_directory(self, directory: str = ".") -> Dict[str, Any]:
        """
        List contents of a directory.
        
        Args:
            directory: Directory path
            
        Returns:
            Directory contents
        """
        try:
            dir_path = self._resolve_path(directory)
            
            if not dir_path.exists():
                return {
                    "success": False,
                    "directory": str(dir_path),
                    "contents": [],
                    "error": "Directory not found"
                }
            
            contents = []
            for item in dir_path.iterdir():
                contents.append({
                    "name": item.name,
                    "path": str(item),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
            
            return {
                "success": True,
                "directory": str(dir_path),
                "contents": contents,
                "count": len(contents),
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "directory": directory,
                "contents": [],
                "error": f"Error listing directory: {str(e)}"
            }

file_manager = FileManagerTool()
