### wiki_page_compare

Compare two revisions of MediaWiki pages or arbitrary content using the Compare API. This tool creates diff output showing differences between specified content sources in various formats, supporting both revision comparison and custom content comparison.

**Source Content Specification (From) Parameters:**
- `fromtitle` (string): Title of the first page to compare
- `fromid` (integer): Page ID of the first page to compare
- `fromrev` (integer): Revision ID of the first content to compare

**Target Content Specification (To) Parameters:**
- `totitle` (string): Title of the second page to compare
- `toid` (integer): Page ID of the second page to compare
- `torev` (integer): Revision ID of the second content to compare

**Slot Management Parameters:**
- `fromslots` (string): Pipe-separated list of slots to modify on the 'from' side. Use templated slot parameters for slot-specific content
- `toslots` (string): Pipe-separated list of slots to modify on the 'to' side. Use templated slot parameters for slot-specific content

**Output Control Parameters:**
- `prop` (string): Which pieces of information to return. Use '*' to specify all available values
- `difftype` (string): Format of diff output. Options: 'inline', 'table', 'unified'

**Slot-Specific Content Parameters (Main Slot):**
- `fromtext_main` (string): Text content for the main slot on 'from' side
- `totext_main` (string): Text content for the main slot on 'to' side
- `fromcontentformat_main` (string): Content serialization format for main slot on 'from' side
- `tocontentformat_main` (string): Content serialization format for main slot on 'to' side
- `fromcontentmodel_main` (string): Content model for main slot on 'from' side (e.g., 'wikitext', 'json', 'css')
- `tocontentmodel_main` (string): Content model for main slot on 'to' side
- `fromsection_main` (string): Section identifier for main slot on 'from' side
- `tosection_main` (string): Section identifier for main slot on 'to' side
- `frompst_main` (boolean): Perform pre-save transform for main slot on 'from' side
- `topst_main` (boolean): Perform pre-save transform for main slot on 'to' side

**Legacy Parameters (Deprecated but Supported):**
- `fromtext` (string): Text content for 'from' side (use `fromslots=main` and `fromtext_main` instead)
- `totext` (string): Text content for 'to' side (use `toslots=main` and `totext_main` instead)
- `fromcontentformat` (string): Content format for 'from' side (use `fromcontentformat_main` instead)
- `tocontentformat` (string): Content format for 'to' side (use `tocontentformat_main` instead)
- `fromcontentmodel` (string): Content model for 'from' side (use `fromcontentmodel_main` instead)
- `tocontentmodel` (string): Content model for 'to' side (use `tocontentmodel_main` instead)
- `tosection` (string): Section identifier for 'to' side (use slot-specific section parameters instead)

**Supported Content Formats:**
- `application/json`
- `application/octet-stream`
- `application/unknown`
- `application/x-binary`
- `text/css`
- `text/javascript`
- `text/plain`
- `text/unknown`
- `text/x-wiki`
- `unknown/unknown`

**Supported Content Models:**
- `GadgetDefinition`
- `JsonSchema`
- `MassMessageListContent`
- `NewsletterContent`
- `Scribunto`
- `SecurePoll`
- `css`
- `flow-board`
- `javascript`
- `json`
- `sanitized-css`
- `text`
- `translate-messagebundle`
- `unknown`
- `wikitext`

**Usage Examples:**

**Compare Two Specific Revisions:**
```
fromrev: 12345
torev: 12350
difftype: table
```

**Compare Current Page Content with Modified Text:**
```
fromtitle: "Example Page"
toslots: "main"
totext_main: "Modified content"
tocontentmodel_main: "wikitext"
difftype: unified
```

**Compare Two Different Pages:**
```
fromtitle: "Page A"
totitle: "Page B"
prop: "*"
difftype: inline
```

**Compare with Section Modification:**
```
fromtitle: "Documentation"
toslots: "main"
totext_main: "Updated section content"
tosection_main: "2"
tocontentmodel_main: "wikitext"
```

**Advanced Slot-Based Comparison:**
```
fromtitle: "Template:Example"
toslots: "main"
totext_main: "{{Updated template code}}"
tocontentmodel_main: "wikitext"
topst_main: true
difftype: table
```

**Notes:**
- At least one 'from' parameter (fromtitle, fromid, fromrev, fromtext, or fromslots) is required
- At least one 'to' parameter (totitle, toid, torev, totext, or toslots) is required
- Slot-based parameters take precedence over legacy parameters when both are provided
- Content models should match the actual content type for accurate parsing
- The tool returns formatted comparison output showing additions, deletions, and metadata
