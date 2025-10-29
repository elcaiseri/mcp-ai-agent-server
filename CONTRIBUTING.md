# Contributing to MCP AI Agent Server

Thank you for considering contributing to the MCP AI Agent Server! 

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)

### Suggesting Features

1. Check existing issues and discussions
2. Create a new issue describing:
   - The problem you're trying to solve
   - Your proposed solution
   - Any alternatives you've considered

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write or update tests
5. Ensure tests pass (`uv run pytest`)
6. Format code (`uv run black src/`)
7. Commit changes (`git commit -m 'Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/mcp-ai-agent-server.git
cd mcp-ai-agent-server

# Run setup
./setup.sh

# Run tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test
uv run pytest tests/test_calculator.py
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for functions/classes
- Keep functions focused and small
- Use meaningful variable names

## Testing

- Write tests for new features
- Ensure existing tests pass
- Aim for >80% code coverage
- Use pytest fixtures for reusable test data
- Mock external API calls

## Adding a New Tool

1. Create tool file in `src/tools/`
2. Implement tool class with async methods
3. Add error handling
4. Create tests in `tests/`
5. Update `src/server.py` to register tool
6. Update documentation

Example:
```python
# src/tools/my_tool.py
from typing import Dict, Any

class MyTool:
    """Description of what this tool does."""
    
    async def do_something(self, param: str) -> Dict[str, Any]:
        """
        Do something useful.
        
        Args:
            param: Description of parameter
            
        Returns:
            Result dictionary
        """
        try:
            # Implementation
            result = f"Processed: {param}"
            
            return {
                "success": True,
                "result": result,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": str(e)
            }

my_tool = MyTool()
```

## Documentation

- Update README.md for major changes
- Update API.md for new tools
- Add examples in examples/
- Update CHANGELOG.md

## Commit Messages

Use clear, descriptive commit messages:
- `feat: Add support for X`
- `fix: Resolve issue with Y`
- `docs: Update API documentation`
- `test: Add tests for Z`
- `refactor: Improve code structure`

## Questions?

Feel free to open an issue for any questions or discussions!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
