import logging
import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from .obsidian import Obsidian
from fastmcp.resources import Resource

# Configure logging
logger = logging.getLogger("obsidian_mcp")
logging.basicConfig(level=logging.INFO)

# Load environment variables
try:
    # Construct the path to the .env file in the user dir
    home_dotenv_path = os.path.join(os.path.expanduser("~"), ".obsidian-mcp", ".env")

    # Load environment variables from multiple locations
    loaded_any = load_dotenv("../../.env") or load_dotenv(".env") or load_dotenv(home_dotenv_path)

    if not loaded_any:
        logger.info(".env file not found! Place in project root or in ~/.obsidian-mcp or pass from host")
    else:
        logger.debug(".env file found!")

    api_key = os.getenv("OBSIDIAN_API_KEY")
    if not api_key:
        raise ValueError("OBSIDIAN_API_KEY not found! Set in your environment or in a .env file.")
    logger.debug("Obsidian API key loaded successfully")
    
    local_vault_path = os.getenv("OBSIDIAN_LOCAL_PATH")

    ob = Obsidian(
        api_key=api_key,
        local_vault_path=local_vault_path,
    )

except ValueError as e:
    logger.error(f"Configuration error: {e}")
    exit(1)


# Initialize the FastMCP server
mcp = FastMCP("obsidian_mcp")


# Register resources
try:
    for r in ob.get_resources_list():
        mcp.add_resource(r)
        logger.info(f"Registered resource: {r.name}")
    
except Exception as e:
    logger.error(f"Failed to register resources: {e}")
    exit(1)


# Register tools
try:
    for t in ob.get_tools_list():
        mcp.add_tool(t)
        logger.info(f"Registered tool: {t.name}")
    
except Exception as e:
    logger.error(f"Failed to register tools: {e}")
    exit(1)


logger.info("Obsidian MCP server initialized successfully")

if __name__ == "__main__":
    try:
        mcp.run()
    except Exception as e:
        logger.exception(f"Script encountered an unexpected error: {e}")
        exit(1)
