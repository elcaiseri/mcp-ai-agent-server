"""Calculator tool for mathematical operations."""

import math
from typing import Dict, Any


class CalculatorTool:
    """Tool for performing calculations."""

    async def calculate(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression safely.

        Args:
            expression: Mathematical expression (e.g., "2 + 2", "sqrt(16)")

        Returns:
            Calculation result
        """
        try:
            # Define safe functions
            safe_functions = {
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "sum": sum,
                "sqrt": math.sqrt,
                "pow": pow,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "log": math.log,
                "log10": math.log10,
                "exp": math.exp,
                "pi": math.pi,
                "e": math.e,
            }

            # Clean the expression
            expression = expression.strip()

            # Evaluate safely
            result = eval(expression, {"__builtins__": {}}, safe_functions)

            return {
                "success": True,
                "expression": expression,
                "result": result,
                "error": None,
            }
        except ZeroDivisionError:
            return {
                "success": False,
                "expression": expression,
                "result": None,
                "error": "Division by zero",
            }
        except Exception as e:
            return {
                "success": False,
                "expression": expression,
                "result": None,
                "error": f"Error calculating: {str(e)}",
            }

    async def convert_units(
        self, value: float, from_unit: str, to_unit: str
    ) -> Dict[str, Any]:
        """
        Convert between units.

        Args:
            value: Numeric value to convert
            from_unit: Unit to convert from
            to_unit: Unit to convert to

        Supported conversions:
        - Temperature: celsius, fahrenheit, kelvin
        - Length: meter, kilometer, mile, foot, inch
        - Weight: kilogram, gram, pound, ounce
        """
        conversions = {
            # Temperature
            ("celsius", "fahrenheit"): lambda x: (x * 9 / 5) + 32,
            ("fahrenheit", "celsius"): lambda x: (x - 32) * 5 / 9,
            ("celsius", "kelvin"): lambda x: x + 273.15,
            ("kelvin", "celsius"): lambda x: x - 273.15,
            # Length
            ("meter", "kilometer"): lambda x: x / 1000,
            ("kilometer", "meter"): lambda x: x * 1000,
            ("mile", "kilometer"): lambda x: x * 1.60934,
            ("kilometer", "mile"): lambda x: x / 1.60934,
            ("foot", "meter"): lambda x: x * 0.3048,
            ("meter", "foot"): lambda x: x / 0.3048,
            # Weight
            ("kilogram", "pound"): lambda x: x * 2.20462,
            ("pound", "kilogram"): lambda x: x / 2.20462,
            ("kilogram", "gram"): lambda x: x * 1000,
            ("gram", "kilogram"): lambda x: x / 1000,
        }

        key = (from_unit.lower(), to_unit.lower())

        if key in conversions:
            result = conversions[key](value)
            return {
                "success": True,
                "value": value,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "result": result,
                "error": None,
            }
        else:
            return {
                "success": False,
                "value": value,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "result": None,
                "error": f"Conversion from {from_unit} to {to_unit} not supported",
            }


calculator = CalculatorTool()
