# MediaWiki MCP Server

A Model Context Protocol (MCP) server that allows LLMs like Claude to interact with MediaWiki installations through the MediaWiki API as a bot user.

## Features

The server provides various MCP tools with the `wiki_` prefix:

- **`wiki_page_edit`**: Edit or create MediaWiki pages with comprehensive editing options
- **`wiki_page_get`**: Retrieve page information and content
- **`wiki_search`**: Search for pages using MediaWiki's search API with advanced filtering
- **`wiki_opensearch`**: Search using OpenSearch protocol for quick suggestions and autocomplete

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
    ├── wiki_search.py    # Search handlers
    └── wiki_opensearch.py # OpenSearch handlers

tests/
├── __init__.py
├── test_server.py         # Integration tests
├── test_wiki_page_edit.py # Edit handler tests
├── test_wiki_page_get.py  # Get handler tests
├── test_wiki_search.py    # Search handler tests
├── test_wiki_opensearch.py # OpenSearch handler tests
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

## Tools

### wiki_page_edit

Edit or create MediaWiki pages with comprehensive editing capabilities. This tool supports full page creation, content replacement, section editing, and text appending/prepending operations.

**Page Identification Parameters:**
- `title` (string): Title of the page to edit. Either this or `pageid` must be provided
- `pageid` (integer): Page ID of the page to edit. Alternative to `title` for precise page identification

**Content Modification Parameters:**
- `text` (string): Complete page content that replaces all existing content
- `appendtext` (string): Text to append to the end of the page or specified section
- `prependtext` (string): Text to prepend to the beginning of the page or specified section

**Section Editing Parameters:**
- `section` (string): Section to edit. Use "0" for the top section, "new" to create a new section, or a section number for existing sections
- `sectiontitle` (string): Title for the new section when using `section="new"`

**Edit Metadata Parameters:**
- `summary` (string): Edit summary describing the changes made. Highly recommended for tracking edit history
- `minor` (boolean): Mark edit as minor (default: false). Minor edits are typically small corrections or formatting changes
- `bot` (boolean): Mark edit as a bot edit (default: true). Helps distinguish automated edits in page history

**Page Creation/Protection Parameters:**
- `createonly` (boolean): Only create the page if it doesn't exist. Fails if page already exists (default: false)
- `nocreate` (boolean): Only edit existing pages. Fails if page doesn't exist (default: false)

### wiki_page_get

Retrieve page information and content using multiple MediaWiki API methods optimized for different use cases. Supports various output formats and retrieval strategies.

**Page Identification Parameters:**
- `title` (string): Title of the page to retrieve. Either this or `pageid` must be provided
- `pageid` (integer): Page ID of the page to retrieve. Alternative to `title` for precise page identification

**Retrieval Method Parameters:**
- `method` (string): Retrieval strategy with different performance characteristics (default: "revisions")
  - `"revisions"`: Uses Revisions API for complete page content with metadata. Most comprehensive but slower
  - `"parse"`: Uses Parse API for processed content. Good for getting formatted output
  - `"raw"`: Uses Raw API for fastest wikitext retrieval. Minimal metadata but highest performance
  - `"extracts"`: Uses TextExtracts API for plain text summaries. Best for getting readable content excerpts

**Content Format Parameters:**
- `format` (string): Output format for content (default: "wikitext")
  - `"wikitext"`: Raw MediaWiki markup (available for all methods)
  - `"html"`: Parsed HTML content (only available with `method="parse"`)
  - `"text"`: Plain text without markup (only available with `method="extracts"`)

**Extract Limitation Parameters (only for `method="extracts"`):**
- `sentences` (integer): Number of sentences to extract from the beginning of the page
- `chars` (integer): Character limit for extract length. Cannot be used simultaneously with `sentences`

### wiki_search

Comprehensive search functionality using MediaWiki's advanced search API with extensive filtering, sorting, and result customization options.

**Core Search Parameters:**
- `query` (string): **Required.** Search query string using MediaWiki search syntax

**Namespace Filtering Parameters:**
- `namespaces` (array of integers): List of namespace IDs to search within (default: [0] for main namespace)
  - Common namespaces: 0 (Main), 1 (Talk), 2 (User), 3 (User talk), 4 (Project), 6 (File), 10 (Template), 14 (Category)

**Search Type Parameters:**
- `what` (string): Type of search to perform (default: "text")
  - `"text"`: Full-text search in page content
  - `"title"`: Search only in page titles
  - `"nearmatch"`: Find pages with titles closely matching the query

