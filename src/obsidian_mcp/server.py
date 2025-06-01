import logging
import os
from dotenv import load_dotenv
from mcp.server import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("obsidian_mcp")

# Load environment variables
if not load_dotenv():
    raise ValueError(".env file not found. Please ensure it exists in the current directory.")

api_key = os.getenv("OBSIDIAN_API_KEY")
if not api_key:
    raise ValueError("OBSIDIAN_API_KEY environment not set (fatal)")

# Initialize the FastMCP server
app = FastMCP("obsidian_mcp")

# Import tools after app definition to avoid errors
from . import tools
logger.debug("Tools imported successfully")

if __name__ == "__main__":
    try:
        app.run()
    except Exception as e:
        logger.exception(f"Script encountered an unexpected error: {e}")
        exit(1)