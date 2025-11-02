import inspect
import re
from collections.abc import Iterable as IterableABC, Mapping as MappingABC, Sequence as SequenceABC
from enum import Enum
from typing import (
    Any,
    Dict,
    Iterable,
    Literal,
    Mapping,
    Sequence,
    Tuple,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

def func_to_tool(func, func_name: str = None, return_type: Any = False) -> dict:
    """Convert any Python function into an MCP Tool() definition with comprehensive docstring parsing."""
    hints = get_type_hints(func)
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or "No description provided"

    # Parse full docstring
    parsed_doc = parse_full_docstring(doc)

    properties = {}
    required = []

    for name, param in sig.parameters.items():
        if name == "self":
            continue

        param_type = hints.get(name, Any)
        param_info = parsed_doc["parameters"].get(name, {})
        schema = python_type_to_json(param_type)

        if not schema and param_info.get("type"):
            schema = python_doc_type_to_json(param_info["type"])

        if not schema:
            schema = {"type": "string"}

        description = param_info.get("description", f"Parameter '{name}'")
        properties[name] = {**schema, "description": description}

        if "enum" in param_info:
            properties[name]["enum"] = param_info["enum"]

        if param.default == inspect.Parameter.empty:
            required.append(name)
        else:
            properties[name]["default"] = param.default

    tool_schema = {
        "name": func_name or func.__name__,
        "description": parsed_doc["description"],
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required
        }
    }

    # Add examples if present
    if parsed_doc.get("examples"):
        tool_schema["examples"] = parsed_doc["examples"]

    # Add notes if present
    if parsed_doc.get("notes"):
        tool_schema["notes"] = parsed_doc["notes"]

    # Optional output schema
    annotated_return = return_type and hints.get("return")
    if annotated_return:
        output_schema = python_type_to_json(annotated_return) or {"type": "string"}
        output_schema.setdefault(
            "description",
            parsed_doc.get("returns", f"Return type: {annotated_return}"),
        )
        tool_schema["outputSchema"] = output_schema

    return tool_schema


def python_type_to_json(py_type):
    """Map Python type hints to JSON Schema fragments."""
    if py_type is Any:
        return {}
    if py_type is type(None):
        return {"type": "null"}

    origin = get_origin(py_type)
    if origin is Union:
        return _union_type_to_schema(get_args(py_type))
    if _is_sequence_origin(origin):
        return _sequence_type_to_schema(get_args(py_type))
    if origin in (tuple, Tuple):
        return _tuple_type_to_schema(get_args(py_type))
    if _is_mapping_origin(origin):
        return _mapping_type_to_schema(get_args(py_type))
    if origin is Literal:
        return _literal_type_to_schema(get_args(py_type))

    mapping = {
        str: {"type": "string"},
        int: {"type": "integer"},
        float: {"type": "number"},
        bool: {"type": "boolean"},
        bytes: {"type": "string", "contentEncoding": "base64"},
        dict: {"type": "object"},
        list: {"type": "array"},
        tuple: {"type": "array"},
        set: {"type": "array", "uniqueItems": True},
    }

    if isinstance(py_type, type) and issubclass(py_type, Enum):
        values = [member.value for member in py_type]
        return _values_to_enum_schema(values)

    return mapping.get(py_type, mapping.get(origin, {})).copy()


def _is_sequence_origin(origin):
    if origin in (list, Sequence, SequenceABC, Iterable, IterableABC):
        return True
    try:
        return issubclass(origin, (SequenceABC, IterableABC))
    except TypeError:
        return False


def _is_mapping_origin(origin):
    if origin in (dict, Mapping, MappingABC):
        return True
    try:
        return issubclass(origin, MappingABC)
    except TypeError:
        return False


def _union_type_to_schema(args):
    has_none = any(arg is type(None) for arg in args)
    non_none_args = [arg for arg in args if arg is not type(None)]

    if not non_none_args:
        return {"type": "null"}

    schemas = [
        python_type_to_json(arg) or {"type": "string"} for arg in non_none_args
    ]

    if len(schemas) == 1:
        base_schema = schemas[0]
    else:
        base_schema = _combine_union_schemas(schemas)

    if has_none:
        base_schema = _add_null_to_schema(base_schema)

    return base_schema


