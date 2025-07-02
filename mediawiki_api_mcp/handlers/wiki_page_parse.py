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

    # Special handling for summary-only parsing
    if summary and not any([title, pageid, oldid, text, page]):
        # Summary-only parsing requires empty prop parameter according to API docs
        if prop is None:
            prop = []
        logger.debug(f"Summary-only parsing requested: {summary}")

    # Convert prop to list if it's a string
    if prop and isinstance(prop, str):
        prop = [p.strip() for p in prop.split("|") if p.strip()]

    # Convert templatesandboxprefix to list if it's a string
    if templatesandboxprefix and isinstance(templatesandboxprefix, str):
        templatesandboxprefix = [p.strip() for p in templatesandboxprefix.split("|") if p.strip()]

    # Convert title parameter to page parameter for consistency with MediaWiki API
    # The Parse API primarily uses 'page' parameter, not 'title'
    if title and not page:
        page = title
        title = None

    try:
        # Track if this is a summary-only parsing request for fallback handling
        is_summary_only = summary and not any([title, pageid, oldid, text, page])

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

        # If this was a summary-only parsing request and we got minimal content,
        # try a fallback approach by parsing the summary as regular text
        if is_summary_only and "parse" in result:
            parse_data = result["parse"]
            if "text" in parse_data:
                text_content = parse_data["text"]
                if isinstance(text_content, dict) and "*" in text_content:
                    text_content = text_content["*"]

                # Check for minimal content (empty or very minimal parser output)
                if _is_minimal_content(text_content):
                    logger.warning(f"Summary parsing returned minimal content, attempting fallback for: {summary}")

                    # Try parsing the summary as regular text instead
                    try:
                        fallback_result = await client.parse_page(
                            text=summary,
                            contentmodel="wikitext",
                            prop=["text", "categories", "links", "templates", "parsewarnings"],
                            disablelimitreport=disablelimitreport,
                            disableeditsection=disableeditsection
                        )

                        if "parse" in fallback_result:
                            fallback_parse = fallback_result["parse"]
                            if "text" in fallback_parse:
                                fallback_text = fallback_parse["text"]
                                if isinstance(fallback_text, dict) and "*" in fallback_text:
                                    fallback_text = fallback_text["*"]

                                # If fallback has better content, use it with a note
                                if not _is_minimal_content(fallback_text):
                                    logger.info("Fallback summary parsing succeeded, using text parsing approach")
                                    # Update the result with fallback data but preserve original structure
                                    parse_data["text"] = fallback_parse["text"]
                                    # Add other useful properties from fallback if available
                                    for prop_name in ["categories", "links", "templates", "parsewarnings"]:
                                        if prop_name in fallback_parse:
                                            parse_data[prop_name] = fallback_parse[prop_name]
                                    # Add a note about the fallback
                                    if "parsewarnings" not in parse_data:
                                        parse_data["parsewarnings"] = []
                                    parse_data["parsewarnings"].append("Note: Used text parsing fallback due to summary parsing issue")
                    except Exception as fallback_error:
                        logger.warning(f"Fallback summary parsing also failed: {fallback_error}")
                        # Continue with original result

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
            # Enhanced error reporting for debugging
            response_keys = list(result.keys())

            # Create detailed error message based on response content
            error_details = []
            error_details.append(f"Response keys: {response_keys}")

            # Check for common error patterns and provide specific guidance
            if "query" in result:
                error_details.append("Note: Received 'query' response - this indicates the wrong API endpoint was used")
                error_details.append("The Parse API should return a 'parse' key, not 'query'")

                # Check for missing pages in query response
                if isinstance(result.get("query", {}).get("pages", {}), dict):
                    pages = result["query"]["pages"]
                    missing_pages = [page for page in pages.values() if page.get("missing", False)]
                    if missing_pages:
                        error_details.append(f"Note: {len(missing_pages)} page(s) marked as missing in query response")

            elif "missing" in result:
                error_details.append("Note: Page is marked as missing in the response")

            elif "badtitle" in str(result).lower():
                error_details.append("Note: Response suggests the page title may be invalid")

            elif any(key in result for key in ["nosuchsection", "invalidsection"]):
                error_details.append("Note: The specified section does not exist or is invalid")

            elif "invalidparammix" in str(result).lower():
                error_details.append("Note: Invalid parameter combination detected")
                error_details.append("Check that conflicting parameters (page/title/text/oldid) are not used together")

            # Add parameter information for debugging
            used_params = []
            for param in ["title", "pageid", "oldid", "text", "page", "summary"]:
                value = arguments.get(param)
                if value:
                    used_params.append(f"{param}={repr(value)}")
            if used_params:
                error_details.append(f"Used parameters: {', '.join(used_params)}")

            # Add full response for debugging in case of unknown errors
            if len(str(result)) < 500:  # Only include full response if it's not too long
                error_details.append(f"Full response: {result}")

            error_message = "Error: Unexpected response format from Parse API.\n" + "\n".join(error_details)

            return [types.TextContent(
                type="text",
                text=error_message
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
            # Check if it's just an empty div (common issue) or if fallback was used
            is_minimal = _is_minimal_content(text_content)
            if is_minimal:
                # This looks like minimal content - add warning
                formatted_sections.append(_format_section("Parsed HTML",
                    f"WARNING: Content appears minimal. This may indicate a summary parsing issue.\n\n{text_content}"))
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


def _is_minimal_content(content: str) -> bool:
    """
    Check if content appears to be minimal/empty, indicating a parsing issue.

    This detects cases where the MediaWiki API returns nearly empty content,
    which often indicates that the summary parsing didn't work properly.
    """
    if not content or len(content.strip()) == 0:
        return True

    # Check for common minimal content patterns
    content_lower = content.lower().strip()

    # Empty parser wrapper divs with minimal content
    if ('<div class="mw-' in content_lower and
        content_lower.count('<') <= 3 and
        len(content.strip()) < 200):
        return True

    # Just whitespace or basic HTML structure
    if content_lower in ['<p></p>', '<div></div>', ''] or content_lower.isspace():
        return True

    # Check for content that's basically just a parser wrapper with no actual content
    # Remove common wrapper patterns and see if there's actual content left
    import re
    # Remove parser wrapper divs
    cleaned = re.sub(r'<div[^>]*class="[^"]*mw-[^"]*"[^>]*>', '', content)
    cleaned = re.sub(r'</div>', '', cleaned)
    # Remove empty paragraphs and whitespace
    cleaned = re.sub(r'<p[^>]*></p>', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # If after removing wrappers there's very little content, it's likely minimal
    return len(cleaned) < 10


def _format_section(title: str, content: str) -> str:
    """Format a section with a title and content."""
    if not content:
        return f"## {title}\n(No content)\n"

    # Truncate very long content for readability
    if len(content) > 5000:
        content = content[:5000] + "\n... (content truncated)"

    return f"## {title}\n{content}\n"
