"""MediaWiki search handlers for MCP server."""

import logging
from collections.abc import Sequence
from typing import Any

import mcp.types as types

from ..client import MediaWikiClient

logger = logging.getLogger(__name__)


async def handle_search(
    client: MediaWikiClient,
    arguments: dict[str, Any]
) -> Sequence[types.TextContent]:
    """Handle wiki_search tool calls with comprehensive search functionality."""
    query = arguments.get("query")

    if not query:
        return [types.TextContent(
            type="text",
            text="Error: Search query is required"
        )]

    # Extract search parameters with defaults
    namespaces = arguments.get("namespaces")
    limit = arguments.get("limit", 10)
    offset = arguments.get("offset", 0)
    what = arguments.get("what", "text")
    info = arguments.get("info")
    prop = arguments.get("prop")
    interwiki = arguments.get("interwiki", False)
    enable_rewrites = arguments.get("enable_rewrites", True)
    srsort = arguments.get("srsort", "relevance")
    qiprofile = arguments.get("qiprofile", "engine_autoselect")

    try:
        result = await client.search_pages(
            search_query=query,
            namespaces=namespaces,
            limit=limit,
            offset=offset,
            what=what,
            info=info,
            prop=prop,
            interwiki=interwiki,
            enable_rewrites=enable_rewrites,
            srsort=srsort,
            qiprofile=qiprofile
        )

        if "query" not in result:
            return [types.TextContent(
                type="text",
                text=f"Unexpected response format: {result}"
            )]

        query_data = result["query"]

        # Format search metadata
        response_text = f"Search Results for: '{query}'\n"
        response_text += "=" * (len(response_text) - 1) + "\n\n"

        # Add search info if available
        if "searchinfo" in query_data:
            search_info = query_data["searchinfo"]
            if "totalhits" in search_info:
                response_text += f"Total hits: {search_info['totalhits']}\n"
            if "suggestion" in search_info:
                response_text += f"Did you mean: {search_info['suggestion']}\n"
            if "rewrittenquery" in search_info:
                response_text += f"Query rewritten to: {search_info['rewrittenquery']}\n"
            response_text += "\n"

        # Process search results
        search_results = query_data.get("search", [])

        if not search_results:
            response_text += "No search results found."
        else:
            response_text += f"Showing {len(search_results)} results"
            if offset > 0:
                response_text += f" (starting from result #{offset + 1})"
            response_text += ":\n\n"

            for i, page in enumerate(search_results, 1):
                result_num = offset + i
                response_text += f"{result_num}. **{page.get('title', 'Unknown Title')}**\n"

                # Add page ID and namespace info
                if 'pageid' in page:
                    response_text += f"   Page ID: {page['pageid']}"
                if 'ns' in page:
                    response_text += f" | Namespace: {page['ns']}"
                response_text += "\n"

                # Add size and word count if available
                metadata = []
                if 'size' in page:
                    metadata.append(f"Size: {page['size']} bytes")
                if 'wordcount' in page:
                    metadata.append(f"Words: {page['wordcount']}")
                if 'timestamp' in page:
                    metadata.append(f"Last edited: {page['timestamp']}")

                if metadata:
                    response_text += f"   {' | '.join(metadata)}\n"

                # Add snippet if available
                if 'snippet' in page and page['snippet']:
                    # Clean up snippet HTML tags for better readability
                    snippet = page['snippet'].replace('<span class="searchmatch">', '**').replace('</span>', '**')
                    response_text += f"   Preview: {snippet}\n"

                # Add title snippet if different from title
                if 'titlesnippet' in page and page['titlesnippet'] != page.get('title'):
                    title_snippet = page['titlesnippet'].replace('<span class="searchmatch">', '**').replace('</span>', '**')
                    response_text += f"   Title match: {title_snippet}\n"

                # Add redirect info if available
                if 'redirecttitle' in page:
                    response_text += f"   Redirected from: {page['redirecttitle']}\n"
                if 'redirectsnippet' in page:
                    redirect_snippet = page['redirectsnippet'].replace('<span class="searchmatch">', '**').replace('</span>', '**')
                    response_text += f"   Redirect match: {redirect_snippet}\n"

                # Add section info if available
                if 'sectiontitle' in page:
                    response_text += f"   Section: {page['sectiontitle']}\n"
                if 'sectionsnippet' in page:
                    section_snippet = page['sectionsnippet'].replace('<span class="searchmatch">', '**').replace('</span>', '**')
                    # Remove "Section " prefix if present to avoid duplication
                    if section_snippet.startswith("Section "):
                        section_snippet = section_snippet[8:]
                    response_text += f"   Section match: {section_snippet}\n"

                # Add category info if available
                if 'categorysnippet' in page:
                    category_snippet = page['categorysnippet'].replace('<span class="searchmatch">', '**').replace('</span>', '**')
                    response_text += f"   Category: {category_snippet}\n"

                # Add file match indicator
                if 'isfilematch' in page and page['isfilematch']:
                    response_text += "   File content match: Yes\n"

                response_text += "\n"

        # Add pagination info if applicable
        if "continue" in result:
            continue_info = result["continue"]
            if "sroffset" in continue_info:
                next_offset = continue_info["sroffset"]
                response_text += f"\nMore results available. Use offset={next_offset} to see the next page."

        return [types.TextContent(
            type="text",
            text=response_text
        )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error performing search: {str(e)}"
        )]
