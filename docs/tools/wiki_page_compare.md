### wiki_page_compare

Compare two pages, revisions, or text content to show differences between them. This tool provides comprehensive diff capabilities including HTML-formatted differences, metadata comparison, and slot-specific comparisons for multi-content revisions.

**From Source Parameters (at least one required):**
- `fromtitle` (string): Title of the first page to compare
- `fromid` (integer): Page ID of the first page to compare
- `fromrev` (integer): Revision ID of the first revision to compare

**To Source Parameters (at least one required):**
- `totitle` (string): Title of the second page to compare
- `toid` (integer): Page ID of the second page to compare
- `torev` (integer): Revision ID of the second revision to compare
- `torelative` (string): Use a revision relative to the "from" revision. Options: "cur" (current), "next", "prev"

**Content Override Parameters:**
- `fromslots` (string): Pipe-separated list of slots to override in the "from" revision (e.g., "main")
- `toslots` (string): Pipe-separated list of slots to override in the "to" revision (e.g., "main")
- `frompst` (boolean): Apply pre-save transform to "from" content (default: false)
- `topst` (boolean): Apply pre-save transform to "to" content (default: false)

**Templated Slot Parameters for "from" side:**
- `fromtext_main` (string): Custom text content for the main slot of the "from" revision
- `fromsection_main` (string): Section identifier when using section content for the "from" revision
- `fromcontentmodel_main` (string): Content model for the "from" text (e.g., "wikitext", "json", "css")
- `fromcontentformat_main` (string): Content serialization format for the "from" text

**Templated Slot Parameters for "to" side:**
- `totext_main` (string): Custom text content for the main slot of the "to" revision
- `tosection_main` (string): Section identifier when using section content for the "to" revision
- `tocontentmodel_main` (string): Content model for the "to" text (e.g., "wikitext", "json", "css")
- `tocontentformat_main` (string): Content serialization format for the "to" text

**Output Control Parameters:**
- `prop` (string): Pipe-separated list of information to include. Options: "comment", "diff", "diffsize", "ids", "parsedcomment", "rel", "size", "timestamp", "title", "user" (default: "diff|ids|title")
- `slots` (string): Return individual diffs for specific slots rather than combined diff. Use "*" for all slots or pipe-separated slot names
- `difftype` (string): Format of the diff output. Options: "table" (default), "inline", "unified"

**Example Usage:**

Compare two pages by title:
```
fromtitle: "Template:Example"
totitle: "Template:Example/sandbox"
prop: "diff|title|user|timestamp"
```

Compare specific revisions:
```
fromrev: 12345
torev: 12346
difftype: "unified"
```

Compare current revision to previous:
```
fromtitle: "Main Page"
torelative: "prev"
prop: "diff|diffsize|comment"
```

Compare with custom content:
```
fromrev: 12345
torev: 12346
fromslots: "main"
fromtext_main: "Custom comparison text"
fromcontentmodel_main: "wikitext"
```

**Return Format:**

The tool returns a formatted text output containing:
- Page/revision identification information
- Diff size and metadata (timestamps, users, comments) if requested
- HTML-formatted diff showing additions, deletions, and changes
- Individual slot diffs if multiple slots are compared
- Clear indication when no differences are found

**Common Use Cases:**
- Reviewing changes between page revisions
- Comparing live pages with sandbox versions
- Analyzing differences in template implementations
- Checking content changes before publishing
- Debugging page content issues by comparing known good revisions

**Notes:**
- At least one "from" parameter and one "to" parameter must be specified
- Templated slot parameters use underscores in parameter names (e.g., `fromtext_main`) but are converted to hyphens internally (e.g., `fromtext-main`)
- The diff HTML output is formatted for display in tables with appropriate CSS classes
- Relative comparisons at the first or last revision of a page may produce special results as documented in the MediaWiki API
