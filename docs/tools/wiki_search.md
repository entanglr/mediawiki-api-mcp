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
