"""MediaWiki page parsing handlers for MCP server."""

import logging
from collections.abc import Sequence
from typing import Any

import mcp.types as types

from ..client import MediaWikiClient

logger = logging.getLogger(__name__)


async def handle_parse_page(
    client: MediaWikiClient,
    arguments: dict[str, Any]
) -> Sequence[types.TextContent]:
    """Handle wiki_page_parse tool calls with comprehensive Parse API support."""
    # Extract arguments with defaults
    title = arguments.get("title")
    pageid = arguments.get("pageid")
    oldid = arguments.get("oldid")
    text = arguments.get("text")
    revid = arguments.get("revid")
    summary = arguments.get("summary")
    page = arguments.get("page")
    redirects = arguments.get("redirects", False)
    prop = arguments.get("prop")
    wrapoutputclass = arguments.get("wrapoutputclass")
    usearticle = arguments.get("usearticle", False)
    parsoid = arguments.get("parsoid", False)
    pst = arguments.get("pst", False)
    onlypst = arguments.get("onlypst", False)
    section = arguments.get("section")
    sectiontitle = arguments.get("sectiontitle")
    disablelimitreport = arguments.get("disablelimitreport", False)
    disableeditsection = arguments.get("disableeditsection", False)
    disablestylededuplication = arguments.get("disablestylededuplication", False)
    showstrategykeys = arguments.get("showstrategykeys", False)
    preview = arguments.get("preview", False)
    sectionpreview = arguments.get("sectionpreview", False)
    disabletoc = arguments.get("disabletoc", False)
    useskin = arguments.get("useskin")
    contentformat = arguments.get("contentformat")
    contentmodel = arguments.get("contentmodel")
    mobileformat = arguments.get("mobileformat", False)
    templatesandboxprefix = arguments.get("templatesandboxprefix")
    templatesandboxtitle = arguments.get("templatesandboxtitle")
    templatesandboxtext = arguments.get("templatesandboxtext")
    templatesandboxcontentmodel = arguments.get("templatesandboxcontentmodel")
    templatesandboxcontentformat = arguments.get("templatesandboxcontentformat")

    # Validate that at least one content source is provided
    content_sources = [title, pageid, oldid, text, page, summary]
    if not any(content_sources):
        return [types.TextContent(
            type="text",
            text="Error: Must provide one of: title, pageid, oldid, text, page, or summary"
        )]

    # Convert prop to list if it's a string
    if prop and isinstance(prop, str):
        prop = [p.strip() for p in prop.split("|") if p.strip()]

    # Convert templatesandboxprefix to list if it's a string
    if templatesandboxprefix and isinstance(templatesandboxprefix, str):
        templatesandboxprefix = [p.strip() for p in templatesandboxprefix.split("|") if p.strip()]

    try:
        result = await client.parse_page(
            title=title,
            pageid=pageid,
            oldid=oldid,
            text=text,
            revid=revid,
            summary=summary,
            page=page,
            redirects=redirects,
            prop=prop,
            wrapoutputclass=wrapoutputclass,
            usearticle=usearticle,
            parsoid=parsoid,
            pst=pst,
            onlypst=onlypst,
            section=section,
            sectiontitle=sectiontitle,
            disablelimitreport=disablelimitreport,
            disableeditsection=disableeditsection,
            disablestylededuplication=disablestylededuplication,
            showstrategykeys=showstrategykeys,
            preview=preview,
            sectionpreview=sectionpreview,
            disabletoc=disabletoc,
            useskin=useskin,
            contentformat=contentformat,
            contentmodel=contentmodel,
            mobileformat=mobileformat,
            templatesandboxprefix=templatesandboxprefix,
            templatesandboxtitle=templatesandboxtitle,
            templatesandboxtext=templatesandboxtext,
            templatesandboxcontentmodel=templatesandboxcontentmodel,
            templatesandboxcontentformat=templatesandboxcontentformat
        )

        # Handle API errors
        if "error" in result:
            error_info = result["error"]
            if isinstance(error_info, dict):
                error_code = error_info.get("code", "unknown")
                error_message = error_info.get("info", "Unknown error")
                return [types.TextContent(
                    type="text",
                    text=f"MediaWiki API Error ({error_code}): {error_message}"
                )]
            else:
                # Handle case where error is a string
                return [types.TextContent(
                    type="text",
                    text=f"MediaWiki API Error: {error_info}"
                )]

        # Handle warnings
        warning_text = None
        if "warnings" in result:
            warnings = result["warnings"]
            warning_messages = []
            for key, warning in warnings.items():
                if isinstance(warning, dict) and "*" in warning:
                    warning_messages.append(f"{key}: {warning['*']}")
                else:
                    warning_messages.append(f"{key}: {warning}")

            if warning_messages:
                warning_text = "API Warnings:\n" + "\n".join(warning_messages)

        if "parse" not in result:
            # More detailed error reporting for debugging
            response_keys = list(result.keys())
            error_details = f"Response keys: {response_keys}"

            # Check for common error patterns
            if "query" in result:
                # This might indicate the wrong API endpoint was used
                error_details += "\nNote: Received 'query' response - verify Parse API is being used correctly"

            if "missing" in result or (isinstance(result.get("query", {}).get("pages", {}), dict) and
                                     any(page.get("missing", False) for page in result["query"]["pages"].values())):
                error_details += "\nNote: Page appears to be missing from the wiki"

            return [types.TextContent(
                type="text",
                text=f"Error: Unexpected response format from Parse API. {error_details}"
            )]

        return await _format_parse_result(result, prop, warning_text)

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error parsing content: {str(e)}"
        )]


