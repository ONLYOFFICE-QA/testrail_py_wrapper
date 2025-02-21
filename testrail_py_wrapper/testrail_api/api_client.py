# -*- coding: utf-8 -*-
import aiohttp

from typing import Optional, Dict, Any

class APIClient:
    """
    A client for interacting with the TestRail API.

    Attributes:
        base_url (str): The base URL for the API.
        aio_http_auth (aiohttp.BasicAuth): The authentication object for the API.
    """
    __cache = {}

    def __init__(self, base_url: str, username: str, password: str) -> None:
        """
        Initializes the APIClient with the provided base URL and authentication details.

        Args:
            base_url (str): The base URL for the API.
            username (str): The username for authentication.
            password (str): The password for authentication.
        """
        self.base_url = base_url
        self.aio_http_auth = aiohttp.BasicAuth(username, password)

    async def request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, no_cache: bool = False) -> Dict[str, Any]:
        """
        Sends a request to the API and returns the response.

        Args:
            method (str): The HTTP method (e.g., "GET", "POST").
            endpoint (str): The API endpoint to request.
            data (Optional[Dict[str, Any]]): The data to send with the request, if any.
            no_cache (bool): If True, bypasses cache for GET requests.

        Returns:
            Dict[str, Any]: The response data from the API.

        Raises:
            RuntimeError: If the request fails with a non-200 status code.
        """
        cache_key = (method, endpoint, frozenset(data.items()) if data else None)

        if not no_cache and method == "GET" and cache_key in self.__cache:
            return self.__cache[cache_key]

        async with aiohttp.ClientSession(auth=self.aio_http_auth) as session:
            url = self.base_url + endpoint
            async with session.request(method, url, json=data) as response:
                result = await response.json()
                if response.status != 200:
                    raise RuntimeError(
                        f"Request failed with status code {response.status} "
                        f"for {method} request to {url}"
                    )

                if method == "GET":
                    self.__cache[cache_key] = result

                return result