def _sequence_type_to_schema(args):
    item_type = args[0] if args else Any
    items_schema = python_type_to_json(item_type) or {"type": "string"}
    return {"type": "array", "items": items_schema}


def _tuple_type_to_schema(args):
    if not args:
        return {"type": "array"}
    if len(args) == 2 and args[1] is Ellipsis:
        # Homogeneous tuple Tuple[T, ...]
        return {
            "type": "array",
            "items": python_type_to_json(args[0]) or {"type": "string"},
        }
    item_schemas = [python_type_to_json(arg) or {"type": "string"} for arg in args]
    return {"type": "array", "prefixItems": item_schemas, "items": False}


def _mapping_type_to_schema(args):
    value_type = args[1] if len(args) > 1 else Any
    additional_schema = python_type_to_json(value_type) or {"type": "string"}
    return {"type": "object", "additionalProperties": additional_schema}


def _literal_type_to_schema(values):
    schema = _values_to_enum_schema(values)
    if "type" not in schema:
        inferred_types = {_python_value_to_json_type(value) for value in values}
        if len(inferred_types) == 1:
            schema["type"] = inferred_types.pop()
    return schema


def _values_to_enum_schema(values):
    return {"enum": list(values)}


def _python_value_to_json_type(value):
    if value is None:
        return "null"
    value_type = type(value)
    if value_type in (str, int, float, bool):
        return {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
        }[value_type]
    if isinstance(value, (list, tuple, set)):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "string"


def _combine_union_schemas(schemas):
    simple_types = []
    complex_schemas = []
    for schema in schemas:
        schema = schema.copy()
        schema_type = schema.pop("type", None)
        if schema_type is not None and not schema:
            if isinstance(schema_type, list):
                simple_types.extend(schema_type)
            else:
                simple_types.append(schema_type)
        else:
            if schema_type is not None:
                schema["type"] = schema_type
            complex_schemas.append(schema)

    combined_parts = []
    if simple_types:
        unique_types = list(dict.fromkeys(simple_types))
        if len(unique_types) == 1:
            combined_parts.append({"type": unique_types[0]})
        else:
            combined_parts.append({"type": unique_types})

    combined_parts.extend(complex_schemas)

    if not combined_parts:
        return {}
    if len(combined_parts) == 1:
        return combined_parts[0]
    return {"anyOf": combined_parts}


def _add_null_to_schema(schema):
    if not schema:
        return {"type": ["null"]}
    schema = schema.copy()
    if "type" in schema:
        current_type = schema["type"]
        types = current_type if isinstance(current_type, list) else [current_type]
        if "null" not in types:
            types = list(dict.fromkeys(types + ["null"]))
        schema["type"] = types if len(types) > 1 else types[0]
        return schema
    if "anyOf" in schema:
        schema["anyOf"] = schema["anyOf"] + [{"type": "null"}]
        return schema
    return {"anyOf": [schema, {"type": "null"}]}


def python_doc_type_to_json(type_str: str) -> Dict[str, Any]:
    """Best-effort mapping from docstring type hints to JSON Schema."""
    if not type_str:
        return {}
    cleaned = type_str.strip()
    optional = False
    if re.search(r"\boptional\b", cleaned, flags=re.IGNORECASE):
        optional = True
        cleaned = re.sub(r",?\s*optional", "", cleaned, flags=re.IGNORECASE)

    literal_match = re.search(r"Literal\[(.+)\]", cleaned)
    if literal_match:
        values = [
            value.strip().strip('"').strip("'")
            for value in literal_match.group(1).split(",")
        ]
        schema = _values_to_enum_schema(values)
        schema["type"] = "string"
        return _add_null_to_schema(schema) if optional else schema

    basic_mapping = {
        "str": {"type": "string"},
        "string": {"type": "string"},
        "int": {"type": "integer"},
        "integer": {"type": "integer"},
        "float": {"type": "number"},
        "number": {"type": "number"},
        "bool": {"type": "boolean"},
        "boolean": {"type": "boolean"},
        "dict": {"type": "object"},
        "mapping": {"type": "object"},
        "list": {"type": "array"},
        "sequence": {"type": "array"},
        "tuple": {"type": "array"},
        "set": {"type": "array", "uniqueItems": True},
        "none": {"type": "null"},
    }

    lowered = cleaned.lower()
    schema = None
    for key, value in basic_mapping.items():
        if lowered.startswith(key):
            schema = value.copy()
            break

    if schema is None:
        return {}
    return _add_null_to_schema(schema) if optional else schema


