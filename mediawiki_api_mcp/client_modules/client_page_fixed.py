"""Fixed version of the parse_page method with corrected parameter handling."""

from typing import Any


async def parse_page_fixed(
    auth_client,
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
    Fixed parse_page method with proper parameter handling and error handling.
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
    # Priority: oldid > pageid > page > title (for existing page) > text > summary
    if oldid:
        # Parse specific revision - use oldid (highest priority)
        params["oldid"] = str(oldid)
    elif pageid:
        # Parse existing page by ID - use pageid (overrides page parameter)
        params["pageid"] = str(pageid)
    elif page:
        # Parse existing page by title - use page parameter
        params["page"] = page
    elif title and not text and not summary:
        # Parse existing page by title when no other content provided - use page parameter
        # This fixes the title vs page inconsistency
        params["page"] = title
    elif text:
        # Parse arbitrary text - use text parameter
        params["text"] = text
        # Optionally specify which page the text belongs to for context
        if title:
            params["title"] = title
    elif summary:
        # Parse summary only - requires empty prop parameter
        params["summary"] = summary
        # When parsing summary only, prop should be empty according to MediaWiki API docs
        if prop is None:
            prop = []
    elif title:
        # Fallback case - treat title as page to parse
        params["page"] = title

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

    if prop:
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

    response = await auth_client._make_request("GET", params=params)
    return response
