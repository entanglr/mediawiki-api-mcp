### wiki_page_parse

Parse content and return parser output from a MediaWiki page using the comprehensive Parse API. This tool provides access to MediaWiki's full parsing engine with support for wikitext processing, HTML generation, metadata extraction, and advanced parsing features.

**Content Source Parameters (provide one):**
- `title` (string): Title of page the text belongs to. If omitted, contentmodel must be specified
- `pageid` (integer): Parse the content of this page. Overrides `page` parameter
- `oldid` (integer): Parse the content of this revision. Overrides `page` and `pageid` parameters
- `text` (string): Text to parse. Use `title` or `contentmodel` to control the content model
- `revid` (integer): Revision ID, for {{REVISIONID}} and similar variables
- `summary` (string): Summary to parse (for parsing edit summaries)
- `page` (string): Parse the content of this page. Cannot be used together with `text` and `title`

**Output Control Parameters:**
- `redirects` (boolean): If page or pageid is set to a redirect, resolve it (default: false)
- `prop` (string): Which pieces of information to get. Pipe-separated values from:
  - `text`: Gives the parsed text of the wikitext (HTML output)
  - `langlinks`: Gives the language links in the parsed wikitext
  - `categories`: Gives the categories in the parsed wikitext
  - `categorieshtml`: Gives the HTML version of the categories
  - `links`: Gives the internal links in the parsed wikitext
  - `templates`: Gives the templates in the parsed wikitext
  - `images`: Gives the images in the parsed wikitext
  - `externallinks`: Gives the external links in the parsed wikitext
  - `sections`: Gives the sections in the parsed wikitext
  - `revid`: Adds the revision ID of the parsed page
  - `displaytitle`: Adds the title of the parsed wikitext
  - `subtitle`: Adds the page subtitle for the parsed page
  - `wikitext`: Gives the original wikitext that was parsed
  - `properties`: Gives various properties defined in the parsed wikitext
  - `parsewarnings`: Gives the warnings that occurred while parsing content
  - `iwlinks`: Gives interwiki links in the parsed wikitext
  - Default: `text|langlinks|categories|links|templates|images|externallinks|sections|revid|displaytitle|iwlinks|properties|parsewarnings`

**Formatting and Display Parameters:**
- `wrapoutputclass` (string): CSS class to use to wrap the parser output (default: "mw-parser-output")
- `usearticle` (boolean): Use the ArticleParserOptions hook to ensure options match article page views
- `parsoid` (boolean): Generate HTML conforming to the MediaWiki DOM spec using Parsoid
- `useskin` (string): Apply the selected skin to the parser output (affects text, langlinks, modules, etc.)
- `mobileformat` (boolean): Return parse output in a format suitable for mobile devices

**Processing Control Parameters:**
- `pst` (boolean): Do a pre-save transform on the input before parsing it. Only valid when used with `text`
- `onlypst` (boolean): Do a pre-save transform (PST) on the input, but don't parse it. Only valid when used with `text`
- `preview` (boolean): Parse in preview mode
- `sectionpreview` (boolean): Parse in section preview mode (enables preview mode too)

**Section Parameters:**
- `section` (string): Only parse the content of the section with this identifier. Use "new" to parse text and sectiontitle as if adding a new section
- `sectiontitle` (string): New section title when section is "new". Unlike page editing, this does not fall back to summary when omitted

**Output Customization Parameters:**
- `disablelimitreport` (boolean): Omit the limit report ("NewPP limit report") from the parser output
- `disableeditsection` (boolean): Omit edit section links from the parser output
- `disablestylededuplication` (boolean): Do not deduplicate inline stylesheets in the parser output
- `disabletoc` (boolean): Omit table of contents in output
- `showstrategykeys` (boolean): Whether to include internal merge strategy information in jsconfigvars

**Content Model Parameters:**
- `contentformat` (string): Content serialization format used for the input text. Only valid when used with `text`
  - Options: application/json, application/octet-stream, text/css, text/javascript, text/plain, text/x-wiki, etc.
- `contentmodel` (string): Content model of the input text. If omitted, title must be specified. Only valid when used with `text`
  - Options: wikitext, javascript, css, json, text, etc.

**Template Sandbox Parameters:**
- `templatesandboxprefix` (string): Template sandbox prefix, as with Special:TemplateSandbox (pipe-separated for multiple values)
- `templatesandboxtitle` (string): Parse the page using templatesandboxtext in place of the contents of the page named here
- `templatesandboxtext` (string): Parse the page using this page content in place of the page named by templatesandboxtitle
- `templatesandboxcontentmodel` (string): Content model of templatesandboxtext
- `templatesandboxcontentformat` (string): Content format of templatesandboxtext

**Examples:**

Parse a page by title:
```
wiki_page_parse(title="Main Page")
```

Parse specific wikitext:
```
wiki_page_parse(text="Hello '''world'''! [[Example]]", contentmodel="wikitext")
```

Parse a page with specific properties:
```
wiki_page_parse(title="Example", prop="text|categories|links|templates")
```

Parse a section of a page:
```
wiki_page_parse(title="Large Article", section="2")
```

Parse with mobile formatting:
```
wiki_page_parse(title="Main Page", mobileformat=true, prop="text")
```

Parse a revision by ID:
```
wiki_page_parse(oldid=12345, prop="text|parsewarnings")
```

The tool returns comprehensive parsed content including HTML output, metadata, links, categories, templates, and any requested analysis information formatted in a readable structure.

## Recent Bug Fixes and Improvements

**Version Improvements (Latest)**:

**Bug Fix #1: Enhanced Content Retrieval**
- **Issue**: Pages returning empty content despite existing in database
- **Solution**: Improved page identification logic with proper priority handling (oldid > pageid > page/title > text)
- **Enhancement**: Added intelligent content detection that warns when minimal or missing content is returned
- **Result**: Reliable parsing of existing pages with clear diagnostics for content issues

**Bug Fix #2: Redirect Resolution**
- **Issue**: Redirect pages parsed as empty content instead of target content
- **Solution**: Proper implementation of `redirects` parameter to automatically resolve redirects to target pages
- **Enhancement**: Transparent redirect following ensures users get content from the target page
- **Result**: Redirect pages now correctly return the content from their target pages when `redirects=true`

**Bug Fix #3: Section Parsing Validation**
- **Issue**: "Unexpected response format" errors when using `section` parameter
- **Solution**: Added comprehensive section parameter validation and proper error handling
- **Enhancement**: Support for numeric sections, "new" sections, and template sections (T-prefix)
- **Result**: Reliable section parsing with clear error messages for invalid section identifiers

**Additional Improvements**:
- Enhanced error reporting with detailed diagnostics for troubleshooting
- Improved parameter validation to prevent common usage errors
- Better handling of edge cases in content parsing and formatting
- Comprehensive test coverage for all major functionality and edge cases
