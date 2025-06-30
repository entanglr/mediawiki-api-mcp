"""MediaWiki API authentication client."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class MediaWikiAuthClient:
    """Client for handling MediaWiki authentication and base HTTP operations."""

    def __init__(self, api_url: str, username: str, password: str, user_agent: str):
        self.api_url = api_url
        self.username = username
        self.password = password
        self.user_agent = user_agent
        self.session = httpx.AsyncClient()
        self.csrf_token: str | None = None
        self.logged_in = False

    async def __aenter__(self) -> "MediaWikiAuthClient":
        """Async context manager entry."""
        await self.login()
        return self

    async def __aexit__(self, exc_type: type | None, exc_val: BaseException | None, exc_tb: object | None) -> None:
        """Async context manager exit."""
        await self.session.aclose()

    async def _make_request(
        self,
        method: str = "GET",
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Make a request to the MediaWiki API."""
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json"
        }

        if method == "GET":
            response = await self.session.get(self.api_url, params=params, headers=headers)
        else:
            response = await self.session.post(self.api_url, data=data, headers=headers)

        response.raise_for_status()
        json_response: dict[str, Any] = response.json()
        return json_response

    async def login(self) -> bool:
        """Authenticate with MediaWiki using bot credentials."""
        try:
            # Step 1: Get login token
            login_token_params = {
                "action": "query",
                "meta": "tokens",
                "type": "login",
                "format": "json"
            }

            response = await self._make_request("GET", params=login_token_params)
            login_token = response["query"]["tokens"]["logintoken"]

            # Step 2: Login with credentials
            login_data = {
                "action": "login",
                "lgname": self.username,
                "lgpassword": self.password,
                "lgtoken": login_token,
                "format": "json"
            }

            login_response = await self._make_request("POST", data=login_data)

            if login_response.get("login", {}).get("result") == "Success":
                self.logged_in = True
                logger.info("Successfully logged in to MediaWiki")
                return True
            else:
                logger.error(f"Login failed: {login_response}")
                return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    async def get_csrf_token(self) -> str | None:
        """Get CSRF token for editing operations."""
        if not self.logged_in:
            await self.login()

        try:
            params = {
                "action": "query",
                "meta": "tokens",
                "format": "json"
            }

            response = await self._make_request("GET", params=params)
            self.csrf_token = response["query"]["tokens"]["csrftoken"]
            return self.csrf_token

        except Exception as e:
            logger.error(f"Failed to get CSRF token: {e}")
            return None
