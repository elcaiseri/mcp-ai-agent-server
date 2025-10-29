"""LangChain AI Agent for intelligent task execution."""
from typing import Dict, Any, Optional, List
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from ..utils.config import config

from ..tools.news import news_tool
from ..tools.weather import weather_tool
from ..tools.file_manager import file_manager
from ..tools.web_fetcher import web_fetcher
from ..tools.calculator import calculator

class AIAgent:
    """AI Agent powered by LangChain and OpenAI."""
    
    def __init__(self, tools_dict: Dict[str, Any]):
        """
        Initialize the AI agent.
        
        Args:
            tools_dict: Dictionary mapping tool names to their implementations
        """
        self.tools_dict = tools_dict
        self.tools = self._create_tool_wrappers()

        self.llm = None
        self.agent = None
        
        if config.OPENAI_API_KEY:
            self._initialize_agent()
    
    def _create_tool_wrappers(self) -> List:
        """Create LangChain tool wrappers for all tools."""
        tools = []
        
        # Weather tools
        if "get_weather" in self.tools_dict:
            @tool(
                "weather_tool",
                description="Get current weather information for a specific location. Input should be a location string (city, state/country).",
            )
            async def get_weather(location: str) -> str:
                return await self.tools_dict["get_weather"](location)
            tools.append(get_weather)
        
        # News tools
        if "fetch_news" in self.tools_dict:
            @tool(
                "news_tool",
                description="Useful for getting the latest news headlines about a specific topic or person. Input should be a single string representing the topic or person's name.",
            )
            async def fetch_news(topic: str, limit: int = 10, language: str = "en") -> str:
                return await self.tools_dict["fetch_news"](topic, limit, language)
            tools.append(fetch_news)
        
        # File management tools
        if "create_file" in self.tools_dict:
            @tool(
                "file_create_tool",
                description="Create a new file with specified content. Input should be filename and content.",
            )
            async def create_file(filename: str, content: str) -> str:
                return await self.tools_dict["create_file"](filename, content)
            tools.append(create_file)
        
        if "read_file" in self.tools_dict:
            @tool(
                "file_read_tool", 
                description="Read content from an existing file. Input should be the filename.",
            )
            async def read_file(filename: str) -> str:
                return await self.tools_dict["read_file"](filename)
            tools.append(read_file)
        
        if "delete_file" in self.tools_dict:
            @tool(
                "file_delete_tool",
                description="Delete an existing file. Input should be the filename.",
            )
            async def delete_file(filename: str) -> str:
                return await self.tools_dict["delete_file"](filename)
            tools.append(delete_file)
        
        if "search_files" in self.tools_dict:
            @tool(
                "file_search_tool",
                description="Search for files in directories. Input should be search parameters.",
            )
            async def search_files(pattern: str) -> str:
                return await self.tools_dict["search_files"](pattern)
            tools.append(search_files)
        
        if "list_directory" in self.tools_dict:
            @tool(
                "list_directory_tool",
                description="List contents of a directory. Input should be directory path.",
            )
            async def list_directory(path: str = ".") -> str:
                return await self.tools_dict["list_directory"](path)
            tools.append(list_directory)
        
        # Web tools
        if "fetch_webpage" in self.tools_dict:
            @tool(
                "web_fetch_tool",
                description="Fetch content from a webpage. Input should be a valid URL.",
            )
            async def fetch_webpage(url: str) -> str:
                return await self.tools_dict["fetch_webpage"](url)
            tools.append(fetch_webpage)
        
        # Calculator tools
        if "calculate" in self.tools_dict:
            @tool(
                "calculator_tool",
                description="Perform mathematical calculations. Input should be a mathematical expression as a string.",
            )
            def calculate(expression: str) -> str:
                return self.tools_dict["calculate"](expression)
            tools.append(calculate)
        
        if "convert_units" in self.tools_dict:
            @tool(
                "unit_converter_tool",
                description="Convert between different units. Supported conversions: Temperature (celsius, fahrenheit, kelvin), Length (meter, kilometer, mile, foot, inch), Weight (kilogram, gram, pound, ounce). Input format: value (float), from_unit (str), to_unit (str).",
            )
            async def convert_units(value: float, from_unit: str, to_unit: str) -> str:
                return await self.tools_dict["convert_units"](value, from_unit, to_unit)
            tools.append(convert_units)

        
        return tools
    
    def _initialize_agent(self):
        """Initialize LangChain agent with tools."""
        try:
            # Initialize LLM
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                max_tokens=None,
                timeout=60,
                openai_api_key=config.OPENAI_API_KEY
            )
            
            # Create tool wrappers
            tools = self._create_tool_wrappers()

            assert len(tools) == len(self.tools_dict), "Mismatch in number of tools created."
            
            # Create agent
            self.agent = create_agent(
                model=self.llm,
                tools=tools,
                debug=False,
                name="AI Agent",
                system_prompt="You're an AI agent that helps users fetch news, weather updates, manage files, fetch web content, and perform calculations efficiently. Always use the appropriate tools to complete tasks. Be concise but thorough in your responses."
            )
            
        except Exception as e:
            print(f"Error initializing agent: {e}")
            self.agent = None
    
    async def agent_conversation(
        self, 
        user_input: str, 
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Have a conversation with the AI agent.
        
        Args:
            user_input: User's message or query
            history: Optional separate conversation history. If None, starts fresh.
            
        Returns:
            Agent's response with conversation context
        """
        if not self.agent:
            return {
                "success": False,
                "user_input": user_input,
                "response": None,
                "history": history or [],
                "error": "AI Agent not initialized. Please set OPENAI_API_KEY."
            }
        
        try:
            # Use provided history or start fresh
            conversation_history = history if history is not None else []
            
            # Add user message to history
            conversation_history.append({"role": "user", "content": user_input})
            
            # Execute agent with conversation history
            inputs = {"messages": conversation_history}
            result = await self.agent.ainvoke(inputs)
            
            # Extract agent response
            agent_message = result["messages"][-1].content
            
            # Update history with full conversation
            updated_history = result["messages"]
            
            return {
                "success": True,
                "user_input": user_input,
                "response": agent_message,
                "history": updated_history,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "user_input": user_input,
                "response": None,
                "history": history or [],
                "error": f"Error in conversation: {str(e)}"
            }
    
    async def chat(self, callback=None) -> None:
        """
        Start an interactive conversation loop.
        
        Args:
            callback: Optional callback function to handle custom input/output.
                     Should accept (prompt: str) and return user input string.
                     If None, uses basic input().
        """
        if not self.agent:
            print("AI Agent not initialized. Please set OPENAI_API_KEY.")
            return
        
        print("🤖 AI Agent Chat")
        print("Type 'exit' or 'quit' to end the conversation\n")
        result = dict()
        while True:
            try:
                # Get user input
                if callback:
                    user_input = callback("You: ")
                else:
                    user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit"]:
                    print("👋 Goodbye!")
                    break
                
                # Process with agent
                result = await self.agent_conversation(user_input, result.get("history", None))
                
                if result["success"]:
                    print(f"\n🤖 Agent: {result['response']}\n")
                else:
                    print(f"\n❌ Failed: {result['error']}\n")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")
    
    def is_available(self) -> bool:
        """Check if the agent is available."""
        return self.agent is not None

async def main():
    """Main function to run the AI agent chat."""
    tools_dict = {
        # Weather tools
        "get_weather": weather_tool.get_weather,
        
        # News tools
        "fetch_news": news_tool.fetch_news,
        
        # File management tools
        "create_file": file_manager.create_file,
        "read_file": file_manager.read_file,
        "delete_file": file_manager.delete_file,
        "search_files": file_manager.search_files,
        "list_directory": file_manager.list_directory,
        
        # Web tools
        "fetch_webpage": web_fetcher.fetch_webpage,
        
        # Calculator tools
        "calculate": calculator.calculate,
        "convert_units": calculator.convert_units,
    }

    agent = AIAgent(tools_dict)
    await agent.chat()

if __name__ == "__main__":
    tools_dict = {
        # Weather tools
        "get_weather": weather_tool.get_weather,
        
        # News tools
        "fetch_news": news_tool.fetch_news,
        
        # File management tools
        "create_file": file_manager.create_file,
        "read_file": file_manager.read_file,
        "delete_file": file_manager.delete_file,
        "search_files": file_manager.search_files,
        "list_directory": file_manager.list_directory,
        
        # Web tools
        "fetch_webpage": web_fetcher.fetch_webpage,
    }

    agent = AIAgent(tools_dict)

    if agent.is_available():
        import asyncio
        asyncio.run(agent.chat())

