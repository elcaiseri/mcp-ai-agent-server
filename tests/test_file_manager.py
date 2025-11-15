"""Tests for file manager tool."""
import pytest
import tempfile
from pathlib import Path
from src.tools.file_manager_tools import file_manager

@pytest.mark.asyncio
async def test_create_and_read_file():
    """Test file creation and reading."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_manager.base_dir = Path(tmpdir)
        
        # Create file
        result = await file_manager.create_file("test.txt", "Hello World")
        assert result["success"] is True
        
        # Read file
        result = await file_manager.read_file("test.txt")
        assert result["success"] is True
        assert result["content"] == "Hello World"

@pytest.mark.asyncio
async def test_delete_file():
    """Test file deletion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_manager.base_dir = Path(tmpdir)
        
        # Create and delete
        await file_manager.create_file("delete_me.txt", "temp")
        result = await file_manager.delete_file("delete_me.txt")
        
        assert result["success"] is True

@pytest.mark.asyncio
async def test_search_files():
    """Test file search."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_manager.base_dir = Path(tmpdir)
        
        # Create some files
        await file_manager.create_file("data1.txt", "test")
        await file_manager.create_file("data2.txt", "test")
        await file_manager.create_file("other.log", "test")
        
        # Search for txt files
        result = file_manager.search_files(".", "*.txt")
        
        assert result["success"] is True
        assert result["count"] == 2
