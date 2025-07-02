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

    async def parse_page(
        self,
        title: str | None = None,
        pageid: int | None = None,
        oldid: int | None = None,
        text: str | None = None,
        revid: int | None = None,
        summary: str | None = None,
        page: str | None = None,
        redirects: bool = False,
        prop: list[str] | None = None,
        wrapoutputclass: str | None = None,
        usearticle: bool = False,
        parsoid: bool = False,
        pst: bool = False,
        onlypst: bool = False,
        section: str | None = None,
        sectiontitle: str | None = None,
        disablelimitreport: bool = False,
        disableeditsection: bool = False,
        disablestylededuplication: bool = False,
        showstrategykeys: bool = False,
        preview: bool = False,
        sectionpreview: bool = False,
        disabletoc: bool = False,
        useskin: str | None = None,
        contentformat: str | None = None,
        contentmodel: str | None = None,
        mobileformat: bool = False,
        templatesandboxprefix: list[str] | None = None,
        templatesandboxtitle: str | None = None,
        templatesandboxtext: str | None = None,
        templatesandboxcontentmodel: str | None = None,
        templatesandboxcontentformat: str | None = None,
        **kwargs: Any
    ) -> dict[str, Any]:
        """
        Parse content and return parser output using the MediaWiki Parse API.

        This is a comprehensive implementation of the Parse API that supports
        all documented parameters for parsing wikitext content.

        Args:
            title: Title of page the text belongs to
            pageid: Parse the content of this page (overrides page)
            oldid: Parse the content of this revision (overrides page and pageid)
            text: Text to parse (use title or contentmodel to control content model)
            revid: Revision ID for {{REVISIONID}} and similar variables
            summary: Summary to parse
            page: Parse the content of this page (cannot be used with text and title)
            redirects: If page or pageid is set to a redirect, resolve it
            prop: Which pieces of information to get (list of property names)
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
            templatesandboxprefix: Template sandbox prefix
            templatesandboxtitle: Parse page using templatesandboxtext
            templatesandboxtext: Parse page using this content
            templatesandboxcontentmodel: Content model of templatesandboxtext
            templatesandboxcontentformat: Content format of templatesandboxtext
            **kwargs: Additional parameters

        Returns:
            API response dictionary containing parsed content
        """
        params = {
            "action": "parse",
            "format": "json",
            "formatversion": "2"
        }

        # Page/content identification - validate mutual exclusivity and set correct parameters
        identification_params = [title, pageid, oldid, text, page, summary]
        provided_params = [p for p in identification_params if p is not None]

        if len(provided_params) == 0:
            raise ValueError("Must provide one of: title, pageid, oldid, text, page, or summary")

        # Set page/content identification parameters according to MediaWiki Parse API rules
        # Priority: oldid > pageid > page > title > text > summary
        if oldid:
            # Parse specific revision - use oldid (highest priority)
            params["oldid"] = str(oldid)
        elif pageid:
            # Parse existing page by ID - use pageid (overrides page parameter)
            params["pageid"] = str(pageid)
        elif page:
            # Parse existing page by title - use page parameter
            params["page"] = page
        elif title:
            # Parse existing page by title - always use page parameter for consistency
            # This fixes the title vs page parameter inconsistency bug
            params["page"] = title
        elif text:
            # Parse arbitrary text - use text parameter
            params["text"] = text
        elif summary:
            # Parse summary only - use summary parameter with empty prop
            params["summary"] = summary
            # For summary parsing, prop should be empty according to API docs
            if prop is None:
                prop = []

        if revid:
            params["revid"] = str(revid)

        # Content control parameters
        if redirects:
            params["redirects"] = "1"

        # Default prop if not specified - use conservative defaults
        if prop is None:
            # Start with basic properties that are supported by most MediaWiki installations
            prop = ["text", "categories", "links", "sections", "revid"]

            # Add additional properties if specific functionality is requested
            if not (text or summary):  # Only for existing pages, not arbitrary text parsing
                prop.extend(["displaytitle", "parsewarnings"])

            # Add template and image info for existing pages
            if title or pageid or oldid or page:
                prop.extend(["templates", "images", "externallinks"])

            # Add advanced properties only when explicitly parsing existing pages
            if (title or pageid or oldid or page) and not pst and not onlypst:
                prop.extend(["langlinks", "iwlinks", "properties"])

        if prop is not None:
            params["prop"] = "|".join(prop)

        # Output formatting parameters
        if wrapoutputclass:
            params["wrapoutputclass"] = wrapoutputclass
        if usearticle:
            params["usearticle"] = "1"
        if parsoid:
            params["parsoid"] = "1"
        if pst:
            params["pst"] = "1"
        if onlypst:
            params["onlypst"] = "1"

        # Section parameters - validate section parameter
        if section is not None:
            # Convert section to string if it's an integer
            section_str = str(section)
            # Ensure section is a valid identifier (number, 'new', or 'T-' prefix for template sections)
            if section_str == "new" or section_str.isdigit() or section_str.startswith("T-"):
                params["section"] = section_str
            else:
                raise ValueError("Section parameter must be a number, 'new', or 'T-' prefixed template section")
        if sectiontitle:
            params["sectiontitle"] = sectiontitle

        # Output control parameters
        if disablelimitreport:
            params["disablelimitreport"] = "1"
        if disableeditsection:
            params["disableeditsection"] = "1"
        if disablestylededuplication:
            params["disablestylededuplication"] = "1"
        if showstrategykeys:
            params["showstrategykeys"] = "1"
        if preview:
            params["preview"] = "1"
        if sectionpreview:
            params["sectionpreview"] = "1"
        if disabletoc:
            params["disabletoc"] = "1"

        # Rendering parameters
        if useskin:
            params["useskin"] = useskin
        if mobileformat:
            params["mobileformat"] = "1"

        # Content model parameters
        if contentformat:
            params["contentformat"] = contentformat
        if contentmodel:
            params["contentmodel"] = contentmodel

        # Template sandbox parameters
        if templatesandboxprefix:
            params["templatesandboxprefix"] = "|".join(templatesandboxprefix)
        if templatesandboxtitle:
            params["templatesandboxtitle"] = templatesandboxtitle
        if templatesandboxtext:
            params["templatesandboxtext"] = templatesandboxtext
        if templatesandboxcontentmodel:
            params["templatesandboxcontentmodel"] = templatesandboxcontentmodel
        if templatesandboxcontentformat:
            params["templatesandboxcontentformat"] = templatesandboxcontentformat

        # Add any additional parameters
        params.update(kwargs)

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

    async def compare_pages(
        self,
        fromtitle: str | None = None,
        fromid: int | None = None,
        fromrev: int | None = None,
        fromslots: list[str] | None = None,
        frompst: bool = False,
        totitle: str | None = None,
        toid: int | None = None,
        torev: int | None = None,
        torelative: str | None = None,
        toslots: list[str] | None = None,
        topst: bool = False,
        prop: list[str] | None = None,
        slots: list[str] | None = None,
        difftype: str = "table",
        **kwargs: Any
    ) -> dict[str, Any]:
        """
        Get the difference between two pages using the MediaWiki Compare API.

        Args:
            fromtitle: First title to compare
            fromid: First page ID to compare
            fromrev: First revision to compare
            fromslots: Override content of the from revision (specify slots)
            frompst: Do a pre-save transform on fromtext-{slot}
            totitle: Second title to compare
            toid: Second page ID to compare
            torev: Second revision to compare
            torelative: Use a revision relative to the from revision ('cur', 'next', 'prev')
            toslots: Override content of the to revision (specify slots)
            topst: Do a pre-save transform on totext
            prop: Which pieces of information to get
            slots: Return individual diffs for these slots
            difftype: Return comparison formatted as 'inline', 'table', or 'unified'
            **kwargs: Additional parameters including templated slot parameters

        Returns:
            API response dictionary containing comparison results
        """
        params = {
            "action": "compare",
            "format": "json",
            "formatversion": "2"
        }

        # From parameters
        if fromtitle:
            params["fromtitle"] = fromtitle
        if fromid:
            params["fromid"] = str(fromid)
        if fromrev:
            params["fromrev"] = str(fromrev)
        if fromslots:
            params["fromslots"] = "|".join(fromslots)
        if frompst:
            params["frompst"] = "1"

        # To parameters
        if totitle:
            params["totitle"] = totitle
        if toid:
            params["toid"] = str(toid)
        if torev:
            params["torev"] = str(torev)
        if torelative:
            params["torelative"] = torelative
        if toslots:
            params["toslots"] = "|".join(toslots)
        if topst:
            params["topst"] = "1"

        # Output control parameters
        if prop:
            params["prop"] = "|".join(prop)
        else:
            # Default properties
            params["prop"] = "diff|ids|title"

        if slots:
            if slots == ["*"]:
                params["slots"] = "*"
            else:
                params["slots"] = "|".join(slots)

        if difftype:
            params["difftype"] = difftype

        # Add any additional parameters (including templated slot parameters)
        params.update(kwargs)

        response = await self.auth_client._make_request("GET", params=params)
        return response
