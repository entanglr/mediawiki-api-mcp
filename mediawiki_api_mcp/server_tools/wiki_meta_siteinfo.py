"""Wiki meta siteinfo tool for MediaWiki API MCP integration."""

import logging
from typing import Callable

from mcp.server.fastmcp import FastMCP
from ..client import MediaWikiClient, MediaWikiConfig

logger = logging.getLogger(__name__)


def register_wiki_meta_siteinfo_tool(mcp: FastMCP, get_config: Callable[[], MediaWikiConfig]) -> None:
    """Register the wiki_meta_siteinfo tool with the MCP server."""

    @mcp.tool()
    async def wiki_meta_siteinfo(
        siprop: list[str] | None = None,
        sifilteriw: str = "",
        sishowalldb: bool = False,
        sinumberingroup: bool = False,
        siinlanguagecode: str = "",
    ) -> str:
        """Get overall site information from MediaWiki.

        Args:
            siprop: Which information to get (options: general, namespaces, namespacealiases,
                    specialpagealiases, magicwords, interwikimap, dbrepllag, statistics, usergroups,
                    autocreatetempuser, clientlibraries, libraries, extensions, fileextensions,
                    rightsinfo, restrictions, languages, languagevariants, skins, extensiontags,
                    functionhooks, showhooks, variables, protocols, defaultoptions, uploaddialog,
                    autopromote, autopromoteonce, copyuploaddomains). Default: ["general"]
            sifilteriw: Return only local or only nonlocal entries of interwiki map ("local" or "!local")
            sishowalldb: List all database servers, not just the one lagging the most
            sinumberingroup: Lists the number of users in user groups
            siinlanguagecode: Language code for localised language names and skin names
        """
        try:
            config = get_config()
            async with MediaWikiClient(config) as client:
                # Import here to avoid circular imports
                from ..handlers import handle_meta_siteinfo

                # Convert FastMCP parameters to handler arguments
                arguments = {
                    "siprop": siprop,
                    "sifilteriw": sifilteriw if sifilteriw else None,
                    "sishowalldb": sishowalldb,
                    "sinumberingroup": sinumberingroup,
                    "siinlanguagecode": siinlanguagecode if siinlanguagecode else None,
                }

                result = await handle_meta_siteinfo(client, arguments)
                # Return the formatted text from the handler
                return result[0].text if result else "No results"
        except Exception as e:
            logger.error(f"Wiki meta siteinfo failed: {e}")
            return f"Error: {str(e)}"
