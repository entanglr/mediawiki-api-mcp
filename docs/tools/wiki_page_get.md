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
