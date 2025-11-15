"""Example usage scripts for the MCP AI Agent Server."""
import asyncio
import json
from src.tools.weather_tools import weather_tool
from src.tools.news_tools import news_tool
from src.tools.file_manager_tools import file_manager
from src.tools.web_fetcher_tools import web_fetcher
from src.tools.calculator_tools import calculator

async def demo_weather():
    """Demo: Fetch weather data."""
    print("\n=== Weather Demo ===")
    result = await weather_tool.get_weather("Tokyo")
    print(json.dumps(result, indent=2))

async def demo_news():
    """Demo: Fetch news articles."""
    print("\n=== News Demo ===")
    result = await news_tool.fetch_news("artificial intelligence", limit=3)
    print(json.dumps(result, indent=2))

async def demo_file_operations():
    """Demo: File management."""
    print("\n=== File Operations Demo ===")
    
    # Create a file
    result = await file_manager.create_file(
        "demo/example.txt",
        "This is a demo file created by the MCP AI Agent!"
    )
    print("Create:", json.dumps(result, indent=2))
    
    # Read the file
    result = await file_manager.read_file("demo/example.txt")
    print("Read:", json.dumps(result, indent=2))
    
    # Search files
    result = file_manager.search_files("demo", "*.txt")
    print("Search:", json.dumps(result, indent=2))

async def demo_web_fetcher():
    """Demo: Fetch webpage content."""
    print("\n=== Web Fetcher Demo ===")
    result = await web_fetcher.fetch_webpage("https://example.com")
    print(json.dumps(result, indent=2))

def demo_calculator():
    """Demo: Mathematical calculations."""
    print("\n=== Calculator Demo ===")
    
    # Basic calculation
    result = calculator.calculate("(10 + 5) * 2")
    print("Calculate:", json.dumps(result, indent=2))
    
    # Unit conversion
    result = calculator.convert_units(25, "celsius", "fahrenheit")
    print("Convert:", json.dumps(result, indent=2))

async def run_all_demos():
    """Run all demonstrations."""
    print("=" * 60)
    print("MCP AI Agent Server - Usage Examples")
    print("=" * 60)
    
    await demo_weather()
    await demo_news()
    await demo_file_operations()
    await demo_web_fetcher()
    demo_calculator()
    
    print("\n" + "=" * 60)
    print("All demos completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_all_demos())
