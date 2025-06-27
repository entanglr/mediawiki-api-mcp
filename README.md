# MediaWiki API MCP Server

A Model Context Protocol (MCP) server that allows LLMs like Claude to interact with MediaWiki installations through the MediaWiki API as a bot user.

## Features

### Tools

The server provides various MCP tools with the `wiki_` prefix:

|Tool|Description|
|---|---|
|[**`wiki_page_edit`**](docs/tools/wiki_page_edit.md)|Edit or create MediaWiki pages with comprehensive editing options|
|[**`wiki_page_get`**](docs/tools/wiki_page_get.md)|Retrieve page information and content|
|[**`wiki_page_move`**](docs/tools/wiki_page_move.md)|Move pages with support for talk pages, subpages, and redirects|
|[**`wiki_page_delete`**](docs/tools/wiki_page_delete.md)|Delete pages with support for talk pages, watchlist management, and logging|
|[**`wiki_search`**](docs/tools/wiki_search.md)|Search for pages using MediaWiki's search API with advanced filtering|
|[**`wiki_opensearch`**](docs/tools/wiki_opensearch.md)|Search using OpenSearch protocol for quick suggestions and autocomplete|

## Installation

1. Clone the repository and checkout the `main` branch

2. Install dependencies using UV:

```bash
uv install
```

3. Set up environment variables:

```bash
export MEDIAWIKI_API_URL="http://mediawiki.test/api.php"
export MEDIAWIKI_API_BOT_USERNAME="YourUserName@YourBotName"
export MEDIAWIKI_API_BOT_PASSWORD="YourBotPassword"
export MEDIAWIKI_API_BOT_USER_AGENT="MediaWiki-MCP-Bot/1.0 (your.email@mediawiki.test)"  # Optional
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

#### Configuration File Location

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

#### Template Configuration

Add to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "mediawiki-api": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/mediawiki-api-mcp",
        "run",
        "mediawiki-api-mcp"
      ],
      "env": {
        "MEDIAWIKI_API_URL": "http://mediawiki.test/api.php",
        "MEDIAWIKI_API_BOT_USERNAME": "YourUserName@YourBotName",
        "MEDIAWIKI_API_BOT_PASSWORD": "YourBotPassword",
        "MEDIAWIKI_API_BOT_USER_AGENT": "MediaWiki-MCP-Bot/1.0 (your.email@mediawiki.test)"
      }
    }
  }
}
```

#### Configuration Instructions

1. Replace `/absolute/path/to/mediawiki-api-mcp` with the actual absolute path to this project directory
2. Update `MEDIAWIKI_API_URL` with your MediaWiki installation's API endpoint
3. Set `MEDIAWIKI_API_BOT_USERNAME` to your bot username (typically in format `YourUserName@YourBotName`)
4. Set `MEDIAWIKI_API_BOT_PASSWORD` to the generated bot password from your wiki's `Special:BotPasswords` page
5. Customize `MEDIAWIKI_API_BOT_USER_AGENT` with appropriate contact information (optional)

##### Bot Password Setup

Create bot credentials at e.g.: `http://mediawiki.test/index.php/Special:BotPasswords`

Required permissions:

- **Basic rights**: Read pages
- **High-volume editing**: Edit existing pages, Create, edit, and move pages
- Additional permissions as needed for your specific use case

##### Security Notes

- Keep your bot credentials secure and never commit them to version control
- Use the principle of least privilege when setting bot permissions
- Monitor bot activity through your MediaWiki's logging interface
- Consider using IP restrictions for additional security

## Development

### Architecture

#### Client Layer (`client.py`)
- Handles MediaWiki API authentication and requests
- Manages CSRF tokens and session state
- Provides typed methods for API operations

#### Tools Layer (`tools/`)
- Defines MCP tool schemas using JSON Schema
- Separated by functional area (edit, search)
- Ensures all tools have `wiki_` prefix

#### Handlers Layer (`handlers/`)
- Implements actual tool logic
- Handles argument validation and error handling
- Returns properly formatted MCP responses

#### Server Layer (`server.py`)
- Main MCP server orchestration
- Routes tool calls to appropriate handlers
- Manages configuration and client lifecycle

### Project Structure

The project is organized into modular components for maintainability:

```
mediawiki_api_mcp/
├── __init__.py
├── server.py                # Main MCP server implementation
├── client.py                # MediaWiki API client
├── tools/                   # Tool definitions
│   ├── __init__.py
│   ├── wiki_page_edit.py    # Edit page tools
│   ├── wiki_page_get.py     # Get page tools
│   ├── wiki_page_move.py    # Move page tools
│   ├── wiki_page_delete.py  # Delete page tools
│   └── wiki_search.py       # Search tools
└── handlers/                # Tool handlers
    ├── __init__.py
    ├── wiki_page_edit.py    # Edit page handlers
    ├── wiki_page_get.py     # Get page handlers
    ├── wiki_page_move.py    # Move page handlers
    ├── wiki_page_delete.py  # Delete page handlers
    ├── wiki_search.py       # Search handlers
    └── wiki_opensearch.py   # OpenSearch handlers

tests/
├── __init__.py
├── test_server.py           # Integration tests
├── test_wiki_page_edit.py   # Edit handler tests
├── test_wiki_page_get.py    # Get handler tests
├── test_wiki_page_move.py   # Move handler tests
├── test_wiki_page_delete.py # Delete handler tests
├── test_wiki_search.py      # Search handler tests
├── test_wiki_opensearch.py  # OpenSearch handler tests
└── test_tools.py            # Tool definition tests
```

### Running Tests

```bash
uv run pytest
```

Run specific test modules, e.g.:

```bash
uv run pytest tests/test_server.py
uv run pytest tests/test_tools.py
uv run pytest tests/test_wiki_page_edit.py
uv run pytest tests/test_wiki_search.py
uv run pytest tests/test_wiki_opensearch.py
```

### Code Quality

```bash
# Linting
uv run ruff check

# Type checking
uv run mypy mediawiki_api_mcp
```

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

[MIT License](https://github.com/entanglr/mediawiki-api-mcp/blob/main/LICENSE)
