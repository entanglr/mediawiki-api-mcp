"""MediaWiki API meta operations client."""

import logging
from typing import Any

from .client_auth import MediaWikiAuthClient

logger = logging.getLogger(__name__)


class MediaWikiMetaClient:
    """Client for handling MediaWiki meta operations."""

    def __init__(self, auth_client: MediaWikiAuthClient):
        self.auth_client = auth_client

    async def get_siteinfo(
        self,
        siprop: list[str] | None = None,
        sifilteriw: str | None = None,
        sishowalldb: bool = False,
        sinumberingroup: bool = False,
        siinlanguagecode: str | None = None,
        **kwargs: Any
    ) -> dict[str, Any]:
        """
        Get overall site information from MediaWiki.

        Args:
            siprop: Which information to get (default: ["general"])
            sifilteriw: Return only local or only nonlocal entries of interwiki map ("local" or "!local")
            sishowalldb: List all database servers, not just the one lagging the most
            sinumberingroup: Lists the number of users in user groups
            siinlanguagecode: Language code for localised language names and skin names
            **kwargs: Additional parameters

        Returns:
            API response dictionary containing site information
        """
        # Build siteinfo parameters
        params = {
            "action": "query",
            "meta": "siteinfo",
            "format": "json"
        }

        # Set which information to get (default to general)
        if siprop is None:
            siprop = ["general"]

        # Validate siprop values
        valid_props = [
            "general", "namespaces", "namespacealiases", "specialpagealiases",
            "magicwords", "interwikimap", "dbrepllag", "statistics", "usergroups",
            "autocreatetempuser", "clientlibraries", "libraries", "extensions",
            "fileextensions", "rightsinfo", "restrictions", "languages",
            "languagevariants", "skins", "extensiontags", "functionhooks",
            "showhooks", "variables", "protocols", "defaultoptions",
            "uploaddialog", "autopromote", "autopromoteonce", "copyuploaddomains"
        ]

        filtered_props = [p for p in siprop if p in valid_props]
        if filtered_props:
            params["siprop"] = "|".join(filtered_props)

        # Set interwiki filter
        if sifilteriw and sifilteriw in ["local", "!local"]:
            params["sifilteriw"] = sifilteriw

        # Set boolean parameters
        if sishowalldb:
            params["sishowalldb"] = "1"

        if sinumberingroup:
            params["sinumberingroup"] = "1"

        # Set language code
        if siinlanguagecode:
            params["siinlanguagecode"] = siinlanguagecode

        # Add any additional parameters
        params.update(kwargs)

        try:
            response = await self.auth_client._make_request("GET", params=params)
            logger.info("Siteinfo query completed successfully")
            return response

        except Exception as e:
            logger.error(f"Siteinfo request failed: {e}")
            raise
