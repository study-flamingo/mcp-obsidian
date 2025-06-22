from collections.abc import Sequence
from mcp.types import (
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from typing import Annotated, Literal
from pydantic import Field
import json
import os
from . import obsidian
from .server import mcp

api_key = os.getenv("OBSIDIAN_API_KEY", "")
obsidian_host = os.getenv("OBSIDIAN_HOST", "127.0.0.1")


@mcp.tool(
    description="Lists all files and directories in the root directory of your Obsidian vault."
)
async def list_files_in_vault() -> list[str]:
    """Lists all files and directories in the root directory of your Obsidian vault."""
    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    files = api.list_files_in_vault()
    return files

@mcp.tool(
    description="Lists all files and directories that exist in a specific Obsidian directory."
)
async def list_files_in_dir(
    dirpath: Annotated[str, Field(description="Path to list files from (relative to your vault root). Note that empty directories will not be returned.")]
) -> list[str]:
    """Lists all files and directories that exist in a specific Obsidian directory."""
    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    files = api.list_files_in_dir(dirpath)
    return files

@mcp.tool(
    description="Return the content of a single file in your vault."
)
async def get_file_contents(
    filepath: Annotated[str, Field(description="Path to the relevant file (relative to your vault root).", format="path")]
) -> str:
    """Return the content of a single file in your vault."""
    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    content = api.get_file_contents(filepath)
    return content

@mcp.tool(
    description="""Simple search for documents matching a specified text query across all files in the vault.
            Use this tool when you want to do a simple text search"""
)
async def simple_search(
    query: Annotated[str, Field(description="Text to a simple search for in the vault.")],
    context_length: Annotated[int, Field(description="How much context to return around the matching string (default: 100)", default=100)] = 100
) -> list[dict]:
    """Simple search for documents matching a specified text query across all files in the vault."""
    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    results = api.search(query, context_length)

    formatted_results = []
    for result in results:
        formatted_matches = []
        for match in result.get('matches', []):
            context = match.get('context', '')
            match_pos = match.get('match', {})
            start = match_pos.get('start', 0)
            end = match_pos.get('end', 0)

            formatted_matches.append({
                'context': context,
                'match_position': {'start': start, 'end': end}
            })

        formatted_results.append({
            'filename': result.get('filename', ''),
            'score': result.get('score', 0),
            'matches': formatted_matches
        })

    return formatted_results

@mcp.tool(
    description="Append content to a new or existing file in the vault."
)
async def append_content(
    filepath: Annotated[str, Field(description="Path to the file (relative to vault root)", format="path")],
    content: Annotated[str, Field(description="Content to append to the file")]
) -> str:
    """Append content to a new or existing file in the vault."""
    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    api.append_content(filepath, content)
    return f"Successfully appended content to {filepath}"

@mcp.tool(
    description="Insert content into an existing note relative to a heading, block reference, or frontmatter field."
)
async def patch_content(
    filepath: Annotated[str, Field(description="Path to the file (relative to vault root)", format="path")],
    operation: Annotated[Literal["append", "prepend", "replace"], Field(description="Operation to perform (append, prepend, or replace)")],
    target_type: Annotated[Literal["heading", "block", "frontmatter"], Field(description="Type of target to patch")],
    target: Annotated[str, Field(description="Target identifier (heading path, block reference, or frontmatter field)")],
    content: Annotated[str, Field(description="Content to insert")]
) -> str:
    """Insert content into an existing note relative to a heading, block reference, or frontmatter field."""
    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    api.patch_content(filepath, operation, target_type, target, content)
    return f"Successfully patched content in {filepath}"

@mcp.tool(
    description="Delete a file or directory from the vault."
)
async def delete_file(
    filepath: Annotated[str, Field(description="Path to the file or directory to delete (relative to vault root)", format="path")],
    confirm: Annotated[bool, Field(description="Confirmation to delete the file (must be true)", default=False)] = False
) -> str:
    """Delete a file or directory from the vault."""
    if not confirm:
        raise RuntimeError("confirm must be set to true to delete a file")

    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    api.delete_file(filepath)
    return f"Successfully deleted {filepath}"

@mcp.tool(
    description="""Complex search for documents using a JsonLogic query.
            Supports standard JsonLogic operators plus 'glob' and 'regexp' for pattern matching. Results must be non-falsy.

            Use this tool when you want to do a complex search, e.g. for all documents with certain tags etc.
            """
)
async def complex_search(
    query: Annotated[dict, Field(description="JsonLogic query object. Example: {\"glob\": [\"*.md\", {\"var\": \"path\"}]} matches all markdown files")]
) -> list[dict]:
    """Complex search for documents using a JsonLogic query."""
    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    results = api.search_json(query)
    return results

@mcp.tool(
    description="Return the contents of multiple files in your vault, concatenated with headers."
)
async def batch_get_file_contents(
    filepaths: Annotated[list[str], Field(description="List of file paths to read", items={"type": "string", "description": "Path to a file (relative to your vault root)", "format": "path"})]
) -> str:
    """Return the contents of multiple files in your vault, concatenated with headers."""
    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    content = api.get_batch_file_contents(filepaths)
    return content

@mcp.tool(
    description="Get current periodic note for the specified period."
)
async def get_periodic_note(
    period: Annotated[Literal["daily", "weekly", "monthly", "quarterly", "yearly"], Field(description="The period type (daily, weekly, monthly, quarterly, yearly)")]
) -> str:
    """Get current periodic note for the specified period."""
    valid_periods = ["daily", "weekly", "monthly", "quarterly", "yearly"]
    if period not in valid_periods:
        raise RuntimeError(f"Invalid period: {period}. Must be one of: {', '.join(valid_periods)}")

    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    content = api.get_periodic_note(period)
    return content

@mcp.tool(
    description="Get most recent periodic notes for the specified period type."
)
async def get_recent_periodic_notes(
    period: Annotated[Literal["daily", "weekly", "monthly", "quarterly", "yearly"], Field(description="The period type (daily, weekly, monthly, quarterly, yearly)")],
    limit: Annotated[int, Field(description="Maximum number of notes to return (default: 5)", default=5, minimum=1, maximum=50)] = 5,
    include_content: Annotated[bool, Field(description="Whether to include note content (default: false)", default=False)] = False
) -> list[dict]:
    """Get most recent periodic notes for the specified period type."""
    valid_periods = ["daily", "weekly", "monthly", "quarterly", "yearly"]
    if period not in valid_periods:
        raise RuntimeError(f"Invalid period: {period}. Must be one of: {', '.join(valid_periods)}")

    if not isinstance(limit, int) or limit < 1:
        raise RuntimeError(f"Invalid limit: {limit}. Must be a positive integer")

    if not isinstance(include_content, bool):
        raise RuntimeError(f"Invalid include_content: {include_content}. Must be a boolean")

    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    results = api.get_recent_periodic_notes(period, limit, include_content)
    return results

@mcp.tool(
    description="Get recently modified files in the vault."
)
async def get_recent_changes(
    limit: Annotated[int, Field(description="Maximum number of files to return (default: 10)", default=10, minimum=1, maximum=100)] = 10,
    days: Annotated[int, Field(description="Only include files modified within this many days (default: 90)", minimum=1, default=90)] = 90
) -> list[dict]:
    """Get recently modified files in the vault."""
    if not isinstance(limit, int) or limit < 1:
        raise RuntimeError(f"Invalid limit: {limit}. Must be a positive integer")

    if not isinstance(days, int) or days < 1:
        raise RuntimeError(f"Invalid days: {days}. Must be a positive integer")

    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    results = api.get_recent_changes(limit, days)
    return results
