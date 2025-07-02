"""MediaWiki page comparison handlers for MCP server."""

import logging
from collections.abc import Sequence
from typing import Any

import mcp.types as types

from ..client import MediaWikiClient

logger = logging.getLogger(__name__)


async def handle_compare_pages(
    client: MediaWikiClient,
    arguments: dict[str, Any]
) -> Sequence[types.TextContent]:
    """Handle wiki_page_compare tool calls to compare two pages or revisions."""
    # Extract from parameters
    fromtitle = arguments.get("fromtitle")
    fromid = arguments.get("fromid")
    fromrev = arguments.get("fromrev")
    fromslots = arguments.get("fromslots")
    frompst = arguments.get("frompst", False)

    # Extract to parameters
    totitle = arguments.get("totitle")
    toid = arguments.get("toid")
    torev = arguments.get("torev")
    torelative = arguments.get("torelative")
    toslots = arguments.get("toslots")
    topst = arguments.get("topst", False)

    # Extract output parameters
    prop = arguments.get("prop")
    slots = arguments.get("slots")
    difftype = arguments.get("difftype", "table")

    # Validate that we have valid from and to specifications
    from_specified = bool(fromtitle or fromid or fromrev)
    to_specified = bool(totitle or toid or torev or torelative)

    if not from_specified:
        return [types.TextContent(
            type="text",
            text="Error: Must specify at least one 'from' parameter (fromtitle, fromid, or fromrev)"
        )]

    if not to_specified:
        return [types.TextContent(
            type="text",
            text="Error: Must specify at least one 'to' parameter (totitle, toid, torev, or torelative)"
        )]

    try:
        # Prepare parameters for client call
        kwargs = {}

        # Handle templated slot parameters
        # Extract any fromtext-{slot}, fromsection-{slot}, fromcontentmodel-{slot}, fromcontentformat-{slot}
        # and totext-{slot}, tosection-{slot}, tocontentmodel-{slot}, tocontentformat-{slot}
        for key, value in arguments.items():
            if (key.startswith(("fromtext-", "fromsection-", "fromcontentmodel-", "fromcontentformat-",
                                "totext-", "tosection-", "tocontentmodel-", "tocontentformat-")) and
                value is not None):
                kwargs[key] = value

        # Convert list parameters to lists
        if isinstance(fromslots, str):
            fromslots = [s.strip() for s in fromslots.split("|") if s.strip()]
        if isinstance(toslots, str):
            toslots = [s.strip() for s in toslots.split("|") if s.strip()]
        if isinstance(prop, str):
            prop = [s.strip() for s in prop.split("|") if s.strip()]
        if isinstance(slots, str):
            if slots == "*":
                slots = ["*"]
            else:
                slots = [s.strip() for s in slots.split("|") if s.strip()]

        result = await client.compare_pages(
            fromtitle=fromtitle,
            fromid=fromid,
            fromrev=fromrev,
            fromslots=fromslots,
            frompst=frompst,
            totitle=totitle,
            toid=toid,
            torev=torev,
            torelative=torelative,
            toslots=toslots,
            topst=topst,
            prop=prop,
            slots=slots,
            difftype=difftype,
            **kwargs
        )

        if "compare" not in result:
            return [types.TextContent(
                type="text",
                text=f"Error: Unexpected response format from MediaWiki Compare API: {result}"
            )]

        compare_data = result["compare"]

        # Format the comparison results
        output_lines = []

        # Basic page information
        if "fromtitle" in compare_data and "totitle" in compare_data:
            output_lines.append(f"Comparing: '{compare_data['fromtitle']}' → '{compare_data['totitle']}'")
        elif "fromid" in compare_data and "toid" in compare_data:
            output_lines.append(f"Comparing: Page ID {compare_data['fromid']} → Page ID {compare_data['toid']}")

        # Revision information
        if "fromrevid" in compare_data and "torevid" in compare_data:
            output_lines.append(f"Revisions: {compare_data['fromrevid']} → {compare_data['torevid']}")

        # Size information
        if "diffsize" in compare_data:
            output_lines.append(f"Diff size: {compare_data['diffsize']} bytes")

        # Timestamp information
        if "fromtimestamp" in compare_data and "totimestamp" in compare_data:
            output_lines.append(f"From timestamp: {compare_data['fromtimestamp']}")
            output_lines.append(f"To timestamp: {compare_data['totimestamp']}")

        # User information
        if "fromuser" in compare_data and "touser" in compare_data:
            output_lines.append(f"From user: {compare_data['fromuser']}")
            output_lines.append(f"To user: {compare_data['touser']}")

        # Comment information
        if "fromcomment" in compare_data and "tocomment" in compare_data:
            output_lines.append(f"From comment: {compare_data['fromcomment']}")
            output_lines.append(f"To comment: {compare_data['tocomment']}")

        output_lines.append("")  # Empty line before diff

        # Diff content
        if "diff" in compare_data:
            if compare_data["diff"]:
                output_lines.append("Diff HTML:")
                output_lines.append(compare_data["diff"])
            else:
                output_lines.append("No differences found between the compared revisions.")

        # Individual slot diffs if requested
        if "slots" in compare_data:
            output_lines.append("\nSlot-specific diffs:")
            for slot_name, slot_diff in compare_data["slots"].items():
                output_lines.append(f"\nSlot '{slot_name}':")
                if slot_diff.get("diff"):
                    output_lines.append(slot_diff["diff"])
                else:
                    output_lines.append("No differences in this slot.")

        return [types.TextContent(
            type="text",
            text="\n".join(output_lines)
        )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error comparing pages: {str(e)}"
        )]
