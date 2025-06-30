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
