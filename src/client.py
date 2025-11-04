"""LangChain AI Agent for intelligent task execution."""
from typing import Dict, Any, Optional, List

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.markdown import Markdown
from rich.tree import Tree
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich import box
from rich.align import Align

from datetime import datetime, timezone
import json
from pathlib import Path

from .utils.config import config
from .utils.prompt import get_system_prompt

from langchain_mcp_adapters.client import MultiServerMCPClient

class AIAgentMCPClient:
    """AI Agent MCP Client powered by LangChain and OpenAI."""

    def __init__(self, mcp_client: MultiServerMCPClient):
        """
        Initialize the AI agent.
        
        Args:
            mcp_client: An instance of MultiServerMCPClient to interact with the MCP servers
        """
        self.mcp_client = mcp_client
        self.console = Console()
        self.total_tokens_used = 0
        self.conversation_count = 0
        self.show_stats = False  # Hidden by default
        self.command_history = []  # Store command history
        self.session_start_time = datetime.now(timezone.utc)
        
        self.tools = None
        self.llm = None
        self.agent = None
        
        # Note: Call initialize() explicitly after construction

    async def _initialize_agent(self):
        """Initialize LangChain agent with tools."""
        if not config.OPENAI_API_KEY:
            return
            
        try:
            # Initialize LLM
            self.llm = ChatOpenAI(
                model=config.MODEL_NAME,
                temperature=0.1,
                max_tokens=None,
                timeout=300,
                openai_api_key=config.OPENAI_API_KEY
            )
            
            # Create tool wrappers
            self.tools = await self.mcp_client.get_tools()
            
            # Enhanced system prompt
            system_prompt = get_system_prompt()

            # Create agent
            self.agent = create_agent(
                model=self.llm,
                tools=self.tools,
                debug=False,
                name="AI Agent",
                system_prompt=system_prompt
            )
            
        except Exception as e:
            print(f"Error initializing agent: {e}")
    
    async def initialize(self):
        """Public method to initialize the agent asynchronously."""
        await self._initialize_agent()
    
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
                "error": "⚠️ AI Agent not initialized. Please set OPENAI_API_KEY in your environment variables or .env file.",
                "tokens": 0
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
            
            # Calculate token usage
            tokens_used = 0
            for msg in updated_history:
                if hasattr(msg, 'usage_metadata'):
                    tokens_used += msg.usage_metadata.get('total_tokens', 0)
            
            self.total_tokens_used += tokens_used
            self.conversation_count += 1
            
            return {
                "success": True,
                "user_input": user_input,
                "response": agent_message,
                "history": updated_history,
                "error": None,
                "tokens": tokens_used
            }
        except Exception as e:
            error_msg = f"❌ Error in conversation: {str(e)}"
            if "rate_limit" in str(e).lower():
                error_msg += "\n\n💡 Tip: You've hit the rate limit. Please wait a moment and try again."
            elif "api_key" in str(e).lower():
                error_msg += "\n\n💡 Tip: Check your OPENAI_API_KEY configuration."
            elif "timeout" in str(e).lower():
                error_msg += "\n\n💡 Tip: The request timed out. Try a simpler query or check your connection."
            
            return {
                "success": False,
                "user_input": user_input,
                "response": None,
                "history": history or [],
                "error": error_msg,
                "tokens": 0
            }
    
    def _display_tool_calls(self, messages: List, previous_message_count: int = 0) -> None:
        """Display tool calls in a beautifully formatted tree structure."""
        # Only look at messages after the previous count (new messages)
        new_messages = messages[previous_message_count:] if previous_message_count > 0 else messages
        
        tool_call_count = 0
        tool_results = {}
        
        # Create main tree with styled root
        tool_calls_tree = Tree(
            Text("🔧 Tool Execution", style="bold cyan"),
            guide_style="bright_blue"
        )
        
        # First pass: collect tool calls
        for msg in new_messages:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_call_count += 1
                    
                    # Create styled tool name
                    tool_name = Text()
                    tool_name.append("⚡ ", style="yellow")
                    tool_name.append(tool_call['name'], style="bold yellow")
                    
                    tool_node = tool_calls_tree.add(tool_name)
                    
                    # Format arguments nicely
                    args_text = Text()
                    args_text.append("📋 Args: ", style="dim cyan")
                    args_text.append(str(tool_call['args']), style="dim white")
                    tool_node.add(args_text)
                    
                    tool_results[tool_call.get('id', '')] = tool_node
        
        # Second pass: add results to corresponding tool calls
        for msg in new_messages:
            if isinstance(msg, ToolMessage):
                result_preview = msg.content[:150] + "..." if len(msg.content) > 150 else msg.content
                tool_call_id = getattr(msg, 'tool_call_id', '')
                
                # Create styled result
                result_text = Text()
                result_text.append("✓ ", style="bold green")
                result_text.append("Result: ", style="green")
                result_text.append(result_preview, style="dim white")
                
                if tool_call_id in tool_results:
                    tool_results[tool_call_id].add(result_text)
                else:
                    tool_calls_tree.add(result_text)
        
        if tool_call_count > 0:
            # Create a styled panel with custom box
            panel = Panel(
                tool_calls_tree,
                title=f"[bold cyan]🔧 Tool Execution[/bold cyan] [dim]({tool_call_count} call{'s' if tool_call_count > 1 else ''})[/dim]",
                title_align="left",
                border_style="bright_cyan",
                box=box.ROUNDED,
                padding=(1, 2),
                expand=False
            )
            self.console.print(panel)
            self.console.print()  # Add spacing
    
    def _display_stats(self, tokens_used: int = None) -> Table:
        """Display comprehensive conversation statistics."""
        stats_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1), show_edge=False)
        stats_table.add_column(style="dim cyan", justify="right", no_wrap=True)
        stats_table.add_column(style="white", justify="left")
        
        # Session info
        session_duration = datetime.now() - self.session_start_time
        hours, remainder = divmod(int(session_duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours}h {minutes}m {seconds}s" if hours > 0 else f"{minutes}m {seconds}s"
        
        stats_table.add_row("Session duration:", duration_str)
        stats_table.add_row("", "")  # Spacer
        
        # Token stats
        if tokens_used is not None:
            stats_table.add_row("Tokens (this turn):", f"{tokens_used:,}")
        stats_table.add_row("Total tokens:", f"{self.total_tokens_used:,}")
        stats_table.add_row("Conversations:", f"{self.conversation_count}")
        
        if self.conversation_count > 0:
            avg_tokens = self.total_tokens_used // self.conversation_count
            stats_table.add_row("Avg tokens/turn:", f"{avg_tokens:,}")
        
        # Estimated cost (rough estimate for gpt-4o-mini)
        estimated_cost = (self.total_tokens_used / 1_000_000) * 0.15  # $0.15 per 1M tokens
        if estimated_cost > 0:
            stats_table.add_row("", "")  # Spacer
            stats_table.add_row("Est. cost:", f"${estimated_cost:.4f}")
        
        return stats_table
    
    def _display_welcome_banner(self) -> None:
        """Display an enhanced welcome banner with system info."""
        banner = Text()
        banner.append("╔══════════════════════════════════════════╗\n", style="bright_blue")
        banner.append("║     ", style="bright_blue")
        banner.append("🤖  AI AGENT CHAT INTERFACE", style="bold bright_blue")
        banner.append("     ║\n", style="bright_blue")
        banner.append("╚══════════════════════════════════════════╝", style="bright_blue")
        
        self.console.print(Align.center(banner))
        self.console.print()
        
        # Display system info
        info_table = Table.grid(padding=(0, 2))
        info_table.add_column(style="dim", justify="right")
        info_table.add_column(style="bold cyan")

        info_table.add_row("Model:", config.MODEL_NAME)
        info_table.add_row("Tools:", f"{len(self.tools)}")
        info_table.add_row("Started:", self.session_start_time.strftime("%H:%M:%S"))
        
        self.console.print(Align.center(info_table))
        self.console.print()
        
        # Display enhanced help
        help_table = Table.grid(padding=(0, 1))
        help_table.add_column(style="bold cyan", width=20)
        help_table.add_column(style="white")
        
        help_table.add_row("💬 Chat", "Type your message naturally")
        help_table.add_row("📊 stats", "View session statistics")
        help_table.add_row("📋 export", "Export conversation to file")
        help_table.add_row("🔍 tools", "List available tools")
        help_table.add_row("🐛 debug on/off", "Toggle debug mode")
        help_table.add_row("🧹 clear", "Clear screen")
        help_table.add_row("🚪 exit/quit", "End session")
        
        help_panel = Panel(
            help_table,
            title="[dim]Commands[/dim]",
            border_style="dim blue",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        self.console.print(Align.center(help_panel))
        self.console.print()
        self.console.print(Rule(style="dim blue"))
        self.console.print()
    
    def _list_tools(self) -> None:
        """Display available tools in a formatted table."""
        tools_table = Table(title="🔧 Available Tools", box=box.ROUNDED, show_header=True, header_style="bold cyan")
        tools_table.add_column("Tool", style="yellow", no_wrap=True)
        tools_table.add_column("Description", style="white")
        
        tool_descriptions = {
            "weather_tool": "Get weather information",
            "news_tool": "Fetch latest news",
            "file_create_tool": "Create files",
            "file_read_tool": "Read files",
            "file_delete_tool": "Delete files",
            "file_search_tool": "Search files",
            "list_directory_tool": "List directory contents",
            "web_fetch_tool": "Fetch webpage content",
            "calculator_tool": "Mathematical calculations",
            "unit_converter_tool": "Convert units"
        }
        
        for tool in self.tools:
            tool_name = tool.name
            description = tool_descriptions.get(tool_name, "No description")
            tools_table.add_row(tool_name, description)
        
        self.console.print(tools_table)
        self.console.print()
    
    def _export_conversation(self, result: Dict[str, Any]) -> None:
        """Export conversation history to a file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)
            
            filename = export_dir / f"conversation_{timestamp}.json"
            
            # Prepare export data
            export_data = {
                "session_info": {
                    "start_time": self.session_start_time.isoformat(),
                    "export_time": datetime.now().isoformat(),
                    "total_conversations": self.conversation_count,
                    "total_tokens": self.total_tokens_used
                },
                "conversations": []
            }
            
            # Extract conversations from history
            if result.get("history"):
                for msg in result["history"]:
                    msg_data = {
                        "type": msg.__class__.__name__,
                        "content": getattr(msg, 'content', ''),
                    }
                    if hasattr(msg, 'tool_calls'):
                        msg_data["tool_calls"] = msg.tool_calls
                    export_data["conversations"].append(msg_data)
            
            # Write to file
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.console.print(f"[green]✓ Conversation exported to:[/green] {filename}\n")
            
        except Exception as e:
            self.console.print(f"[red]✗ Export failed:[/red] {str(e)}\n")
    
    def _get_user_input_styled(self) -> str:
        """Get user input with enhanced styling and hints."""
        timestamp = datetime.now().strftime("%H:%M")
        
        prompt_text = Text()
        prompt_text.append(f"[{timestamp}] ", style="dim")
        prompt_text.append("💬 ", style="bold green")
        prompt_text.append("You", style="bold green")
        prompt_text.append(" › ", style="dim")
        
        user_input = Prompt.ask(prompt_text)
        
        # Add to command history
        if user_input and user_input not in ["", " "]:
            self.command_history.append(user_input)
        
        return user_input
    
    async def chat(self, callback=None) -> None:
        """
        Start an enhanced developer-friendly interactive conversation loop.
        
        Args:
            callback: Optional callback function to handle custom input/output.
        """
        if not self.agent:
            self.console.print(Panel(
                Text("❌ AI Agent not initialized. Please set OPENAI_API_KEY.", style="bold red"),
                border_style="red",
                box=box.HEAVY
            ))
            return
        
        # Clear screen and display welcome banner
        self.console.clear()
        self._display_welcome_banner()
        
        result = dict()
        previous_message_count = 0
        
        while True:
            try:
                # Get user input
                if callback:
                    user_input = callback("You: ")
                else:
                    user_input = self._get_user_input_styled()
                
                if not user_input or user_input.strip() == "":
                    continue
                
                user_input = user_input.strip()
                
                # Handle special commands
                if user_input.lower() in ["exit", "quit", "bye"]:
                    # Show goodbye with comprehensive stats
                    session_duration = datetime.now() - self.session_start_time
                    minutes = int(session_duration.total_seconds() / 60)
                    
                    goodbye_text = Text()
                    goodbye_text.append("👋 ", style="yellow")
                    goodbye_text.append("Thanks for chatting!\n\n", style="bold yellow")
                    goodbye_text.append(f"Session Summary:\n", style="bold cyan")
                    goodbye_text.append(f"  • Duration: {minutes} minutes\n", style="white")
                    goodbye_text.append(f"  • Conversations: {self.conversation_count}\n", style="white")
                    goodbye_text.append(f"  • Total tokens: {self.total_tokens_used:,}\n", style="white")
                    goodbye_text.append(f"  • Commands used: {len(self.command_history)}", style="white")
                    
                    self.console.print()
                    self.console.print(Panel(
                        goodbye_text,
                        border_style="yellow",
                        box=box.DOUBLE,
                        padding=(1, 2)
                    ))
                    break
                
                if user_input.lower() == "clear":
                    self.console.clear()
                    self._display_welcome_banner()
                    continue
                
                if user_input.lower() == "stats":
                    stats_content = self._display_stats()
                    stats_panel = Panel(
                        stats_content,
                        title="[bold cyan]📊 Session Statistics[/bold cyan]",
                        border_style="cyan",
                        box=box.ROUNDED,
                        padding=(1, 2)
                    )
                    self.console.print(stats_panel)
                    self.console.print()
                    continue
                
                if user_input.lower() == "tools":
                    self._list_tools()
                    continue
                
                if user_input.lower() == "export":
                    self._export_conversation(result)
                    continue
                
                if user_input.lower() == "history":
                    if self.command_history:
                        history_panel = Panel(
                            "\n".join(f"{i+1}. {cmd}" for i, cmd in enumerate(self.command_history[-10:])),
                            title="[bold cyan]📜 Recent Commands[/bold cyan]",
                            border_style="cyan",
                            box=box.ROUNDED
                        )
                        self.console.print(history_panel)
                        self.console.print()
                    else:
                        self.console.print("[dim]No command history yet[/dim]\n")
                    continue
                
                if user_input.lower().startswith("debug"):
                    if "on" in user_input.lower():
                        self.show_stats = True
                        self.console.print("[green]✓ Debug mode enabled[/green] - Token stats will be shown\n")
                    elif "off" in user_input.lower():
                        self.show_stats = False
                        self.console.print("[yellow]✓ Debug mode disabled[/yellow] - Token stats hidden\n")
                    else:
                        status = "[green]enabled[/green]" if self.show_stats else "[red]disabled[/red]"
                        self.console.print(f"Debug mode is currently {status}\n")
                    continue
                
                if user_input.lower() in ["help", "?", "h"]:
                    self._display_welcome_banner()
                    continue
                
                self.console.print()  # Add spacing
                
                # Show enhanced progress indicator
                with Progress(
                    SpinnerColumn(spinner_name="dots12", style="cyan"),
                    TextColumn("[bold blue]Processing..."),
                    BarColumn(complete_style="cyan", finished_style="green"),
                    TimeElapsedColumn(),
                    console=self.console,
                    transient=True
                ) as progress:
                    task = progress.add_task("", total=None)
                    result = await self.agent_conversation(
                        user_input,
                        result.get("history", None)
                    )
                
                if result["success"]:
                    # Display tool calls
                    if result.get("history"):
                        self._display_tool_calls(result["history"], previous_message_count)
                        previous_message_count = len(result["history"])
                    
                    # Display agent response
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    title_text = Text()
                    title_text.append("🤖 Agent", style="bold blue")
                    title_text.append(f" • {timestamp}", style="dim")
                    
                    agent_panel = Panel(
                        Markdown(result["response"]),
                        title=title_text,
                        title_align="left",
                        border_style="bright_blue",
                        box=box.ROUNDED,
                        padding=(1, 2)
                    )
                    self.console.print(agent_panel)
                    
                    # Show debug stats if enabled
                    if self.show_stats:
                        self.console.print()
                        stats_table = self._display_stats(result.get("tokens", 0))
                        self.console.print(stats_table)
                    
                else:
                    # Enhanced error display
                    error_text = Text()
                    error_text.append("❌ Error\n\n", style="bold red")
                    error_text.append(result["error"], style="red")
                    error_text.append("\n\n💡 Tip: ", style="dim yellow")
                    error_text.append("Try rephrasing your question or check the logs", style="dim")
                    
                    error_panel = Panel(
                        error_text,
                        border_style="red",
                        box=box.HEAVY,
                        padding=(1, 2)
                    )
                    self.console.print(error_panel)
                
                # Subtle separator
                self.console.print()
                self.console.print(Rule(characters="·", style="dim blue"))
                self.console.print()
                    
            except KeyboardInterrupt:
                self.console.print("\n")
                if Confirm.ask("[yellow]⚠️  Exit session?[/yellow]", default=False):
                    self.console.print(Panel(
                        Text("👋 Session ended", style="bold yellow"),
                        border_style="yellow",
                        box=box.ROUNDED
                    ))
                    break
                else:
                    self.console.print("[dim]Continuing...[/dim]\n")
                    continue
                    
            except Exception as e:
                self.console.print()
                self.console.print(Panel(
                    Text.assemble(
                        ("💥 System Error\n\n", "bold red"),
                        (f"{type(e).__name__}: ", "red"),
                        (str(e), "white"),
                        ("\n\n", ""),
                        ("The agent will continue running", "dim yellow")
                    ),
                    border_style="red",
                    box=box.HEAVY,
                    padding=(1, 2)
                ))
                self.console.print()
    
    def is_available(self) -> bool:
        """Check if the agent is available."""
        return self.agent is not None

async def main():
    """Main function to run the AI agent MCP Client chat."""

    mcp_client = MultiServerMCPClient(
        {
            "stdio-server": {
                "transport": "stdio",
                "command": "uv",
                "args": [
                    "run",
                    "python",
                    "-m",
                    "src.server"
                ],
		    }
        }
    )

    agent = AIAgentMCPClient(mcp_client)
    await agent.initialize()  # Explicitly initialize the agent
    await agent.chat()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

