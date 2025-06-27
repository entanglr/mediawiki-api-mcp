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