**Pagination Parameters:**
- `limit` (integer): Maximum number of results to return. Range: 1-500 (default: 10)
- `offset` (integer): Starting position for results, enabling pagination (default: 0)

**Result Properties Parameters:**
- `prop` (array of strings): Properties to include for each search result
  - `"categorysnippet"`: Snippet showing category matches
  - `"extensiondata"`: Additional extension-specific data
  - `"isfilematch"`: Whether the match is in file content
  - `"redirectsnippet"`: Snippet from redirect pages
  - `"redirecttitle"`: Title of redirect source
  - `"sectionsnippet"`: Snippet from specific page sections
  - `"sectiontitle"`: Title of matching sections
  - `"size"`: Page size in bytes
  - `"snippet"`: Highlighted search result snippet
  - `"timestamp"`: Last edit timestamp
  - `"titlesnippet"`: Highlighted title snippet
  - `"wordcount"`: Number of words in the page

**Search Metadata Parameters:**
- `info` (array of strings): Metadata to return about the search
  - `"rewrittenquery"`: Shows how the search engine rewrote the query
  - `"suggestion"`: Alternative query suggestions
  - `"totalhits"`: Total number of matching pages

**Advanced Search Parameters:**
- `srsort` (string): Sort order for results (default: "relevance")
  - `"relevance"`: Sort by search relevance score
  - `"create_timestamp_asc"` / `"create_timestamp_desc"`: Sort by page creation date
  - `"last_edit_asc"` / `"last_edit_desc"`: Sort by last edit timestamp
  - `"incoming_links_asc"` / `"incoming_links_desc"`: Sort by number of incoming links
  - `"just_match"`: Return only matching results without sorting
  - `"none"`: No specific sort order
  - `"random"` / `"user_random"`: Random ordering

**Search Enhancement Parameters:**
- `enable_rewrites` (boolean): Enable internal query rewriting for improved results (default: true)
- `interwiki` (boolean): Include results from other wikis if interwiki search is configured (default: false)
- `qiprofile` (string): Query-independent ranking profile (default: "engine_autoselect")
  - `"engine_autoselect"`: Let the search engine choose the best profile
  - `"classic"`: Traditional MediaWiki search ranking
  - `"classic_noboostlinks"`: Classic ranking without link boost
  - `"popular_inclinks"`: Boost pages with more incoming links
  - `"popular_inclinks_pv"`: Boost popular pages with incoming links and page views
  - `"wsum_inclinks"` / `"wsum_inclinks_pv"`: Weighted sum algorithms with link metrics

### wiki_opensearch

Search the wiki using the OpenSearch protocol, which provides fast suggestions and autocomplete functionality. Returns results in the standard OpenSearch format with titles, descriptions, and URLs.

**Core Search Parameters:**
- `search` (string): **Required.** Search string to find matching pages

**Namespace Filtering Parameters:**
- `namespace` (array of integers): List of namespace IDs to search within (default: [0] for main namespace)
  - Common namespaces: 0 (Main), 1 (Talk), 2 (User), 4 (Project), 6 (File), 10 (Template), 14 (Category)

**Result Control Parameters:**
- `limit` (integer): Maximum number of results to return. Range: 1-500 (default: 10)

**Search Profile Parameters:**
- `profile` (string): Search profile that determines search behavior (default: "engine_autoselect")
  - `"strict"`: Strict profile with few punctuation characters removed but diacritics and stress marks kept
  - `"normal"`: Few punctuation characters, some diacritics and stopwords removed
  - `"normal-subphrases"`: Normal profile that also matches subphrases/subpages
  - `"fuzzy"`: Similar to normal with typo correction (two typos supported)
  - `"fast-fuzzy"`: Experimental fuzzy profile for rapid results
  - `"fuzzy-subphrases"`: Fuzzy profile that also matches subphrases/subpages
  - `"classic"`: Classic prefix matching with some punctuation and diacritics removed
  - `"engine_autoselect"`: Let the search engine decide on the best profile

**Redirect Handling Parameters:**
- `redirects` (string): How to handle redirect pages
  - `"return"`: Return the redirect page itself in results
  - `"resolve"`: Return the target page that the redirect points to

**Response Format Parameters:**
- `format` (string): Output format for the response (default: "json")
  - `"json"`: JSON format response
  - `"xml"`: XML format response

**Advanced Parameters:**
- `warningsaserror` (boolean): Treat API warnings as errors (default: false)

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
uv run pytest tests/test_wiki_opensearch.py
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
