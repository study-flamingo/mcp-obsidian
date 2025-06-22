import requests
import urllib.parse
from typing import Any, Optional, List
from datetime import datetime
import pathlib
from pathlib import Path
from pydantic import AnyUrl
from fastmcp.resources import Resource, FileResource, TextResource, DirectoryResource
from fastmcp.tools import Tool, FunctionTool
import logging

logger = logging.getLogger("obsidian_mcp")

local_vault_path = Path("C:\\Users\\joelc\\Obsidian\\Home")
class Obsidian():
    def __init__(
            self, 
            api_key: str,
            protocol: str = 'https',
            host: str = "127.0.0.1",
            port: int = 27124,
            verify_ssl: bool = False,
            local_vault_path: Optional[Path | str] = None
        ):
        self.api_key = api_key
        self.protocol = protocol
        self.host = host
        self.port = port
        self.verify_ssl = verify_ssl
        self.timeout = (3, 6)
        self.base_url = f'{self.protocol}://{self.host}:{self.port}'
        self.resources: List[Resource] = []
        self.tools: List[Tool] = []
        
        self._initialize_tools()  # Initialize tools after resources
        
        # Initialize Resources if local_vault_path is set
        if not local_vault_path:
            print("No local vault path provided, using default")
            local_vault_path = Path("C:\\Users\\joelc\\Obsidian\\Home")
        if not Path(local_vault_path).is_dir():
            raise FileNotFoundError(f"Local Obsidian vault not found at {local_vault_path}")
        else:
            print(f"Using local vault path: {local_vault_path}")
            self.local_vault_path = Path(local_vault_path).resolve()
            self._initialize_resources()
            

    def _get_headers(self) -> dict:
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        return headers

    def _make_request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Generic method to make an HTTP request to the Obsidian API."""
        url = f"{self.get_base_url()}{path}"
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
                **kwargs # Pass remaining keyword arguments (params, data, json, etc.)
            )
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            error_data = e.response.json() if e.response.content else {}
            code = error_data.get('errorCode', -1)
            message = error_data.get('message', '<unknown>')
            raise Exception(f"Error {code}: {message}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def _initialize_resources(self):
        """Initialize and register all resources."""
        resource_list = []
        
        resource_list.append(
            DirectoryResource(
                uri=AnyUrl("obsidianmcp://vault"),
                path=local_vault_path,
                name="list_root_files",
                description="List all files in the vault root dir.",
                recursive=False
            )
        )
        resource_list.append(
            DirectoryResource(
                uri=AnyUrl("obsidianmcp://vault"),
                path=local_vault_path,
                name="list_all_files",
                description="List all files in the entire vault.",
                recursive=True
            )
        )
        resource_list.append(
            DirectoryResource(
                uri=AnyUrl("obsidianmcp://vault/{dir_path}"),
                path=pathlib.Path(self.local_vault_path, "{dir_path}"),
                name="list_files_in_subdir",
                description="""
                    List the files in a specific subdirectory of the vault.
                    
                    **Params**:
                        dir_path (str): The path to the subdirectory, relative to the vault root.
                    
                    *Example: `notes/daily` resolves to `obsidianmcp://vault/notes/daily`, returning
                    the files in the `notes/daily` subdirectory of the vault.*
                """,
                recursive=False
            )
        )
        resource_list.append(
            DirectoryResource(
                uri=AnyUrl("obsidianmcp://vault/{dir_path}/r"),
                path=pathlib.Path(self.local_vault_path, "{dir_path}"),
                name="list_files_in_subdir_recursive",
                description="""Recursively list the files of a specific subdirectory of the vault.
                    
                    **Params**:
                        dir_path (str): The path to the subdirectory, relative to the vault root.
                    
                    *Example: `notes/daily` resolves to `obsidianmcp://vault/notes/daily`, returning
                    the files in the `notes/daily` subdirectory of the vault, including all nested
                    files.*
                """,
                recursive=True
            )
        )
        resource_list.append(
            FileResource(
                uri=AnyUrl("obsidianmcp://vault/{file_path}"),
                path=pathlib.Path(self.local_vault_path, "{file_path}"),
                name="read_file",
                description="Read the contents of a specific file in the vault.",
                mime_type="text/markdown"
            )
        )
        
        self.resources.extend(resource_list)

    def _initialize_tools(self): # New method for tools
        """Initialize and register all tools."""
        tool_list = []

        # Example: Registering list_files_in_vault as a tool
        tool_list.append(
            Tool.from_function(
                self.list_files_in_vault,
                name="list_files_in_vault",
                description="List files in the root directory of your vault."
            )
        )

        # Example: Registering list_files_in_dir as a tool
        tool_list.append(
            Tool.from_function(
                self.list_files_in_dir,
                name="list_files_in_dir",
                description="List files that exist in the specified directory."
            )
        )

        # Example: Registering get_file_contents as a tool
        tool_list.append(
            Tool.from_function(
                self.get_file_contents,
                name="get_file_contents",
                description="""
                Get the contents of a file and the current date.

                Args:
                    filepath: Path to the file in the vault.

                Returns:
                    dict: {
                        "now": <current date as string>,
                        "content": <file contents as string>
                    }
                """
            )
        )

        # Add other methods you want to expose as tools here
        tool_list.append(
            Tool.from_function(
                self.get_batch_file_contents,
                name="get_batch_file_contents",
                description="""
                Get contents of multiple files and concatenate them with headers.

                Args:
                    filepaths: List of file paths to read

                Returns:
                    String containing all file contents with headers
                """
            )
        )

        tool_list.append(
            Tool.from_function(
                self.search,
                name="search_vault", # Renamed for clarity as a tool
                description="Search for documents matching a specified text query."
            )
        )

        tool_list.append(
            Tool.from_function(
                self.append_content,
                name="append_content",
                description="Append content to a new or existing file."
            )
        )

        tool_list.append(
            Tool.from_function(
                self.patch_content,
                name="patch_content",
                description="Partially update content in an existing note."
            )
        )

        tool_list.append(
            Tool.from_function(
                self.delete_file,
                name="delete_file",
                description="Delete a file or directory from the vault."
            )
        )

        tool_list.append(
            Tool.from_function(
                self.search_json,
                name="search_json",
                description="Search for documents matching a specified search query using JsonLogic."
            )
        )

        tool_list.append(
            Tool.from_function(
                self.get_periodic_note,
                name="get_periodic_note",
                description="Get current periodic note for the specified period."
            )
        )

        tool_list.append(
            Tool.from_function(
                self.get_recent_periodic_notes,
                name="get_recent_periodic_notes",
                description="Get most recent periodic notes for the specified period type."
            )
        )

        tool_list.append(
            Tool.from_function(
                self.get_recent_changes,
                name="get_recent_changes",
                description="Get recently modified files in the vault."
            )
        )

        self.tools.extend(tool_list)
        logger.info(f"Initialized {len(tool_list)} tools for Obsidian MCP")

    def get_resources_list(self) -> List[Resource]:
        """Get all resources as a list."""
        return self.resources
    
    def get_tools_list(self) -> List[Tool]:
        """Get all tools as a list."""
        return self.tools

    def get_base_url(self) -> str:
        return self.base_url

    # def register_tool(self, tool: Tool) -> None:
    #     """Register a tool to the Obsidian instance."""
    #     if tool not in self.tools:
    #         self.tools.append(tool)
    #         logger.info(f"Registered tool: {tool.name}")

    def list_files_in_vault(self) -> Any:
        """List files in the root directory of your vault."""
        response = self._make_request("GET", "/vault/")
        return response.json()['files']

    def list_files_in_dir(self, dirpath: str) -> Any:
        """List files that exist in the specified directory."""
        response = self._make_request("GET", f"/vault/{dirpath}/")
        return response.json()['files']

    def get_file_contents(self, filepath: str) -> dict:
        """
        Get the contents of a file and the current date.

        Args:
            filepath: Path to the file in the vault.

        Returns:
            dict: {
                "now": <current date as string>,
                "content": <file contents as string>
            }
        """
        response = self._make_request("GET", f"/vault/{filepath}")
        return {
            "now": datetime.now().date().isoformat(),
            "content": response.text
        }
    
    def get_batch_file_contents(self, filepaths: list[str]) -> str:
        """Get contents of multiple files and concatenate them with headers.
        
        Args:
            filepaths: List of file paths to read
            
        Returns:
            String containing all file contents with headers
        """
        result = []
        
        for filepath in filepaths:
            try:
                content = self.get_file_contents(filepath)
                result.append(f"# {filepath}\n\n{content}\n\n---\n\n")
            except Exception as e:
                # Add error message but continue processing other files
                result.append(f"# {filepath}\n\nError reading file: {str(e)}\n\n---\n\n")
                
        return "".join(result)

    def search(self, query: str, context_length: int = 100) -> Any:
        """Search for documents matching a specified text query."""
        params = {
            'query': query,
            'contextLength': context_length
        }
        response = self._make_request("POST", "/search/simple/", params=params)
        return response.json()

    def append_content(self, filepath: str, content: str) -> Any:
        """Append content to a new or existing file."""
        headers = {'Content-Type': 'text/markdown'}
        self._make_request("POST", f"/vault/{filepath}", headers=headers, data=content)
        return None

    def patch_content(self, filepath: str, operation: str, target_type: str, target: str, content: str) -> Any:
        """Partially update content in an existing note."""
        headers = {
            'Content-Type': 'text/markdown',
            'Operation': operation,
            'Target-Type': target_type,
            'Target': urllib.parse.quote(target)
        }
        self._make_request("PATCH", f"/vault/{filepath}", headers=headers, data=content)
        return None

    def delete_file(self, filepath: str) -> int:
        """Delete a file or directory from the vault.

        Args:
            filepath: Path to the file to delete (relative to vault root)

        Returns:
            HTTP status code (e.g., 200 for success)
        """
        response = self._make_request("DELETE", f"/vault/{filepath}")
        return response.status_code

    def search_json(self, query: dict) -> Any:
        """Search for documents matching a specified search query using JsonLogic."""
        headers = {'Content-Type': 'application/vnd.olrapi.jsonlogic+json'}
        response = self._make_request("POST", "/search/", headers=headers, json=query)
        return response.json()

    def get_periodic_note(self, period: str) -> Any:
        """Get current periodic note for the specified period.

        Args:
            period: The period type (daily, weekly, monthly, quarterly, yearly)

        Returns:
            Content of the periodic note
        """
        response = self._make_request("GET", f"/periodic/{period}/")
        return response.text

    def get_recent_periodic_notes(self, period: str, limit: int = 5, include_content: bool = False) -> Any:
        """Get most recent periodic notes for the specified period type.

        Args:
            period: The period type (daily, weekly, monthly, quarterly, yearly)
            limit: Maximum number of notes to return (default: 5)
            include_content: Whether to include note content (default: False)

        Returns:
            List of recent periodic notes
        """
        params = {
            "limit": limit,
            "includeContent": include_content
        }
        response = self._make_request("GET", f"/periodic/{period}/recent", params=params)
        return response.json()

    def get_recent_changes(self, limit: int = 10, days: int = 90) -> Any:
        """Get recently modified files in the vault.

        Args:
            limit: Maximum number of files to return (default: 10)
            days: Only include files modified within this many days (default: 90)

        Returns:
            List of recently modified files with metadata
        """
        # Build the DQL query
        query_lines = [
            "TABLE file.mtime",
            f"WHERE file.mtime >= date(today) - dur({days} days)",
            "SORT file.mtime DESC",
            f"LIMIT {limit}"
        ]

        # Join with proper DQL line breaks
        dql_query = "\n".join(query_lines)

        # Make the request to search endpoint
        headers = {'Content-Type': 'application/vnd.olrapi.dataview.dql+txt'}
        response = self._make_request("POST", "/search/", headers=headers, data=dql_query.encode('utf-8'))
        return response.json()

__all__ = [
    "Obsidian"
]