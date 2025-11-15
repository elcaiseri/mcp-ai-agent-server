"""Command line interface utilities for executing shell commands."""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from ..utils.config import config


class CLIUtilsTool:
    """Tool for command line operations."""

    def __init__(self):
        self.working_dir = config.DATA_DIR
        self.timeout = 60  # Default timeout in seconds

    def _resolve_path(self, path: Optional[str] = None) -> Path:
        """Resolve and validate working directory path."""
        if path is None:
            return self.working_dir

        dir_path = Path(path)
        if not dir_path.is_absolute():
            dir_path = self.working_dir / dir_path
        return dir_path

    async def execute_command(
        self, command: str, cwd: str = ".", timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Execute an arbitrary shell command with full control over execution context.
        This method allows running simple commands (e.g., `ls`, `cat`, `echo`, `pwd`, `mv`) as well as
        complex shell pipelines and redirections (e.g., `grep pattern file | sort > output.txt`).
        It captures both standard output and standard error, and returns structured results.

        Args:
            command (str): Command to execute (any valid shell command)
            cwd (str, optional): Relative Working directory (defaults to data directory)
            timeout (int, optional): Command timeout in seconds

        Returns:
            Result dictionary with stdout, stderr, and return code
        """
        try:
            working_dir = self._resolve_path(cwd)
            timeout_val = timeout or self.timeout

            # Create working directory if it doesn't exist
            working_dir.mkdir(parents=True, exist_ok=True)

            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(working_dir),
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout_val
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    "success": False,
                    "command": command,
                    "stdout": "",
                    "stderr": f"Command timed out after {timeout_val} seconds",
                    "return_code": -1,
                    "error": f"Timeout after {timeout_val}s",
                }

            stdout_str = stdout.decode("utf-8", errors="replace") if stdout else ""
            stderr_str = stderr.decode("utf-8", errors="replace") if stderr else ""

            return {
                "success": process.returncode == 0,
                "command": command,
                "stdout": stdout_str,
                "stderr": stderr_str,
                "return_code": process.returncode,
                "working_dir": str(working_dir),
                "error": None if process.returncode == 0 else stderr_str,
            }

        except Exception as e:
            return {
                "success": False,
                "command": command,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "error": f"Error executing command: {str(e)}",
            }


cli_utils = CLIUtilsTool()
