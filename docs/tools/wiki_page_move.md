### wiki_page_move

Move a page with comprehensive options for handling talk pages, subpages, and redirects. This tool enables renaming pages while maintaining proper link structure and history preservation.

**Page Identification Parameters:**
- `from_title` (string): Title of the page to rename. Cannot be used together with `fromid`
- `fromid` (integer): Page ID of the page to rename. Cannot be used together with `from_title`. Useful for precisely identifying pages with special characters or ambiguous titles
- `to` (string): **Required.** Title to rename the page to. Must be a valid page title in the destination namespace

**Move Reason Parameters:**
- `reason` (string): Reason for the rename. This appears in the move log and helps other editors understand the purpose of the move

**Associated Content Parameters:**
- `movetalk` (boolean): Rename the talk page, if it exists (default: false). Automatically moves the associated discussion page
- `movesubpages` (boolean): Rename subpages, if applicable (default: false). Moves all subpages that follow the pattern `OriginalPage/Subpage`

**Redirect Handling Parameters:**
- `noredirect` (boolean): Don't create a redirect from the old page name (default: false). Requires special permissions (typically bot or sysop rights)

**Watchlist Management Parameters:**
- `watchlist` (string): Watchlist behavior for the moved page (default: "preferences")
  - `"nochange"`: Don't change current watchlist status
  - `"preferences"`: Use user preferences (typically ignored for bot users)
  - `"unwatch"`: Remove from watchlist
  - `"watch"`: Add to watchlist
- `watchlistexpiry` (string): Watchlist expiry timestamp in ISO 8601 format. Omit to leave current expiry unchanged

**Advanced Parameters:**
- `ignorewarnings` (boolean): Ignore any warnings that would normally prevent the move (default: false)
- `tags` (string): Change tags to apply to the move log entry and destination page. Multiple tags separated by pipe (`|`) character

**Important Notes:**
- The `noredirect` option requires the `suppressredirect` right, typically granted to bots and sysops
- If redirect suppression is attempted without proper rights, the API will create a redirect without returning an error
- Subpage moves may fail individually while the main page move succeeds; check response for detailed status
- Some namespaces may be protected from moves (e.g., MediaWiki namespace)
