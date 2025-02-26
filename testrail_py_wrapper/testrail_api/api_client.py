# -*- coding: utf-8 -*-
import aiohttp

from typing import Optional, Dict, Any

class APIClient:
    """
    Client for interacting with the TestRail API.

    Attributes:
        base_url (str): Base URL for the API.
        aio_http_auth (aiohttp.BasicAuth): Authentication object for the API.
    """
    __cache = {}

    def __init__(self, base_url: str, username: str, password: str) -> None:
        """
        Initializes the APIClient.

        :param base_url: Base URL for the API.
        :param username: Username for authentication.
        :param password: Password for authentication.
        """
        self.base_url = base_url
        self.aio_http_auth = aiohttp.BasicAuth(username, password)

    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        no_cache: bool = False
    ) -> Dict[str, Any]:
        """
        Sends an API request.

        :param method: HTTP method.
        :param endpoint: API endpoint.
        :param data: Request data.
        :param no_cache: Bypass cache for GET requests.

        :return: API response.

        :raises RuntimeError: Request failed or connection error.
        """
        cache_key = (method, endpoint, frozenset(data.items()) if data else None)

        if not no_cache and method == "GET" and cache_key in self.__cache:
            return self.__cache[cache_key]

        try:
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

        except aiohttp.ClientError as e:
            raise RuntimeError(f"Connection error occurred: {str(e)}")
