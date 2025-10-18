#!/usr/bin/env python3
"""
Simple reservation agent using Anthropic AI with MCP client integration.
"""
import asyncio
import argparse
import json
import os
import subprocess
import sys
import logging
import signal
from pathlib import Path
from typing import Dict, List, Any, Optional
import tempfile
from contextlib import AsyncExitStack

from dotenv import load_dotenv
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.rule import Rule
from rich.columns import Columns
from rich.table import Table
from rich.syntax import Syntax

# Set up console and logging
console = Console()
logging.basicConfig(
    level=logging.WARNING,  # Reduced to WARNING to hide excessive logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReservationAgent:
    """Agent that uses Anthropic AI with MCP tools for reservation management."""
    
    def __init__(self, anthropic_api_key: str, data_directory: str):
        """Initialize the agent with API key and data directory."""
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)
        self.data_directory = Path(data_directory)
        self.mcp_session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.available_tools: Dict[str, Dict] = {}
        
        # Ensure data directory exists
        self.data_directory.mkdir(parents=True, exist_ok=True)
    
    async def start_mcp_server(self) -> None:
        """Start MCP server as subprocess and connect via stdio."""
        try:
            with console.status("[bold blue]Starting MCP server...", spinner="dots"):
                # Start the MCP server as subprocess
                server_params = StdioServerParameters(
                    command="python",
                    args=["-m", "src.server", str(self.data_directory)],
                    env=None
                )
                
                # Use the proven pattern from working MCP CLI
                stdio_transport = await self.exit_stack.enter_async_context(
                    stdio_client(server_params)
                )
                stdio_read, stdio_write = stdio_transport
                
                # Create session through exit stack
                self.mcp_session = await self.exit_stack.enter_async_context(
                    ClientSession(stdio_read, stdio_write)
                )
                
                # Initialize the session with timeout
                init_result = await asyncio.wait_for(
                    self.mcp_session.initialize(),
                    timeout=15.0  # 15 second timeout
                )
                
                # Discover available tools
                await self.discover_tools()
            
            console.print(Panel.fit(
                f"[bold green]✓[/bold green] MCP Server Connected\n"
                f"[dim]Server: {init_result.serverInfo.name} v{init_result.serverInfo.version}[/dim]",
                border_style="green"
            ))
            
        except asyncio.TimeoutError as e:
            console.print(Panel(
                "[bold red]✗ MCP server startup timed out[/bold red]",
                border_style="red"
            ))
            raise
        except Exception as e:
            console.print(Panel(
                f"[bold red]✗ Error starting MCP server:[/bold red]\n{str(e)}",
                border_style="red"
            ))
            raise
    
    async def discover_tools(self) -> None:
        """Discover available tools from MCP server."""
        try:
            tools_result = await asyncio.wait_for(
                self.mcp_session.list_tools(),
                timeout=10.0
            )
            
            self.available_tools = {}
            for tool in tools_result.tools:
                # Convert MCP tool schema to Anthropic function schema
                function_schema = {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema  # Anthropic expects "input_schema", not "parameters"
                }
                self.available_tools[tool.name] = function_schema
            
            # Create tools table
            table = Table(title="🔧 Available Tools", border_style="cyan")
            table.add_column("Tool", style="cyan", no_wrap=True)
            table.add_column("Description", style="white")
            
            for tool_name, tool_data in self.available_tools.items():
                table.add_row(tool_name, tool_data["description"])
            
            console.print(table)
            
        except asyncio.TimeoutError as e:
            console.print("[bold red]✗ Tool discovery timed out[/bold red]")
            raise
        except Exception as e:
            console.print(f"[bold red]✗ Error discovering tools:[/bold red] {e}")
            raise
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call an MCP tool and return the response text."""
        try:
            result = await asyncio.wait_for(
                self.mcp_session.call_tool(tool_name, arguments),
                timeout=30.0  # 30 second timeout for tool calls
            )
            
            # Extract text from MCP response format
            if result.content and len(result.content) > 0:
                first_content = result.content[0]
                if hasattr(first_content, 'text'):
                    return first_content.text
                elif isinstance(first_content, dict) and 'text' in first_content:
                    return first_content['text']
            
            return "Tool executed successfully but returned no content."
            
        except asyncio.TimeoutError as e:
            return f"Error: Tool {tool_name} timed out"
        except Exception as e:
            return f"Error calling tool {tool_name}: {str(e)}"
    
    async def process_request(self, system_prompt: str, user_prompt: str) -> str:
        """Process user request using Anthropic AI with MCP tools."""
        try:
            # Prepare function definitions for Anthropic
            functions = list(self.available_tools.values())
            
            # Create initial conversation with user message
            messages = [
                {"role": "user", "content": user_prompt}
            ]
            
            logger.info("Starting conversation loop...")
            conversation_log = []
            
            # Main conversation loop (like MCP CLI)
            while True:
                # Initialize/reset for new model response
                current_text = ""
                tool_calls = []
                current_tool_use = None
                has_tool_call = False
                current_partial_json = ""
                
                console.print(Rule(f"[bold cyan]🤖 Claude AI", style="cyan"))
                
                # Make request to Anthropic with streaming (don't use asyncio.to_thread for streaming)
                response = await self.anthropic_client.messages.create(
                    model="claude-sonnet-4-20250514", 
                    max_tokens=5000,
                    system=system_prompt,
                    messages=messages,
                    tools=functions,
                    stream=True
                )
                
                # Process the stream chunks
                async for chunk in response:
                    if chunk.type == "content_block_delta" and chunk.delta.type == "text_delta":
                        current_text += chunk.delta.text
                        print(chunk.delta.text, end='', flush=True)
                    
                    elif chunk.type == "content_block_start" and chunk.content_block.type == "tool_use":
                        has_tool_call = True
                        current_tool_use = {
                            "id": chunk.content_block.id,
                            "name": chunk.content_block.name, 
                            "input": {}
                        }
                    
                    elif chunk.type == "content_block_delta" and chunk.delta.type == "input_json_delta":
                        if chunk.delta.partial_json and current_tool_use:
                            # Accumulate JSON input for tool
                            current_partial_json += chunk.delta.partial_json
                            try:
                                # Try to parse accumulated JSON
                                parsed_json = json.loads(current_partial_json)
                                current_tool_use["input"] = parsed_json
                            except json.JSONDecodeError:
                                pass  # Continue accumulating
                    
                    elif chunk.type == "content_block_stop" and current_tool_use:
                        # Complete tool call
                        tool_calls.append(current_tool_use)
                        current_tool_use = None
                        current_partial_json = ""  # Reset for next tool
                
                # Add newline after Claude's response if there was text
                if current_text:
                    print()
                
                # Create assistant message with text and tool calls
                assistant_content = []
                if current_text.strip():
                    assistant_content.append({"type": "text", "text": current_text.strip()})
                
                for tool_call in tool_calls:
                    assistant_content.append({
                        "type": "tool_use",
                        "id": tool_call["id"],
                        "name": tool_call["name"],
                        "input": tool_call["input"]
                    })
                
                # Add assistant message if we have content
                if assistant_content:
                    assistant_message = {"role": "assistant", "content": assistant_content}
                    messages.append(assistant_message)
                    conversation_log.append(assistant_message)
                
                # Process tool calls if any
                if has_tool_call:
                    tool_results = []
                    
                    for tool_call in tool_calls:
                        # Display tool call in a nice panel
                        args_json = json.dumps(tool_call['input'], indent=2)
                        console.print(Panel(
                            f"[bold yellow]🔧 {tool_call['name']}[/bold yellow]\n"
                            f"[dim]{args_json}[/dim]",
                            title="Tool Call",
                            border_style="yellow"
                        ))
                        
                        try:
                            tool_result = await self.call_mcp_tool(tool_call["name"], tool_call["input"])
                            
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_call["id"],
                                "content": tool_result
                            })
                            
                            # Display result in a panel
                            if "Successfully created" in tool_result:
                                border_style = "green"
                                title = "✓ Success"
                            elif "Error" in tool_result or "Validation error" in tool_result:
                                border_style = "red"
                                title = "✗ Error"
                            else:
                                border_style = "blue"
                                title = "📋 Result"
                            
                            # Try to format JSON if it's JSON content
                            display_result = tool_result
                            if tool_result.strip().startswith('{'):
                                try:
                                    parsed = json.loads(tool_result.split(':', 1)[1].strip() if ':' in tool_result else tool_result)
                                    display_result = json.dumps(parsed, indent=2)
                                except:
                                    pass  # Keep original if not valid JSON
                            
                            console.print(Panel(
                                display_result,
                                title=title,
                                border_style=border_style,
                                expand=False
                            ))
                            
                        except Exception as e:
                            console.print(Panel(
                                f"[bold red]Error: {str(e)}[/bold red]",
                                title="✗ Tool Error",
                                border_style="red"
                            ))
                            tool_results.append({
                                "type": "tool_result", 
                                "tool_use_id": tool_call["id"],
                                "content": f"Error: {str(e)}",
                                "is_error": True
                            })
                    
                    # Add tool results message
                    if tool_results:
                        tool_result_message = {"role": "user", "content": tool_results}
                        messages.append(tool_result_message)
                        conversation_log.append(tool_result_message)
                    
                    # Continue loop for another model turn since we had tool calls
                    continue
                else:
                    # No tool calls, conversation is complete
                    console.print("")
                    console.print(Rule("[bold green]✓ Conversation Complete", style="green"))
                    break
            
            # Extract final result text from conversation
            final_result = ""
            for message in conversation_log:
                if message.get("role") == "assistant":
                    for content in message.get("content", []):
                        if isinstance(content, dict) and content.get("type") == "text":
                            final_result += content.get("text", "") + "\n"
            
            return final_result.strip() if final_result else "Conversation completed successfully."
            
        except Exception as e:
            console.print(Panel(
                f"[bold red]Error in conversation:[/bold red]\n{str(e)}",
                border_style="red"
            ))
            return f"Error processing request: {str(e)}"
    
    async def close(self) -> None:
        """Clean up resources."""
        try:
            with console.status("[dim]Cleaning up...", spinner="dots"):
                await self.exit_stack.aclose()
        except Exception as e:
            console.print(f"[dim red]Error during cleanup: {e}[/dim red]")


async def main():
    """Main entry point for the reservation agent."""
    parser = argparse.ArgumentParser(description="Reservation Agent with MCP Tools")
    parser.add_argument("--system-prompt", required=True, help="Path to system prompt file")
    parser.add_argument("--user-prompt", required=True, help="Path to user prompt file")
    parser.add_argument("--data-dir", default="./data", help="Directory for reservation data")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print header
    console.print(Panel.fit(
        "[bold blue]🏨 Reservation Agent[/bold blue]\n"
        "[dim]Powered by Claude AI + MCP Tools[/dim]",
        border_style="blue"
    ))
    
    # Load environment variables
    load_dotenv()
    
    # Get Anthropic API key
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        console.print(Panel(
            "[bold red]✗ ANTHROPIC_API_KEY not found in environment variables[/bold red]\n"
            "[dim]Please add your API key to the .env file[/dim]",
            border_style="red"
        ))
        sys.exit(1)
    
    # Read prompt files
    try:
        system_prompt = Path(args.system_prompt).read_text(encoding='utf-8')
        user_prompt = Path(args.user_prompt).read_text(encoding='utf-8')
        
        # Display user request
        console.print(Panel(
            user_prompt,
            title="📝 User Request",
            border_style="magenta"
        ))
        
    except Exception as e:
        console.print(Panel(
            f"[bold red]✗ Error reading prompt files:[/bold red]\n{str(e)}",
            border_style="red"
        ))
        sys.exit(1)
    
    # Create and run agent
    agent = ReservationAgent(anthropic_api_key, args.data_dir)
    
    try:
        # Start MCP server and process request
        await agent.start_mcp_server()
        
        result = await agent.process_request(system_prompt, user_prompt)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Operation cancelled by user[/yellow]")
    except Exception as e:
        console.print(Panel(
            f"[bold red]Unexpected error:[/bold red]\n{str(e)}",
            border_style="red"
        ))
        if args.debug:
            console.print_exception()
        sys.exit(1)
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main()) 