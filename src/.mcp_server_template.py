# mcp_server_template.py

import requests
from typing import Any, Optional, List
from pathlib import Path
from pydantic import AnyUrl
from fastmcp.resources import Resource, TextResource
from fastmcp.tools import Tool
import logging

logger = logging.getLogger(__name__)

class MCPAPIClient:
    """
    A template for creating an MCP server that interacts with an HTTP API.
    """
    def __init__(
            self,
            api_key: str,
            protocol: str = 'https',
            host: str = "127.0.0.1",
            port: int = 8000,
            verify_ssl: bool = True,
            # Add any other custom config parameters here
            # e.g., data_path: Optional[Path | str] = None
        ):
        """
        Initializes the API client.

        Args:
            api_key (str): The API key for authentication.
            protocol (str): The protocol to use (http or https).
            host (str): The API host.
            port (int): The API port.
            verify_ssl (bool): Whether to verify SSL certificates.
        """
        self.api_key = api_key
        self.protocol = protocol
        self.host = host
        self.port = port
        self.verify_ssl = verify_ssl
        self.timeout = (3, 6)  # (connect_timeout, read_timeout)
        self.base_url = f'{self.protocol}://{self.host}:{self.port}'

        self.resources: List[Resource] = []
        self.tools: List[Tool] = []

        # Initialize resources and tools
        self._initialize_resources()
        self._initialize_tools()

    def _get_headers(self) -> dict:
        """
        Constructs the default headers for API requests.
        This is where you should add authentication headers.
        """
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def _make_request(self, method: str, path: str, **kwargs) -> requests.Response:
        """
        Generic method to make an HTTP request to the target API.
        """
        url = f"{self.base_url}{path}"
        headers = self._get_headers()
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))

        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                verify=self.verify_ssl,
                timeout=self.timeout,
                **kwargs  # Pass remaining kwargs (e.g., params, data, json)
            )
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            return response
        except requests.HTTPError as e:
            # You can customize error handling here
            logger.error(f"HTTP Error: {e.response.status_code} for URL: {e.response.url}")
            logger.error(f"Response: {e.response.text}")
            raise Exception(f"API request failed with status {e.response.status_code}") from e
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"Request failed: {str(e)}") from e

    def _initialize_resources(self):
        """
        Initialize and register all MCP resources.
        Add your resources to self.resources here.
        """
        resource_list = []

        # --- Example Resource ---
        # This is a simple text resource. You can create your own resource types
        # by inheriting from fastmcp.resources.Resource.
        # See fastmcp documentation for more resource types like FileResource, DirectoryResource etc.
        example_resource = TextResource(
            uri=AnyUrl("my-server://info"),
            text="This is an example resource from the MCP server.",
            name="get_server_info",
            description="Returns static information about the server."
        )
        resource_list.append(example_resource)

        self.resources.extend(resource_list)
        logger.info(f"Initialized {len(resource_list)} resources.")

    def _initialize_tools(self):
        """
        Initialize and register all MCP tools.
        Wrap your client's methods with Tool.from_function to expose them.
        """
        tool_list = []

        # --- Example Tools ---
        # Each tool should correspond to a method in this class.
        tool_list.append(
            Tool.from_function(
                self.get_api_status,
                name="get_api_status",
                description="Checks the status of the downstream API by calling its health check endpoint."
            )
        )

        tool_list.append(
            Tool.from_function(
                self.fetch_data,
                name="fetch_data",
                description="Fetches a specific data item from the API by its ID."
            )
        )

        self.tools.extend(tool_list)
        logger.info(f"Initialized {len(tool_list)} tools.")

    def get_resources_list(self) -> List[Resource]:
        """Get all registered resources."""
        return self.resources

    def get_tools_list(self) -> List[Tool]:
        """Get all registered tools."""
        return self.tools

    # --------------------------------------------------------------------------
    # API-specific Methods (to be exposed as Tools)
    # --------------------------------------------------------------------------
    # These methods implement the logic for your tools by interacting with the
    # downstream API.

    def get_api_status(self) -> dict:
        """
        Example tool method: Calls a '/status' endpoint on the API.
        """
        try:
            response = self._make_request("GET", "/status")
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def fetch_data(self, item_id: str) -> dict:
        """
        Example tool method: Fetches data from a '/items/{item_id}' endpoint.

        Args:
            item_id: The ID of the item to fetch.

        Returns:
            A dictionary containing the item data.
        """
        try:
            response = self._make_request("GET", f"/items/{item_id}")
            return response.json()
        except Exception as e:
            return {"status": "error", "message": f"Failed to fetch item {item_id}: {e}"}

# This allows the class to be imported directly.
__all__ = ["MCPAPIClient"]