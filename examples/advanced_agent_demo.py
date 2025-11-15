"""
Advanced AI Agent Example
Demonstrates complex multi-tool workflows
"""
import asyncio
import json
from src.agent.ai_agent import AIAgent
from langchain.tools import Tool as LangChainTool
from src.tools.weather_tools import weather_tool
from src.tools.news_tools import news_tool
from src.tools.file_manager_tools import file_manager
from src.tools.web_fetcher_tools import web_fetcher
from src.tools.calculator_tools import calculator

async def setup_agent():
    """Setup the AI agent with all tools."""
    tools = [
        LangChainTool(
            name="get_weather",
            func=lambda location: asyncio.run(weather_tool.get_weather(location)),
            description="Get current weather for a location"
        ),
        LangChainTool(
            name="fetch_news",
            func=lambda topic: asyncio.run(news_tool.fetch_news(topic, limit=3)),
            description="Fetch recent news articles"
        ),
        LangChainTool(
            name="create_file",
            func=lambda args: asyncio.run(
                file_manager.create_file(args["path"], args["content"])
            ),
            description="Create a file with content"
        ),
        LangChainTool(
            name="calculate",
            func=lambda expr: calculator.calculate(expr),
            description="Perform calculations"
        ),
    ]
    
    return AIAgent(tools)

async def example_weather_report():
    """
    Example: Generate a weather report for multiple cities
    and save to a file.
    """
    print("\n" + "="*60)
    print("Example 1: Multi-City Weather Report")
    print("="*60)
    
    agent = await setup_agent()
    
    if not agent.is_available():
        print("⚠️  AI Agent not available. Set OPENAI_API_KEY in .env")
        return
    
    task = """
    Check the weather in Tokyo, New York, and London.
    Compare the temperatures and create a summary report.
    Save the report to a file called 'weather_report.txt'.
    """
    
    result = await agent.execute_task(task)
    
    print("\n📋 Task:", task.strip())
    print("\n✅ Result:")
    print(result["result"])
    
    if result.get("steps"):
        print("\n🔍 Steps taken:")
        for i, step in enumerate(result["steps"], 1):
            print(f"   {i}. {step}")

async def example_news_analysis():
    """
    Example: Fetch news, analyze, and create summary.
    """
    print("\n" + "="*60)
    print("Example 2: News Analysis")
    print("="*60)
    
    agent = await setup_agent()
    
    if not agent.is_available():
        print("⚠️  AI Agent not available. Set OPENAI_API_KEY in .env")
        return
    
    task = """
    Fetch the latest news about 'renewable energy'.
    Analyze the sentiment and main topics.
    Create a bullet-point summary and save it to 'news_summary.txt'.
    """
    
    result = await agent.execute_task(task)
    
    print("\n📋 Task:", task.strip())
    print("\n✅ Result:")
    print(result["result"])

async def example_data_workflow():
    """
    Example: Complex data workflow with calculations.
    """
    print("\n" + "="*60)
    print("Example 3: Data Processing Workflow")
    print("="*60)
    
    agent = await setup_agent()
    
    if not agent.is_available():
        print("⚠️  AI Agent not available. Set OPENAI_API_KEY in .env")
        return
    
    task = """
    1. Calculate the average of these temperatures: 20, 25, 22, 28, 21
    2. Convert the average from Celsius to Fahrenheit
    3. Create a file called 'temperature_analysis.txt' with the results
    """
    
    result = await agent.execute_task(task)
    
    print("\n📋 Task:", task.strip())
    print("\n✅ Result:")
    print(result["result"])

async def example_without_agent():
    """
    Example: Direct tool usage without AI agent.
    Useful when you know exactly which tools to use.
    """
    print("\n" + "="*60)
    print("Example 4: Direct Tool Usage (No AI Agent)")
    print("="*60)
    
    # Get weather for multiple cities
    cities = ["Paris", "Berlin", "Madrid"]
    weather_data = []
    
    print("\n🌍 Fetching weather for:", ", ".join(cities))
    for city in cities:
        result = await weather_tool.get_weather(city)
        if result.get("error"):
            print(f"   ⚠️  {city}: {result['error']}")
        else:
            temp = result.get("temperature", "N/A")
            desc = result.get("description", "N/A")
            weather_data.append({
                "city": city,
                "temperature": temp,
                "description": desc
            })
            print(f"   ✅ {city}: {temp}°C, {desc}")
    
    # Create a summary file
    if weather_data:
        content = "Weather Report\n" + "="*40 + "\n\n"
        for data in weather_data:
            content += f"{data['city']}: {data['temperature']}°C\n"
            content += f"   Conditions: {data['description']}\n\n"
        
        result = await file_manager.create_file(
            "direct_weather_report.txt",
            content
        )
        
        if result["success"]:
            print(f"\n📄 Report saved to: {result['path']}")

async def run_all_examples():
    """Run all example scenarios."""
    print("\n" + "="*60)
    print("🤖 MCP AI Agent - Advanced Examples")
    print("="*60)
    
    # Example 4 doesn't require AI agent
    await example_without_agent()
    
    # Check if AI agent is available
    test_agent = await setup_agent()
    if not test_agent.is_available():
        print("\n" + "="*60)
        print("⚠️  AI Agent Examples Skipped")
        print("="*60)
        print("\nTo run AI agent examples:")
        print("1. Set OPENAI_API_KEY in your .env file")
        print("2. Run this script again")
        return
    
    # Run AI agent examples
    await example_weather_report()
    await example_news_analysis()
    await example_data_workflow()
    
    print("\n" + "="*60)
    print("✅ All examples completed!")
    print("="*60)
    print("\nCheck the mcp_data directory for generated files.")

if __name__ == "__main__":
    asyncio.run(run_all_examples())
