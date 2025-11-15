"""Weather tool for fetching current weather data."""

import httpx
from typing import Dict, Any
from ..utils.config import config


class WeatherTool:
    """Tool for fetching weather information."""

    def __init__(self):
        self.api_key = config.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    async def get_weather(self, location: str) -> Dict[str, Any]:
        """
        Get current weather for a location.

        Args:
            location: City name or "City, Country Code"

        Returns:
            Dictionary with weather information
        """
        if not self.api_key:
            return {
                "error": "Weather API key not configured",
                "location": location,
                "data": None,
            }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={"q": location, "appid": self.api_key, "units": "metric"},
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "location": data.get("name", location),
                    "country": data.get("sys", {}).get("country", ""),
                    "temperature": data.get("main", {}).get("temp"),
                    "feels_like": data.get("main", {}).get("feels_like"),
                    "humidity": data.get("main", {}).get("humidity"),
                    "description": data.get("weather", [{}])[0].get("description", ""),
                    "wind_speed": data.get("wind", {}).get("speed"),
                    "error": None,
                }
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP error: {e.response.status_code}",
                "location": location,
                "data": None,
            }
        except Exception as e:
            return {
                "error": f"Error fetching weather: {str(e)}",
                "location": location,
                "data": None,
            }


weather_tool = WeatherTool()
