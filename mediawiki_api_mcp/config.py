"""Configuration for MediaWiki API MCP integration."""

from pydantic import BaseModel


class MediaWikiConfig(BaseModel):
    """Configuration for MediaWiki API connection."""
    api_url: str
    username: str
    password: str
    user_agent: str = "MediaWiki-MCP-Bot/1.0"
