# MediaWiki MCP Server

A Model Context Protocol (MCP) server that allows LLMs like Claude to interact with MediaWiki installations through the MediaWiki API as a bot user.

## Features

The server provides various MCP tools with the `wiki_` prefix:

- **`wiki_page_edit`**: Edit or create MediaWiki pages with comprehensive editing options
- **`wiki_page_get`**: Retrieve page information and content
- **`wiki_search`**: Search for pages using MediaWiki's search API with advanced filtering

## Project Structure

The project is organized into modular components for maintainability:

```
mediawiki_api_mcp/
├── __init__.py
├── server.py             # Main MCP server implementation
├── client.py             # MediaWiki API client
├── tools/                # Tool definitions
│   ├── __init__.py
│   ├── wiki_page_edit.py # Edit page tools
│   ├── wiki_page_get.py  # Get page tools
│   └── wiki_search.py    # Search tools
└── handlers/             # Tool handlers
    ├── __init__.py
    ├── wiki_page_edit.py # Edit page handlers
    ├── wiki_page_get.py  # Get page handlers
    └── wiki_search.py    # Search handlers

tests/
├── __init__.py
├── test_server.py         # Integration tests
├── test_wiki_page_edit.py # Edit handler tests
├── test_wiki_page_get.py  # Get handler tests
├── test_wiki_search.py    # Search handler tests
└── test_tools.py          # Tool definition tests
```

## Installation

1. Clone the repository
2. Install dependencies using UV:

```bash
uv install
```

3. Set up environment variables:

```bash
export MEDIAWIKI_API_URL="https://your-wiki.com/api.php"
export MEDIAWIKI_API_BOT_USERNAME="your_bot_username"
export MEDIAWIKI_API_BOT_PASSWORD="your_bot_password"
export MEDIAWIKI_API_BOT_USER_AGENT="MediaWiki-MCP-Bot/1.0"  # Optional
```

## Usage

### Running the Server

```bash
uv run mediawiki-api-mcp
```

Or directly:

```bash
python -m mediawiki_api_mcp.server
```

### Configuration with Claude Desktop

Add to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "mediawiki-api": {
      "command": "uv",
      "args": ["run", "mediawiki-api-mcp"],
      "env": {
        "MEDIAWIKI_API_URL": "https://your-wiki.com/api.php",
        "MEDIAWIKI_API_BOT_USERNAME": "your_bot_username",
        "MEDIAWIKI_API_BOT_PASSWORD": "your_bot_password",
        "MEDIAWIKI_API_BOT_USER_AGENT": "MediaWiki-MCP-Bot/1.0"
      }
    }
  }
}
```

## Tools

### wiki_page_edit

Edit or create MediaWiki pages with comprehensive options:

- **Page identification**: `title` or `pageid`
- **Content options**: `text` (full replacement), `appendtext`, `prependtext`
- **Section editing**: `section`, `sectiontitle`
- **Metadata**: `summary`, `minor`, `bot`, `createonly`, `nocreate`

### wiki_page_get

Retrieve page information and content:

- **Input**: `title` or `pageid`
- **Output**: Page title, ID, and full wikitext content

### wiki_search

Advanced search functionality with MediaWiki's search API:

- **Query**: Search terms (required)
- **Filtering**: `namespaces`, `what` (text/title/nearmatch)
- **Pagination**: `limit`, `offset`
- **Results**: `prop` (snippet, size, timestamp, etc.)
- **Sorting**: Multiple sort options
- **Advanced**: Query rewriting, interwiki results

## Development

### Running Tests

```bash
uv run pytest
```

Run specific test modules:

```bash
uv run pytest tests/test_server.py
uv run pytest tests/test_tools.py
uv run pytest tests/test_wiki_page_edit.py
uv run pytest tests/test_wiki_search.py
```

### Code Quality

```bash
# Linting
uv run ruff check

# Type checking
uv run mypy mediawiki_api_mcp
```

### Adding New Tools

1. **Define the tool** in `mediawiki_api_mcp/tools/`
2. **Implement the handler** in `mediawiki_api_mcp/handlers/`
3. **Add to server** in `server.py` tool listing and routing
4. **Write tests** in `tests/`

Example tool structure:

```python
# tools/my_feature.py
def get_my_tools() -> List[types.Tool]:
    return [types.Tool(name="wiki_my_tool", ...)]

# handlers/my_feature.py
async def handle_my_tool(client: MediaWikiClient, arguments: Dict[str, Any]):
    # Implementation
    pass
```

## Architecture

### Client Layer (`client.py`)
- Handles MediaWiki API authentication and requests
- Manages CSRF tokens and session state
- Provides typed methods for API operations

### Tools Layer (`tools/`)
- Defines MCP tool schemas using JSON Schema
- Separated by functional area (edit, search)
- Ensures all tools have `wiki_` prefix

### Handlers Layer (`handlers/`)
- Implements actual tool logic
- Handles argument validation and error handling
- Returns properly formatted MCP responses

### Server Layer (`server.py`)
- Main MCP server orchestration
- Routes tool calls to appropriate handlers
- Manages configuration and client lifecycle

## Error Handling

The server implements comprehensive error handling:

- **Configuration errors**: Missing environment variables
- **Authentication errors**: Invalid credentials or permissions
- **API errors**: Network issues, invalid requests
- **Tool errors**: Missing parameters, invalid arguments

All errors are returned as MCP `TextContent` responses for LLM visibility.

## Security

- Bot credentials are required for editing operations
- All API requests include proper User-Agent headers
- CSRF tokens are automatically managed
- Input validation on all tool parameters

## License

[Your License Here]
