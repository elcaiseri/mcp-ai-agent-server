"""Tests for the weather tool."""
import pytest
from src.tools.weather_tools import weather_tool

@pytest.mark.asyncio
async def test_weather_without_api_key(monkeypatch):
    """Test weather tool without API key."""
    monkeypatch.setattr("src.tools.weather.weather_tool.api_key", "")
    
    result = await weather_tool.get_weather("New York")
    
    assert result["error"] is not None
    assert "not configured" in result["error"]

@pytest.mark.asyncio
async def test_weather_invalid_location():
    """Test weather tool with invalid location."""
    result = await weather_tool.get_weather("InvalidCityName12345XYZ")
    
    # Should handle error gracefully
    assert "location" in result
