"""MediaWiki page comparison handlers for MCP server."""

import logging
from collections.abc import Sequence
from typing import Any

import mcp.types as types

from ..client import MediaWikiClient

logger = logging.getLogger(__name__)


async def handle_compare_page(
    client: MediaWikiClient,
    arguments: dict[str, Any]
) -> Sequence[types.TextContent]:
    """Handle wiki_page_compare tool calls with support for MediaWiki Compare API."""
    # Extract basic comparison parameters
    fromtitle = arguments.get("fromtitle")
    fromid = arguments.get("fromid")
    fromrev = arguments.get("fromrev")
    totitle = arguments.get("totitle")
    toid = arguments.get("toid")
    torev = arguments.get("torev")

    # Extract slot and output parameters
    fromslots = arguments.get("fromslots")
    toslots = arguments.get("toslots")
    prop = arguments.get("prop")
    difftype = arguments.get("difftype")

    # Extract legacy parameters
    fromtext = arguments.get("fromtext")
    totext = arguments.get("totext")
    fromcontentformat = arguments.get("fromcontentformat")
    tocontentformat = arguments.get("tocontentformat")
    fromcontentmodel = arguments.get("fromcontentmodel")
    tocontentmodel = arguments.get("tocontentmodel")
    tosection = arguments.get("tosection")

    # Extract slot-specific parameters
    slot_params = {}
    for key, value in arguments.items():
        if (key.startswith(("fromtext-", "totext-", "fromcontentformat-", "tocontentformat-",
                           "fromcontentmodel-", "tocontentmodel-", "fromsection-", "tosection-",
                           "frompst-", "topst-")) and value is not None):
            slot_params[key] = value

    try:
        result = await client.compare_page(
            fromtitle=fromtitle,
            fromid=fromid,
            fromrev=fromrev,
            totitle=totitle,
            toid=toid,
            torev=torev,
            fromslots=fromslots,
            toslots=toslots,
            prop=prop,
            difftype=difftype,
            fromtext=fromtext,
            totext=totext,
            fromcontentformat=fromcontentformat,
            tocontentformat=tocontentformat,
            fromcontentmodel=fromcontentmodel,
            tocontentmodel=tocontentmodel,
            tosection=tosection,
            slot_params=slot_params if slot_params else None
        )

        if "compare" not in result:
            return [types.TextContent(
                type="text",
                text="Error: Unexpected response format from MediaWiki Compare API"
            )]

        return await _format_compare_result(result, arguments)

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error comparing pages: {str(e)}"
        )]


async def _format_compare_result(
    result: dict[str, Any],
    arguments: dict[str, Any]
) -> Sequence[types.TextContent]:
    """Format the comparison result for display."""
    compare_data = result["compare"]

    # Build descriptive output
    output_lines = ["# Page Comparison Result\n"]

    # Source information
    from_info = []
    if "fromtitle" in compare_data:
        from_info.append(f"Title: {compare_data['fromtitle']}")
    if "fromid" in compare_data:
        from_info.append(f"ID: {compare_data['fromid']}")
    if "fromrevid" in compare_data:
        from_info.append(f"Revision: {compare_data['fromrevid']}")
    if "fromns" in compare_data:
        from_info.append(f"Namespace: {compare_data['fromns']}")

    output_lines.append(f"**From:** {', '.join(from_info) if from_info else 'Unknown'}")

    # Target information
    to_info = []
    if "totitle" in compare_data:
        to_info.append(f"Title: {compare_data['totitle']}")
    if "toid" in compare_data:
        to_info.append(f"ID: {compare_data['toid']}")
    if "torevid" in compare_data:
        to_info.append(f"Revision: {compare_data['torevid']}")
    if "tons" in compare_data:
        to_info.append(f"Namespace: {compare_data['tons']}")

    output_lines.append(f"**To:** {', '.join(to_info) if to_info else 'Unknown'}")
    output_lines.append("")

    # Add diff format information
    difftype = arguments.get("difftype", "default")
    output_lines.append(f"**Diff format:** {difftype}")
    output_lines.append("")

    # Add diff content if available
    if "body" in compare_data:
        output_lines.append("## Comparison Output\n")
        output_lines.append(compare_data["body"])
    elif "*" in compare_data:
        # Handle legacy format
        output_lines.append("## Comparison Output\n")
        output_lines.append(compare_data["*"])
    else:
        # Check for other possible diff fields
        diff_fields = ["diff", "text", "html"]
        for field in diff_fields:
            if field in compare_data:
                output_lines.append(f"## {field.title()} Comparison\n")
                output_lines.append(str(compare_data[field]))
                break
        else:
            output_lines.append("## Raw API Response\n")
            output_lines.append(str(compare_data))

    # Add metadata if available
    metadata = []
    if "fromsize" in compare_data:
        metadata.append(f"From size: {compare_data['fromsize']} bytes")
    if "tosize" in compare_data:
        metadata.append(f"To size: {compare_data['tosize']} bytes")

    if metadata:
        output_lines.append("\n## Metadata\n")
        output_lines.extend(metadata)

    formatted_output = "\n".join(output_lines)

    return [types.TextContent(
        type="text",
        text=formatted_output
    )]
