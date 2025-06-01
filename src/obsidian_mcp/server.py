import logging
import os
from dotenv import load_dotenv
from mcp.server import FastMCP
import sys

# Configure logging
logger = logging.getLogger("obsidian_mcp")
logging.basicConfig(level=logging.INFO)

# Load environment variables
try:
    # Construct the path to the .env file in the user's home directory
    home_dotenv_path = os.path.join(os.path.expanduser("~"), ".obsidian-mcp", ".env")

    # Load environment variables from multiple locations
    loaded_any = load_dotenv("../../.env") or load_dotenv(".env") or load_dotenv(home_dotenv_path)

    if not loaded_any:
        logger.info(".env file not found, env variable must be passed by host process.")
    else:
        logger.debug(".env file found!")

    api_key = os.getenv("OBSIDIAN_API_KEY")
    if not api_key:
        raise ValueError("OBSIDIAN_API_KEY environment not set")
    logger.debug("Obsidian API key loaded successfully")
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    exit(1)

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
