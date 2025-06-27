### wiki_page_delete

Delete MediaWiki pages with comprehensive deletion options including talk pages, watchlist management, and detailed logging. This tool provides full access to MediaWiki's delete API functionality.

**Page Identification Parameters:**
- `title` (string): Title of the page to delete. Cannot be used together with `pageid`
- `pageid` (integer): Page ID of the page to delete. Cannot be used together with `title`. Useful for precisely identifying pages with special characters or ambiguous titles

**Deletion Reason Parameters:**
- `reason` (string): Reason for the deletion. If not provided, an automatically generated reason will be used. This appears in the deletion log and helps other editors understand the purpose of the deletion

**Associated Content Parameters:**
- `deletetalk` (boolean): Delete the associated talk page, if it exists (default: false). Automatically removes the discussion page related to the deleted page

**Change Tracking Parameters:**
- `tags` (array of strings): Change tags to apply to the entry in the deletion log. Helps categorize and track different types of deletions for administrative purposes

**Watchlist Management Parameters:**
- `watchlist` (string): Watchlist behavior for the deleted page (default: "preferences")
  - `"nochange"`: Don't change current watchlist status
  - `"preferences"`: Use user preferences (typically ignored for bot users)
  - `"unwatch"`: Remove from watchlist after deletion
  - `"watch"`: Add to watchlist (note: deleted pages are automatically removed from watchlists)
- `watchlistexpiry` (string): Watchlist expiry timestamp in ISO 8601 format. Omit to leave current expiry unchanged
- `watch` (boolean): **Deprecated.** Add the page to the current user's watchlist. Use `watchlist` parameter instead
- `unwatch` (boolean): **Deprecated.** Remove the page from the current user's watchlist. Use `watchlist` parameter instead

**File-Specific Parameters:**
- `oldimage` (string): For file pages, the name of the old image revision to delete as provided by `action=query&prop=imageinfo&iiprop=archivename`. Used to delete specific file revisions rather than the entire file page

**Important Notes:**
- Either `title` or `pageid` must be provided to identify the page to delete
- Deletion operations require appropriate permissions (delete rights) in the MediaWiki installation
- The deletion is logged in the deletion log with the provided reason and any specified tags
- Deleted pages can typically be restored by administrators through the MediaWiki interface
- Talk page deletion with `deletetalk` requires separate permissions and may fail even if the main page deletion succeeds
- File deletions may behave differently depending on whether `oldimage` is specified (revision deletion vs. full file deletion)