def parse_full_docstring(doc: str) -> dict:
    """
    Parse complete docstring including description, parameters, returns, examples, and notes.
    Supports Google-style, NumPy-style, and reST-style docstrings.
    """
    result = {
        "description": "",
        "parameters": {},
        "returns": "",
        "examples": [],
        "notes": "",
        "raises": []
    }

    # Extract main description (first paragraph)
    desc_match = re.match(r"^(.*?)(?=\n\n|\n[A-Z][a-z]+:|\nParameters\n-+|\Z)", doc, re.DOTALL)
    if desc_match:
        result["description"] = desc_match.group(1).strip()

    # Parse Parameters/Args
    result["parameters"] = parse_parameters(doc)

    # Parse Returns
    returns_patterns = [
        r"Returns?:\s*\n\s+(.+?)(?=\n\n[A-Z]|\n[A-Z][a-z]+:|\Z)",
        r"Returns?\s*\n-+\s*\n(.+?)(?=\n\n[A-Z]|\n[A-Z][a-z]+:|\Z)"
    ]
    for pattern in returns_patterns:
        match = re.search(pattern, doc, re.DOTALL)
        if match:
            result["returns"] = match.group(1).strip()
            break

    # Parse Examples
    examples_match = re.search(r"Examples?:\s*\n(.+?)(?=\n\n[A-Z]|\n[A-Z][a-z]+:|\Z)", doc, re.DOTALL)
    if examples_match:
        examples_text = examples_match.group(1).strip()
        result["examples"] = [ex.strip() for ex in examples_text.split("\n\n") if ex.strip()]

    # Parse Notes
    notes_match = re.search(r"Notes?:\s*\n(.+?)(?=\n\n[A-Z]|\n[A-Z][a-z]+:|\Z)", doc, re.DOTALL)
    if notes_match:
        result["notes"] = notes_match.group(1).strip()

    # Parse Raises
    raises_match = re.search(r"Raises?:\s*\n(.+?)(?=\n\n[A-Z]|\n[A-Z][a-z]+:|\Z)", doc, re.DOTALL)
    if raises_match:
        raises_text = raises_match.group(1)
        result["raises"] = re.findall(r"(\w+):\s*(.+?)(?=\n\s*\w+:|\Z)", raises_text, re.DOTALL)

    return result


def parse_parameters(doc: str) -> dict:
    """Extract parameter descriptions with type info and optional enums."""
    params = {}

    # Google-style
    google_match = re.search(r"Args?:\s*\n((?:\s+\w+.*\n?)+)", doc, re.MULTILINE)
    if google_match:
        args_block = google_match.group(1)
        lines = args_block.splitlines()
        current_name = None
        current_indent = None
        for line in lines:
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip())

            if current_name and indent > (current_indent or 0):
                params[current_name]["description"] += " " + line.strip()
                continue

            match = re.match(r"(\w+)\s*(?:\(([^)]*)\))?:\s*(.*)", line.strip())
            if match:
                name, type_str, desc = match.groups()
                params[name] = {
                    "description": desc.strip(),
                    "type": (type_str or "").strip(),
                }
                current_name = name
                current_indent = indent
        return params

    # NumPy-style
    numpy_match = re.search(r"Parameters\s*\n-+\s*\n((?:.+\n?)+?)(?=\n\n[A-Z]|\n[A-Z][a-z]+\n-+|\Z)", doc, re.DOTALL)
    if numpy_match:
        args_block = numpy_match.group(1)
        for match in re.finditer(r"(\w+)\s*:\s*(.+?)\n\s+(.+?)(?=\n\w+\s*:|\Z)", args_block, re.DOTALL):
            name, type_str, desc = match.groups()
            clean_desc = re.sub(r"\s*\n\s*", " ", desc.strip())
            params[name] = {"description": clean_desc, "type": type_str.strip()}
        return params

    return params


def parse_arg_docs(doc):
    """Legacy function - kept for backward compatibility."""
    params = parse_parameters(doc)
    return {name: info["description"] for name, info in params.items()}
