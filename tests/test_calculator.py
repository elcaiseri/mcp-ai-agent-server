"""Tests for calculator tool."""
from src.tools.calculator import calculator

def test_basic_calculation():
    """Test basic arithmetic."""
    result = calculator.calculate("2 + 2")
    assert result["success"] is True
    assert result["result"] == 4

def test_complex_calculation():
    """Test complex math operations."""
    result = calculator.calculate("sqrt(16) + pow(2, 3)")
    assert result["success"] is True
    assert result["result"] == 12.0

def test_division_by_zero():
    """Test division by zero error handling."""
    result = calculator.calculate("10 / 0")
    assert result["success"] is False
    assert "zero" in result["error"].lower()

def test_unit_conversion():
    """Test unit conversion."""
    result = calculator.convert_units(100, "celsius", "fahrenheit")
    assert result["success"] is True
    assert result["result"] == 212.0
    
    result = calculator.convert_units(1000, "meter", "kilometer")
    assert result["success"] is True
    assert result["result"] == 1.0

def test_invalid_conversion():
    """Test invalid unit conversion."""
    result = calculator.convert_units(100, "invalid_unit", "another_invalid")
    assert result["success"] is False
    assert "not supported" in result["error"]
