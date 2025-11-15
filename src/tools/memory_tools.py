# Memory management functions for persistent storage
import json
import aiofiles
from typing import Dict, Any
from ..utils.config import config


class MemoryTool:
    """Tool for managing memory storage."""

    async def load_memory(self) -> Dict[str, Any]:
        """Load memory from file."""
        try:
            async with aiofiles.open(config.MEMORY_FILE, "r") as f:
                return json.loads(await f.read())
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    async def save_memory(self, memory: Dict[str, Any]) -> None:
        """Save memory to file."""
        async with aiofiles.open(config.MEMORY_FILE, "w") as f:
            await f.write(json.dumps(memory, indent=2))

    async def store_memory(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store one or more key–value pairs in persistent memory.
        This method updates the existing memory store with the provided
        key–value pairs. If a key already exists, its value will be overwritten.

        Args:
            input_data (Dict[str, Any]):
                A dictionary containing one or more key–value pairs to be stored.

        Returns:
            Dict[str, Any]:
                A result dictionary indicating success and listing the stored items.
        """

        memory = await self.load_memory()
        memory.update(input_data)
        await self.save_memory(memory)
        return {"status": "success", "stored": input_data}

    async def forget_memory(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove one or all items from persistent memory.

        If the input key is `"ALL"`, the entire memory store is cleared.
        Otherwise, only the specified key will be removed if it exists.

        Args:
            input_data (Dict[str, Any]):
                A dictionary containing a single key `"key"` that specifies
                which memory entry to remove, or `"ALL"` to clear all entries.

        Returns:
            Dict[str, Any]:
                A result dictionary indicating success, failure,
                or whether the requested key was not found.
        """

        memory = await self.load_memory()
        key = input_data.get("key")

        if key == "ALL":
            memory.clear()
            await self.save_memory(memory)
            return {"status": "success", "message": "All memory cleared."}

        if key in memory:
            del memory[key]
            await self.save_memory(memory)
            return {"status": "success", "message": f"Key '{key}' removed."}

        return {"status": "not_found", "message": f"Key '{key}' not found."}

    async def retrieve_memory(self) -> Dict[str, Any]:
        """
        Retrieve the entire memory store.

        Returns:
            Any:
                The complete memory store as a dictionary.
        """
        memory = await self.load_memory()
        return {"status": "success", "memory": memory}


memory = MemoryTool()
