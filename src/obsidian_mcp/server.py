from . import tools
import logging
from collections.abc import Sequence
from typing import Any
import os
from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import asyncio


load_dotenv()


# Load environment variables

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("obsidian_mcp")

api_key = os.getenv("OBSIDIAN_API_KEY")
if not api_key:
    raise ValueError(f"OBSIDIAN_API_KEY environment variable required. Working directory: {os.getcwd()}")

app = Server("obsidian_mcp")

tool_handlers = {}
def add_tool_handler(tool_class: tools.ToolHandler):
    global tool_handlers

    tool_handlers[tool_class.name] = tool_class

def get_tool_handler(name: str) -> tools.ToolHandler | None:
    if name not in tool_handlers:
        return None
    
    return tool_handlers[name]

add_tool_handler(tools.ListFilesInDirToolHandler())
add_tool_handler(tools.ListFilesInVaultToolHandler())
add_tool_handler(tools.GetFileContentsToolHandler())
add_tool_handler(tools.SearchToolHandler())
add_tool_handler(tools.PatchContentToolHandler())
add_tool_handler(tools.AppendContentToolHandler())
add_tool_handler(tools.DeleteFileToolHandler())
add_tool_handler(tools.ComplexSearchToolHandler())
add_tool_handler(tools.BatchGetFileContentsToolHandler())
add_tool_handler(tools.PeriodicNotesToolHandler())
add_tool_handler(tools.RecentPeriodicNotesToolHandler())
add_tool_handler(tools.RecentChangesToolHandler())

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""

    return [th.get_tool_description() for th in tool_handlers.values()]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for command line run."""
    
    if not isinstance(arguments, dict):
        raise RuntimeError("arguments must be dictionary")


    tool_handler = get_tool_handler(name)
    if not tool_handler:
        raise ValueError(f"Unknown tool: {name}")

    try:
        return tool_handler.run_tool(arguments)
    except Exception as e:
        logger.error(str(e))
        raise RuntimeError(f"Caught Exception. Error: {str(e)}")


async def main():

    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server
    stop_event = asyncio.Event()
    async with stdio_server() as (read_stream, write_stream):
        # Run the MCP server loop in the background
        server_task = asyncio.create_task(
            app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
        )
        
        # Keep the main function alive indefinitely until stop_event is set (e.g., by KeyboardInterrupt)
        # Or handle server_task completion/errors if needed
        try:
            await stop_event.wait() # Wait until stop_event is set
        except asyncio.CancelledError:
             logger.debug("Main wait loop cancelled.")
        except KeyboardInterrupt: # Catch Ctrl+C here
             logger.debug("KeyboardInterrupt caught in main loop, setting stop event.")
             stop_event.set() # Signal the finally block to clean up
        finally:
            logger.debug("Cleaning up server task...")
            if not server_task.done():
                server_task.cancel()
                try:
                    await server_task
                except asyncio.CancelledError:
                    logger.debug("Server task successfully cancelled.")
                except Exception as e:
                     logger.error(f"Error during server task cancellation: {e}")
            elif server_task.exception():
                logger.error(f"Server task finished with exception: {server_task.exception()}")
            else:
                 logger.debug("Server task already completed.")

# Make sure logger is defined or imported if used here
if __name__ == "__main__":
    logger.debug("Entering main execution block (__name__ == '__main__').")
    try:
        asyncio.run(main()) # Runs the main() defined in server.py
    except Exception as e: # Removed KeyboardInterrupt handler here
        logger.exception(f"Script encountered an unexpected error: {e}")
        exit(1)
    logger.debug("Script finished.")