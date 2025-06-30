"""MediaWiki API page operations client."""

import logging
from typing import Any

from .client_auth import MediaWikiAuthClient

logger = logging.getLogger(__name__)


class MediaWikiPageClient:
    """Client for handling MediaWiki page operations."""

    def __init__(self, auth_client: MediaWikiAuthClient):
        self.auth_client = auth_client

    async def edit_page(
        self,
        title: str | None = None,
        pageid: int | None = None,
        text: str | None = None,
        summary: str | None = None,
        section: str | None = None,
        sectiontitle: str | None = None,
        appendtext: str | None = None,
        prependtext: str | None = None,
        minor: bool = False,
        bot: bool = True,
        createonly: bool = False,
        nocreate: bool = False,
        **kwargs: Any
    ) -> dict[str, Any]:
        """
        Edit a MediaWiki page.

        Args:
            title: Title of the page to edit
            pageid: Page ID of the page to edit
            text: New page content
            summary: Edit summary
            section: Section identifier (0 for top, "new" for new section)
            sectiontitle: Title for new section
            appendtext: Text to append to page
            prependtext: Text to prepend to page
            minor: Mark as minor edit
            bot: Mark as bot edit
            createonly: Don't edit if page exists
            nocreate: Don't create if page doesn't exist
            **kwargs: Additional parameters

        Returns:
            API response dictionary
        """
        if not title and not pageid:
            raise ValueError("Either title or pageid must be provided")

        if not self.auth_client.csrf_token:
            await self.auth_client.get_csrf_token()

        if not self.auth_client.csrf_token:
            raise ValueError("Could not obtain CSRF token")

        # Build edit parameters
        edit_data = {
            "action": "edit",
            "format": "json",
            "token": self.auth_client.csrf_token
        }

        # Page identification
        if title:
            edit_data["title"] = title
        if pageid:
            edit_data["pageid"] = str(pageid)

        # Content parameters
        if text is not None:
            edit_data["text"] = text
        if appendtext is not None:
            edit_data["appendtext"] = appendtext
        if prependtext is not None:
            edit_data["prependtext"] = prependtext

        # Section handling
        if section is not None:
            edit_data["section"] = section
        if sectiontitle is not None:
            edit_data["sectiontitle"] = sectiontitle

        # Metadata
        if summary:
            edit_data["summary"] = summary
        if minor:
            edit_data["minor"] = "1"
        if bot:
            edit_data["bot"] = "1"
        if createonly:
            edit_data["createonly"] = "1"
        if nocreate:
            edit_data["nocreate"] = "1"

        # Add any additional parameters
        edit_data.update(kwargs)

        try:
            response = await self.auth_client._make_request("POST", data=edit_data)

            if "edit" in response and response["edit"].get("result") == "Success":
                logger.info(f"Successfully edited page: {title or pageid}")
                edit_result: dict[str, Any] = response["edit"]
                return edit_result
            else:
                logger.error(f"Edit failed: {response}")
                return response

        except Exception as e:
            logger.error(f"Edit request failed: {e}")
            raise

    async def get_page_info(
        self,
        title: str | None = None,
        pageid: int | None = None
    ) -> dict[str, Any]:
        """Get information about a page using the Revisions API with proper parameters."""
        if not title and not pageid:
            raise ValueError("Either title or pageid must be provided")

        params = {
            "action": "query",
            "format": "json",
            "formatversion": "2",
            "prop": "revisions",
            "rvslots": "*",
            "rvprop": "content"
        }

        if title:
            params["titles"] = title
        if pageid:
            params["pageids"] = str(pageid)

        response = await self.auth_client._make_request("GET", params=params)
        return response

    async def get_page_raw(
        self,
        title: str | None = None,
        pageid: int | None = None
    ) -> str:
        """Get raw wikitext content using the raw action (fastest method)."""
        if not title and not pageid:
            raise ValueError("Either title or pageid must be provided")

        params = {
            "action": "raw"
        }

        if title:
            params["title"] = title
        elif pageid:
            params["curid"] = str(pageid)

        # Raw action returns plain text, not JSON
        headers = {
            "User-Agent": self.auth_client.user_agent
        }

        response = await self.auth_client.session.get(self.auth_client.api_url, params=params, headers=headers)
        response.raise_for_status()
        return response.text

    async def get_page_parse(
        self,
        title: str | None = None,
        pageid: int | None = None,
        format_type: str = "wikitext"
    ) -> dict[str, Any]:
        """Get page content using the Parse API (HTML or wikitext)."""
        if not title and not pageid:
            raise ValueError("Either title or pageid must be provided")

        params = {
            "action": "parse",
            "format": "json",
            "formatversion": "2"
        }

        if title:
            params["page"] = title
        elif pageid:
            params["oldid"] = str(pageid)

        if format_type == "html":
            params["prop"] = "text"
        else:
            params["prop"] = "wikitext"

        response = await self.auth_client._make_request("GET", params=params)
        return response

    async def get_page_extracts(
        self,
        title: str | None = None,
        pageid: int | None = None,
        sentences: int | None = None,
        chars: int | None = None,
        plain_text: bool = True
    ) -> dict[str, Any]:
        """Get page extracts using the TextExtracts API."""
        if not title and not pageid:
            raise ValueError("Either title or pageid must be provided")

        params = {
            "action": "query",
            "format": "json",
            "formatversion": "2",
            "prop": "extracts",
            "exlimit": "1"
        }

        if title:
            params["titles"] = title
        elif pageid:
            params["pageids"] = str(pageid)

        if sentences:
            params["exsentences"] = str(sentences)
        elif chars:
            params["exchars"] = str(chars)

        if plain_text:
            params["explaintext"] = "1"

        response = await self.auth_client._make_request("GET", params=params)
        return response

    async def move_page(
        self,
        from_title: str | None = None,
        fromid: int | None = None,
        to: str | None = None,
        reason: str | None = None,
        movetalk: bool = False,
        movesubpages: bool = False,
        noredirect: bool = False,
        watchlist: str = "preferences",
        watchlistexpiry: str | None = None,
        ignorewarnings: bool = False,
        tags: list[str] | None = None,
        **kwargs: Any
    ) -> dict[str, Any]:
        """
        Move a MediaWiki page.

        Args:
            from_title: Title of the page to rename
            fromid: Page ID of the page to rename
            to: Title to rename the page to (required)
            reason: Reason for the rename
            movetalk: Rename the talk page, if it exists
            movesubpages: Rename subpages, if applicable
            noredirect: Don't create a redirect
            watchlist: Watchlist behavior - "nochange", "preferences", "unwatch", "watch"
            watchlistexpiry: Watchlist expiry timestamp
            ignorewarnings: Ignore any warnings
            tags: Change tags to apply to the move log
            **kwargs: Additional parameters

        Returns:
            API response dictionary
        """
        if not from_title and not fromid:
            raise ValueError("Either from_title or fromid must be provided")

        if not to:
            raise ValueError("to parameter is required")

        if not self.auth_client.csrf_token:
            await self.auth_client.get_csrf_token()

        if not self.auth_client.csrf_token:
            raise ValueError("Could not obtain CSRF token")

        # Build move parameters
        move_data = {
            "action": "move",
            "format": "json",
            "token": self.auth_client.csrf_token,
            "to": to
        }

        # Page identification
        if from_title:
            move_data["from"] = from_title
        if fromid:
            move_data["fromid"] = str(fromid)

        # Optional parameters
        if reason:
            move_data["reason"] = reason
        if movetalk:
            move_data["movetalk"] = "1"
        if movesubpages:
            move_data["movesubpages"] = "1"
        if noredirect:
            move_data["noredirect"] = "1"
        if watchlist != "preferences":
            move_data["watchlist"] = watchlist
        if watchlistexpiry:
            move_data["watchlistexpiry"] = watchlistexpiry
        if ignorewarnings:
            move_data["ignorewarnings"] = "1"
        if tags:
            move_data["tags"] = "|".join(tags)

        # Add any additional parameters
        move_data.update(kwargs)

        try:
            response = await self.auth_client._make_request("POST", data=move_data)

            if "move" in response:
                logger.info(f"Successfully moved page: {from_title or fromid} -> {to}")
                move_result: dict[str, Any] = response["move"]
                return move_result
            else:
                logger.error(f"Move failed: {response}")
                return response

        except Exception as e:
            logger.error(f"Move request failed: {e}")
            raise

    async def delete_page(
        self,
        title: str | None = None,
        pageid: int | None = None,
        reason: str | None = None,
        tags: list[str] | None = None,
        deletetalk: bool = False,
        watch: bool | None = None,
        watchlist: str = "preferences",
        watchlistexpiry: str | None = None,
        unwatch: bool | None = None,
        oldimage: str | None = None,
        **kwargs: Any
    ) -> dict[str, Any]:
        """
        Delete a MediaWiki page.

        Args:
            title: Title of the page to delete
            pageid: Page ID of the page to delete
            reason: Reason for the deletion
            tags: Change tags to apply to the deletion log
            deletetalk: Delete the talk page, if it exists
            watch: Add the page to watchlist (deprecated, use watchlist)
            watchlist: Watchlist behavior - "nochange", "preferences", "unwatch", "watch"
            watchlistexpiry: Watchlist expiry timestamp
            unwatch: Remove page from watchlist (deprecated, use watchlist)
            oldimage: Name of old image to delete for files
            **kwargs: Additional parameters

        Returns:
            API response dictionary
        """
        if not title and not pageid:
            raise ValueError("Either title or pageid must be provided")

        if not self.auth_client.csrf_token:
            await self.auth_client.get_csrf_token()

        if not self.auth_client.csrf_token:
            raise ValueError("Could not obtain CSRF token")

        # Build delete parameters
        delete_data = {
            "action": "delete",
            "format": "json",
            "token": self.auth_client.csrf_token
        }

        # Page identification
        if title:
            delete_data["title"] = title
        if pageid:
            delete_data["pageid"] = str(pageid)

        # Optional parameters
        if reason:
            delete_data["reason"] = reason
        if tags:
            delete_data["tags"] = "|".join(tags)
        if deletetalk:
            delete_data["deletetalk"] = "1"
        if oldimage:
            delete_data["oldimage"] = oldimage

        # Watchlist handling (handle deprecated parameters)
        if watch is not None and watch:
            delete_data["watchlist"] = "watch"
        elif unwatch is not None and unwatch:
            delete_data["watchlist"] = "unwatch"
        elif watchlist != "preferences":
            delete_data["watchlist"] = watchlist

        if watchlistexpiry:
            delete_data["watchlistexpiry"] = watchlistexpiry

        # Add any additional parameters
        delete_data.update(kwargs)

        try:
            response = await self.auth_client._make_request("POST", data=delete_data)

            if "delete" in response:
                logger.info(f"Successfully deleted page: {title or pageid}")
                delete_result: dict[str, Any] = response["delete"]
                return delete_result
            else:
                logger.error(f"Delete failed: {response}")
                return response

        except Exception as e:
            logger.error(f"Delete request failed: {e}")
            raise

    async def undelete_page(
        self,
        title: str,
        reason: str | None = None,
        tags: list[str] | None = None,
        timestamps: list[str] | None = None,
        fileids: list[int] | None = None,
        undeletetalk: bool = False,
        watchlist: str = "preferences",
        watchlistexpiry: str | None = None,
        **kwargs: Any
    ) -> dict[str, Any]:
        """
        Undelete (restore) the revisions of a deleted MediaWiki page.

        Args:
            title: Title of the page to undelete (required)
            reason: Reason for restoring
            tags: Change tags to apply to the entry in the deletion log
            timestamps: Timestamps of the revisions to undelete
            fileids: IDs of the file revisions to restore
            undeletetalk: Undelete all revisions of the associated talk page, if any
            watchlist: Watchlist behavior - "nochange", "preferences", "unwatch", "watch"
            watchlistexpiry: Watchlist expiry timestamp
            **kwargs: Additional parameters

        Returns:
            API response dictionary
        """
        if not title:
            raise ValueError("Title must be provided")

        if not self.auth_client.csrf_token:
            await self.auth_client.get_csrf_token()

        if not self.auth_client.csrf_token:
            raise ValueError("Could not obtain CSRF token")

        # Build undelete parameters
        undelete_data = {
            "action": "undelete",
            "format": "json",
            "title": title,
            "token": self.auth_client.csrf_token
        }

        # Optional parameters
        if reason:
            undelete_data["reason"] = reason
        if tags:
            undelete_data["tags"] = "|".join(tags)
        if timestamps:
            undelete_data["timestamps"] = "|".join(timestamps)
        if fileids:
            undelete_data["fileids"] = "|".join(str(fid) for fid in fileids)
        if undeletetalk:
            undelete_data["undeletetalk"] = "1"
        if watchlist != "preferences":
            undelete_data["watchlist"] = watchlist
        if watchlistexpiry:
            undelete_data["watchlistexpiry"] = watchlistexpiry

        # Add any additional parameters
        undelete_data.update(kwargs)

        try:
            response = await self.auth_client._make_request("POST", data=undelete_data)

            if "undelete" in response:
                logger.info(f"Successfully undeleted page: {title}")
                undelete_result: dict[str, Any] = response["undelete"]
                return undelete_result
            else:
                logger.error(f"Undelete failed: {response}")
                return response

        except Exception as e:
            logger.error(f"Undelete request failed: {e}")
            raise
