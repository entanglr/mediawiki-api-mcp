### wiki_page_undelete

Undelete (restore) deleted MediaWiki pages with comprehensive restoration options including selective revision restoration, talk page recovery, and detailed logging. This tool provides full access to MediaWiki's undelete API functionality.

**Page Identification Parameters:**
- `title` (string, required): Title of the page to undelete. This must be the exact title of the deleted page as it appears in the deletion log

**Restoration Reason Parameters:**
- `reason` (string): Reason for restoring the page (default: empty). This appears in the deletion log and helps other editors understand the purpose of the restoration

**Selective Restoration Parameters:**
- `timestamps` (string): Pipe-separated list of timestamps of specific revisions to undelete (e.g., "2023-01-01T12:00:00Z|2023-01-02T15:30:00Z"). If both `timestamps` and `fileids` are empty, all revisions will be undeleted
- `fileids` (string): Pipe-separated list of file revision IDs to restore for file pages (e.g., "123|456"). If both `timestamps` and `fileids` are empty, all file versions will be restored

**Associated Content Parameters:**
- `undeletetalk` (boolean): Undelete all revisions of the associated talk page, if any (default: false). Automatically restores the discussion page related to the undeleted page

**Change Tracking Parameters:**
- `tags` (string): Pipe-separated list of change tags to apply to the entry in the deletion log (e.g., "restoration|admin-action"). Helps categorize and track different types of restorations for administrative purposes

**Watchlist Management Parameters:**
- `watchlist` (string): Watchlist behavior for the restored page (default: "preferences")
  - `"nochange"`: Don't change current watchlist status
  - `"preferences"`: Use user preferences (typically ignored for bot users)
  - `"unwatch"`: Remove from watchlist after restoration
  - `"watch"`: Add to watchlist after restoration
- `watchlistexpiry` (string): Watchlist expiry timestamp in ISO 8601 format. Omit to leave current expiry unchanged

**Response Information:**
The tool returns information about the restoration including:
- Page title that was restored
- Reason used for the restoration
- Number of revisions restored
- Number of file versions restored (for file pages)

**Important Notes:**
- The `title` parameter is required and must exactly match the deleted page title
- Undelete operations require appropriate permissions (undelete rights) in the MediaWiki installation
- The restoration is logged in the deletion log with the provided reason and any specified tags
- Selective restoration using `timestamps` or `fileids` allows for partial recovery of page history
- Talk page restoration with `undeletetalk` requires separate permissions and may fail even if the main page restoration succeeds
- If no specific revisions are specified via `timestamps` or `fileids`, all available revisions will be restored
- File pages can have both page revisions and file revisions, which are handled separately
- Some revisions may not be restorable if they have been permanently deleted or if there are permission restrictions

**Usage Examples:**
- Full restoration: `{"title": "Example Page", "reason": "Accidental deletion"}`
- Selective restoration: `{"title": "Example Page", "timestamps": "2023-01-01T12:00:00Z|2023-01-02T15:30:00Z", "reason": "Restore specific versions"}`
- File restoration: `{"title": "File:Example.jpg", "fileids": "123|456", "reason": "Restore file versions"}`
- Complete restoration with talk page: `{"title": "Example Page", "undeletetalk": true, "reason": "Full restoration needed"}`
