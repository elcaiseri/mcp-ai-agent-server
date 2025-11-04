# Memory management functions for persistent storage
import json
import aiofiles
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..utils.config import config

class MemoryTool:
    """Tool for managing memory storage with agentic capabilities."""
    
    async def load_memory(self) -> Dict[str, Any]:
        """Load memory from file."""
        try:
            async with aiofiles.open(config.MEMORY_FILE, "r") as f:
                return json.loads(await f.read())
        except (FileNotFoundError, json.JSONDecodeError):
            return {"short_term": {}, "long_term": {}, "context": {}, "metadata": {}}

    async def save_memory(self, memory: Dict[str, Any]) -> None:
        """Save memory to file."""
        async with aiofiles.open(config.MEMORY_FILE, "w") as f:
            await f.write(json.dumps(memory, indent=2))

    async def store_memory(
        self, 
        key: str, 
        value: Any, 
        memory_type: str = "short_term",
        tags: Optional[List[str]] = None,
        ttl: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Store a key-value pair in persistent memory with metadata.

        Args:
            key: The memory key
            value: The value to store
            memory_type: Type of memory ("short_term", "long_term", "context")
            tags: Optional list of tags for categorization
            ttl: Optional time-to-live in seconds

        Returns:
            Dict with status and stored information
        """
        memory = await self.load_memory()
        
        if memory_type not in memory:
            memory[memory_type] = {}
        
        memory[memory_type][key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "tags": tags or [],
            "ttl": ttl,
            "access_count": 0
        }
        
        await self.save_memory(memory)
        return {"status": "success", "key": key, "memory_type": memory_type}

    async def retrieve_memory(
        self, 
        key: Optional[str] = None,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve memory by key, type, or tags.

        Args:
            key: Specific key to retrieve
            memory_type: Filter by memory type
            tags: Filter by tags

        Returns:
            Dict with status and retrieved memory
        """
        memory = await self.load_memory()
        
        # Retrieve specific key
        if key:
            for mtype, mdata in memory.items():
                if isinstance(mdata, dict) and key in mdata:
                    entry = mdata[key]
                    entry["access_count"] += 1
                    await self.save_memory(memory)
                    return {"status": "success", "key": key, "data": entry["value"], "metadata": entry}
            return {"status": "not_found", "message": f"Key '{key}' not found"}
        
        # Filter by memory type and/or tags
        result = {}
        types_to_search = [memory_type] if memory_type else ["short_term", "long_term", "context"]
        
        for mtype in types_to_search:
            if mtype in memory and isinstance(memory[mtype], dict):
                for k, v in memory[mtype].items():
                    if tags:
                        if any(tag in v.get("tags", []) for tag in tags):
                            result[k] = v
                    else:
                        result[k] = v
        
        return {"status": "success", "memory": result}

    async def forget_memory(
        self, 
        key: Optional[str] = None,
        memory_type: Optional[str] = None,
        clear_all: bool = False
    ) -> Dict[str, Any]:
        """
        Remove memory entries.

        Args:
            key: Specific key to remove
            memory_type: Clear entire memory type
            clear_all: Clear all memory

        Returns:
            Dict with status and message
        """
        memory = await self.load_memory()
        
        if clear_all:
            memory = {"short_term": {}, "long_term": {}, "context": {}, "metadata": {}}
            await self.save_memory(memory)
            return {"status": "success", "message": "All memory cleared"}
        
        if memory_type:
            if memory_type in memory:
                memory[memory_type] = {}
                await self.save_memory(memory)
                return {"status": "success", "message": f"Memory type '{memory_type}' cleared"}
        
        if key:
            found = False
            for mtype, mdata in memory.items():
                if isinstance(mdata, dict) and key in mdata:
                    del mdata[key]
                    found = True
                    break
            
            if found:
                await self.save_memory(memory)
                return {"status": "success", "message": f"Key '{key}' removed"}
            return {"status": "not_found", "message": f"Key '{key}' not found"}
        
        return {"status": "error", "message": "No deletion criteria specified"}

    async def consolidate_memory(self) -> Dict[str, Any]:
        """
        Consolidate short-term to long-term memory based on access patterns.

        Returns:
            Dict with consolidation results
        """
        memory = await self.load_memory()
        consolidated = []
        
        if "short_term" in memory:
            for key, value in list(memory["short_term"].items()):
                if value.get("access_count", 0) > 3:  # Threshold for consolidation
                    if "long_term" not in memory:
                        memory["long_term"] = {}
                    memory["long_term"][key] = value
                    del memory["short_term"][key]
                    consolidated.append(key)
        
        await self.save_memory(memory)
        return {"status": "success", "consolidated_keys": consolidated}

memory = MemoryTool()
