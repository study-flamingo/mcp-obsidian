# MCP server for Obsidian

An MCP server to interact with Obsidian via the Local REST API community plugin.

## Components

This server provides the following components:

#### Tools

The server implements multiple tools to interact with Obsidian:

- `list_files_in_vault`: Lists all files and directories in the root directory of your Obsidian vault.
- `list_files_in_dir`: Lists all files and directories that exist in a specific Obsidian directory.
- `get_file_contents`: Return the content of a single file in your vault.
- `simple_search`: Simple search for documents matching a specified text query across all files in the vault. Use this tool when you want to do a simple text search
- `append_content`: Append content to a new or existing file in the vault.
- `patch_content`: Insert content into an existing note relative to a heading, block reference, or frontmatter field.
- `delete_file`: Delete a file or directory from the vault.
- `complex_search`: Complex search for documents using a JsonLogic query. Supports standard JsonLogic operators plus 'glob' and 'regexp' for pattern matching. Results must be non-falsy. Use this tool when you want to do a complex search, e.g. for all documents with certain tags etc.
- `batch_get_file_contents`: Return the contents of multiple files in your vault, concatenated with headers.
- `get_periodic_note`: Get current periodic note for the specified period.
- `get_recent_periodic_notes`: Get most recent periodic notes for the specified period type.
- `get_recent_changes`: Get recently modified files in the vault.

#### Resources

(No specific resources are defined in tools.py)

#### Prompts

(No specific prompts are defined in tools.py, keeping example prompts from original README)

Its good to first instruct Claude to use Obsidian. Then it will always call the tool.

The use prompts like this:
- Get the contents of the last architecture call note and summarize them
- Search for all files where Azure CosmosDb is mentioned and quickly explain to me the context in which it is mentioned
- Summarize the last meeting notes and put them into a new note 'summary meeting.md'. Add an introduction so that I can send it via email.

### Running the server

To run the server, use `uv run obsidian-mcp` or `uvx obsidian-mcp`.

### Example prompts

- Get the contents of the last architecture call note and summarize them
- Search for all files where Azure CosmosDb is mentioned and quickly explain to me the context in which it is mentioned
- Summarize the last meeting notes and put them into a new note 'summary meeting.md'. Add an introduction so that I can send it via email.

## Quickstart

### Install

#### Obsidian REST API

You need the Obsidian REST API community plugin running: https://github.com/coddingtonbear/obsidian-local-rest-api

Install and enable it in the settings and copy the api key.

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  
To use the local installation with Claude Desktop, configure the server as follows. For cloning and installation steps, please refer to the [Local Installation](#local-installation) section.

```json
{
  "mcpServers": {
    "obsidian-mcp": {
      "command": "uv",
      "args": [
        "run",
        "obsidian-mcp"
      ]
    }
  }
}
```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  
```json
{
  "mcpServers": {
    "obsidian-mcp": {
      "command": "uvx",
      "args": [
        "obsidian-mcp"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key_here>",
        "OBSIDIAN_HOST": "<your_obsidian_host>" # Optional
      }
    }
  }
}
```
</details>

#### Local Installation

After cloning the repository and installing dependencies, you can run the server locally from the project directory using `uv run src/obsidian_mcp/__main__.py`. Alternatively, you can install the project in editable mode using `uv pip install -e .` from the project root, which will allow you to use `uv run obsidian-mcp`.

To get started, first clone the repository and install the dependencies:

1. Clone the repository:
```bash
git clone https://github.com/study-flamingo/obsidian-mcp.git
cd obsidian-mcp
```

2. Install dependencies using uv:
```bash
uv sync
```

## Configuration

### Obsidian REST API Key

There are two ways to configure the environment with the Obsidian REST API Key. 

1. Add to server config (preferred)

```json
{
  "obsidian-mcp": {
    "command": "uvx",
    "args": [
      "obsidian-mcp"
    ],
    "env": {
      "OBSIDIAN_API_KEY": "<your_api_key_here>",
      "OBSIDIAN_HOST": "<your_obsidian_host>" # Optional, defaults to 127.0.0.1
    }
  }
}
```

2. Create a `.env` file in the working directory with the following required variable:

```
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_HOST=your_obsidian_host # Optional, defaults to 127.0.0.1
```

Note: You can find the key in the Obsidian plugin config.

## Development

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector). You can also use `mcp dev` to launch the inspector.

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/obsidian-mcp run obsidian-mcp
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

You can also watch the server logs with this command:

```bash
tail -n 20 -f ~/Library/Logs/Claude/mcp-server-obsidian-mcp.log
```