async def _format_parse_result(
    result: dict[str, Any],
    requested_prop: list[str] | None,
    warning_text: str | None = None
) -> Sequence[types.TextContent]:
    """Format the parse result into a readable response."""
    parse_data = result["parse"]

    # Build the response header
    title = parse_data.get("title", "Unknown")
    pageid = parse_data.get("pageid", "Unknown")
    revid = parse_data.get("revid", "Unknown")

    response_lines = [
        f"Parse Results for: {title}",
        f"Page ID: {pageid}",
        f"Revision ID: {revid}",
        ""
    ]

    # Show warnings if any
    if warning_text:
        response_lines.append(warning_text)
        response_lines.append("")

    # Show which properties were requested
    if requested_prop:
        response_lines.append(f"Requested properties: {', '.join(requested_prop)}")
        response_lines.append("")

    # Format each available property
    formatted_sections = []

    # Main content (text)
    if "text" in parse_data:
        text_content = parse_data["text"]
        if isinstance(text_content, dict) and "*" in text_content:
            text_content = text_content["*"]

        # Check for minimal content issue mentioned in bug report
        if text_content and len(text_content.strip()) > 0:
            # Check if it's just an empty div (common issue)
            if ('<div class="mw-content-' in text_content and
                text_content.count('<') <= 3 and
                '<!-- metadata only -->' not in text_content and
                len(text_content.strip()) < 200):
                # This looks like minimal content - add warning
                formatted_sections.append(_format_section("Parsed HTML",
                    f"WARNING: Content appears minimal. This may indicate a page parsing issue.\n\n{text_content}"))
            else:
                formatted_sections.append(_format_section("Parsed HTML", text_content))
        else:
            formatted_sections.append(_format_section("Parsed HTML",
                "WARNING: No HTML content returned. The page may be empty or there may be a parsing issue."))
    else:
        # Check if this was an existing page request but no text was returned
        if any(parse_data.get(key) for key in ["pageid", "title"]) and parse_data.get("pageid", 0) > 0:
            formatted_sections.append(_format_section("Parsed HTML",
                "WARNING: No text content in parse result for existing page. This may indicate the page is empty or a parsing error occurred."))


    # Wikitext
    if "wikitext" in parse_data:
        wikitext_content = parse_data["wikitext"]
        if isinstance(wikitext_content, dict) and "*" in wikitext_content:
            wikitext_content = wikitext_content["*"]
        formatted_sections.append(_format_section("Wikitext", wikitext_content))

    # Categories
    if "categories" in parse_data:
        categories = parse_data["categories"]
        if categories:
            cat_list = [cat.get("*", cat.get("category", str(cat))) for cat in categories]
            formatted_sections.append(_format_section("Categories", "\n".join(cat_list)))

    # Links
    if "links" in parse_data:
        links = parse_data["links"]
        if links:
            link_list = [link.get("*", link.get("title", str(link))) for link in links]
            formatted_sections.append(_format_section("Internal Links", "\n".join(link_list)))

    # Templates
    if "templates" in parse_data:
        templates = parse_data["templates"]
        if templates:
            template_list = [tmpl.get("*", tmpl.get("title", str(tmpl))) for tmpl in templates]
            formatted_sections.append(_format_section("Templates", "\n".join(template_list)))

    # Images
    if "images" in parse_data:
        images = parse_data["images"]
        if images:
            image_list = [img if isinstance(img, str) else str(img) for img in images]
            formatted_sections.append(_format_section("Images", "\n".join(image_list)))

    # External links
    if "externallinks" in parse_data:
        external_links = parse_data["externallinks"]
        if external_links:
            link_list = [link if isinstance(link, str) else str(link) for link in external_links]
            formatted_sections.append(_format_section("External Links", "\n".join(link_list)))

    # Sections
    if "sections" in parse_data:
        sections = parse_data["sections"]
        if sections:
            section_list = []
            for section in sections:
                level = section.get("level", "")
                line = section.get("line", "")
                section_list.append(f"Level {level}: {line}")
            formatted_sections.append(_format_section("Sections", "\n".join(section_list)))

    # Language links
    if "langlinks" in parse_data:
        langlinks = parse_data["langlinks"]
        if langlinks:
            lang_list = []
            for link in langlinks:
                lang = link.get("lang", "")
                title = link.get("*", link.get("title", ""))
                lang_list.append(f"{lang}: {title}")
            formatted_sections.append(_format_section("Language Links", "\n".join(lang_list)))

    # Interwiki links
    if "iwlinks" in parse_data:
        iwlinks = parse_data["iwlinks"]
        if iwlinks:
            iw_list = []
            for link in iwlinks:
                prefix = link.get("prefix", "")
                title = link.get("*", link.get("title", ""))
                iw_list.append(f"{prefix}: {title}")
            formatted_sections.append(_format_section("Interwiki Links", "\n".join(iw_list)))

    # Properties
    if "properties" in parse_data:
        properties = parse_data["properties"]
        if properties:
            prop_list = []
            for prop in properties:
                name = prop.get("name", "")
                value = prop.get("*", prop.get("value", ""))
                prop_list.append(f"{name}: {value}")
            formatted_sections.append(_format_section("Properties", "\n".join(prop_list)))

    # Parse warnings
    if "parsewarnings" in parse_data:
        warnings = parse_data["parsewarnings"]
        if warnings:
            warning_list = [warning if isinstance(warning, str) else str(warning) for warning in warnings]
            formatted_sections.append(_format_section("Parse Warnings", "\n".join(warning_list)))

    # Display title
    if "displaytitle" in parse_data:
        display_title = parse_data["displaytitle"]
        formatted_sections.append(_format_section("Display Title", display_title))

    # Combine all sections
    if formatted_sections:
        response_lines.extend(formatted_sections)
    else:
        response_lines.append("No content available in the parsed output.")

    return [types.TextContent(
        type="text",
        text="\n".join(response_lines)
    )]


def _format_section(title: str, content: str) -> str:
    """Format a section with a title and content."""
    if not content:
        return f"## {title}\n(No content)\n"

    # Truncate very long content for readability
    if len(content) > 5000:
        content = content[:5000] + "\n... (content truncated)"

    return f"## {title}\n{content}\n"
