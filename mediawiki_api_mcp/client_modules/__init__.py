"""MediaWiki API client modules."""

from .client_auth import MediaWikiAuthClient
from .client_meta import MediaWikiMetaClient
from .client_page import MediaWikiPageClient
from .client_search import MediaWikiSearchClient

__all__ = [
    "MediaWikiAuthClient",
    "MediaWikiMetaClient",
    "MediaWikiPageClient",
    "MediaWikiSearchClient",
]
