"""LangChain AI Agent for intelligent task execution."""
from typing import Dict, Any, Optional, List
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..utils.config import config

class AIAgent:
    """AI Agent powered by LangChain and OpenAI."""
    
    def __init__(self, tools: List[Tool]):
        """
        Initialize the AI agent.
        
        Args:
            tools: List of LangChain tools available to the agent
        """
        self.tools = tools
        self.llm = None
        self.agent_executor = None
        
        if config.OPENAI_API_KEY:
            self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize LangChain agent with tools."""
        try:
            # Initialize LLM
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.7,
                openai_api_key=config.OPENAI_API_KEY
            )
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a helpful AI agent with access to various tools.
                You can fetch weather data, search news, manage files, browse websites, and perform calculations.
                Always use the appropriate tools to complete tasks.
                Be concise but thorough in your responses.
                If you encounter an error, explain it clearly and suggest alternatives."""),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            # create agent
            self.agent_executor = create_agent(
                model=self.llm,
                tools=self.tools,
                system_prompt=prompt,
                #max_iterations=5,
                #verbose=True,
                #handle_parsing_errors=True
            )
            
        except Exception as e:
            print(f"Error initializing agent: {e}")
            self.agent_executor = None
    
    async def execute_task(self, task: str) -> Dict[str, Any]:
        """
        Execute a task using the AI agent.
        
        Args:
            task: Task description in natural language
            
        Returns:
            Task execution result
        """
        if not self.agent_executor:
            return {
                "success": False,
                "task": task,
                "result": None,
                "error": "AI Agent not initialized. Please set OPENAI_API_KEY."
            }
        
        try:
            result = await self.agent_executor.ainvoke({"input": task})
            
            return {
                "success": True,
                "task": task,
                "result": result.get("output", ""),
                "steps": result.get("intermediate_steps", []),
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "task": task,
                "result": None,
                "error": f"Error executing task: {str(e)}"
            }
    
    def is_available(self) -> bool:
        """Check if the agent is available."""
        return self.agent_executor is not None
