"""Wiki page parse tool for MediaWiki API MCP integration."""

import logging
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..client import MediaWikiClient
from ..config import MediaWikiConfig

logger = logging.getLogger(__name__)


def register_wiki_page_parse_tool(mcp: FastMCP, get_config: Callable[[], MediaWikiConfig]) -> None:
    """Register the wiki_page_parse tool with the MCP server."""

    @mcp.tool()
    async def wiki_page_parse(
        title: str = "",
        pageid: int = 0,
        oldid: int = 0,
        text: str = "",
        revid: int = 0,
        summary: str = "",
        page: str = "",
        redirects: bool = False,
        prop: str = "",
        wrapoutputclass: str = "",
        usearticle: bool = False,
        parsoid: bool = False,
        pst: bool = False,
        onlypst: bool = False,
        section: str = "",
        sectiontitle: str = "",
        disablelimitreport: bool = False,
        disableeditsection: bool = False,
        disablestylededuplication: bool = False,
        showstrategykeys: bool = False,
        preview: bool = False,
        sectionpreview: bool = False,
        disabletoc: bool = False,
        useskin: str = "",
        contentformat: str = "",
        contentmodel: str = "",
        mobileformat: bool = False,
        templatesandboxprefix: str = "",
        templatesandboxtitle: str = "",
        templatesandboxtext: str = "",
        templatesandboxcontentmodel: str = "",
        templatesandboxcontentformat: str = "",
    ) -> str:
        """Parse content and return parser output from a MediaWiki page.

        Supports parsing existing pages by title/ID, arbitrary wikitext, or summaries.
        Returns comprehensive parsing information including HTML, metadata, and analysis.

        Content Source Parameters (provide one):
            title: Title of page the text belongs to
            pageid: Parse the content of this page (overrides page)
            oldid: Parse the content of this revision (overrides page and pageid)
            text: Text to parse (use title or contentmodel to control content model)
            revid: Revision ID for {{REVISIONID}} and similar variables
            summary: Summary to parse
            page: Parse the content of this page

        Output Control Parameters:
            redirects: If page or pageid is set to a redirect, resolve it
            prop: Which pieces of information to get (pipe-separated: text|langlinks|categories|links|templates|images|externallinks|sections|revid|displaytitle|iwlinks|properties|parsewarnings)
            wrapoutputclass: CSS class to use to wrap the parser output
            usearticle: Use ArticleParserOptions hook for article page views
            parsoid: Generate HTML conforming to MediaWiki DOM spec using Parsoid
            pst: Do a pre-save transform on the input before parsing
            onlypst: Do PST on input but don't parse it
            section: Only parse content of section with this identifier
            sectiontitle: New section title when section is "new"
            disablelimitreport: Omit the limit report from parser output
            disableeditsection: Omit edit section links from parser output
            disablestylededuplication: Do not deduplicate inline stylesheets
            showstrategykeys: Include internal merge strategy info in jsconfigvars
            preview: Parse in preview mode
            sectionpreview: Parse in section preview mode
            disabletoc: Omit table of contents in output
            useskin: Apply selected skin to parser output
            contentformat: Content serialization format for input text
            contentmodel: Content model of input text
            mobileformat: Return parse output suitable for mobile devices
            templatesandboxprefix: Template sandbox prefix (pipe-separated)
            templatesandboxtitle: Parse page using templatesandboxtext
            templatesandboxtext: Parse page using this content
            templatesandboxcontentmodel: Content model of templatesandboxtext
            templatesandboxcontentformat: Content format of templatesandboxtext
        """
        try:
            config = get_config()
            async with MediaWikiClient(config) as client:
                # Import here to avoid circular imports
                from ..handlers import handle_parse_page

                # Convert FastMCP parameters to handler arguments
                arguments = {}

                # Content source parameters
                if title:
                    arguments["title"] = title
                if pageid:
                    arguments["pageid"] = pageid
                if oldid:
                    arguments["oldid"] = oldid
                if text:
                    arguments["text"] = text
                if revid:
                    arguments["revid"] = revid
                if summary:
                    arguments["summary"] = summary
                if page:
                    arguments["page"] = page

                # Control parameters
                if redirects:
                    arguments["redirects"] = redirects
                if prop:
                    arguments["prop"] = prop
                if wrapoutputclass:
                    arguments["wrapoutputclass"] = wrapoutputclass
                if usearticle:
                    arguments["usearticle"] = usearticle
                if parsoid:
                    arguments["parsoid"] = parsoid
                if pst:
                    arguments["pst"] = pst
                if onlypst:
                    arguments["onlypst"] = onlypst
                if section:
                    arguments["section"] = section
                if sectiontitle:
                    arguments["sectiontitle"] = sectiontitle
                if disablelimitreport:
                    arguments["disablelimitreport"] = disablelimitreport
                if disableeditsection:
                    arguments["disableeditsection"] = disableeditsection
                if disablestylededuplication:
                    arguments["disablestylededuplication"] = disablestylededuplication
                if showstrategykeys:
                    arguments["showstrategykeys"] = showstrategykeys
                if preview:
                    arguments["preview"] = preview
                if sectionpreview:
                    arguments["sectionpreview"] = sectionpreview
                if disabletoc:
                    arguments["disabletoc"] = disabletoc
                if useskin:
                    arguments["useskin"] = useskin
                if contentformat:
                    arguments["contentformat"] = contentformat
                if contentmodel:
                    arguments["contentmodel"] = contentmodel
                if mobileformat:
                    arguments["mobileformat"] = mobileformat
                if templatesandboxprefix:
                    arguments["templatesandboxprefix"] = templatesandboxprefix
                if templatesandboxtitle:
                    arguments["templatesandboxtitle"] = templatesandboxtitle
                if templatesandboxtext:
                    arguments["templatesandboxtext"] = templatesandboxtext
                if templatesandboxcontentmodel:
                    arguments["templatesandboxcontentmodel"] = templatesandboxcontentmodel
                if templatesandboxcontentformat:
                    arguments["templatesandboxcontentformat"] = templatesandboxcontentformat

                result = await handle_parse_page(client, arguments)
                # Return the formatted text from the handler
                return result[0].text if result else "No results"
        except Exception as e:
            logger.error(f"Wiki page parse failed: {e}")
            return f"Error: {str(e)}"
