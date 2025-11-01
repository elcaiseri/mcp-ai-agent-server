import inspect
import re
from typing import get_type_hints, Any

def func_to_tool(func, func_name: str = None, return_type: Any = False) -> dict:
    """Convert any Python function into an MCP Tool() definition with arg docs."""
    hints = get_type_hints(func)
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or "No description provided"

    # Extract per-arg descriptions from docstring
    arg_docs = parse_arg_docs(doc)

    properties = {}
    required = []

    for name, param in sig.parameters.items():
        if name == "self":
            continue

        param_type = hints.get(name, Any)
        json_type = python_type_to_json(param_type)

        properties[name] = {
            "type": json_type,
            "description": arg_docs.get(name, f"Parameter '{name}' ({param_type})")
        }

        if param.default == inspect.Parameter.empty:
            required.append(name)
        else:
            properties[name]["default"] = param.default

    tool_schema = {
        "name": func_name or func.__name__,
        "description": doc.split("\n")[0],
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required
        }
    }

    # Optional output schema
    #return_type = hints.get("return")
    if return_type:
        tool_schema["outputSchema"] = {
            "type": python_type_to_json(return_type),
            "description": f"Return type: {return_type}"
        }

    return tool_schema


def python_type_to_json(py_type):
    """Map Python types to JSON Schema types."""
    mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object"
    }
    return mapping.get(py_type, "string")


def parse_arg_docs(doc):
    """
    Extract argument descriptions from a docstring.
    Supports Google-style and NumPy-style docstrings.
    """
    arg_docs = {}

    # Google-style: Args:
    google_pattern = re.compile(r"Args?:\s*((?:\n\s{4,}[\w_]+.*)+)", re.MULTILINE)
    match = google_pattern.search(doc)
    if match:
        args_block = match.group(1)
        for line in re.findall(r"\n\s{4,}([\w_]+)\s*\(?.*?\)?:\s*(.*)", args_block):
            name, desc = line
            arg_docs[name.strip()] = desc.strip()
        return arg_docs

    # NumPy-style: Parameters
    numpy_pattern = re.compile(r"Parameters\s*-+\s*((?:\n\s{4,}[\w_]+.*)+)", re.MULTILINE)
    match = numpy_pattern.search(doc)
    if match:
        args_block = match.group(1)
        for line in re.findall(r"\n\s{4,}([\w_]+)\s*:.*\n\s{8,}(.*)", args_block):
            name, desc = line
            arg_docs[name.strip()] = desc.strip()
        return arg_docs

    return arg_docs