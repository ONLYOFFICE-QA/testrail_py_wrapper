# -*- coding: utf-8 -*-
import aiohttp

from typing import Optional, Dict, Any


class APIClient:
    __cache = {}

    def __init__(self, base_url: str, username: str, password: str) -> None:
        self.base_url = base_url
        self.aio_http_auth = aiohttp.BasicAuth(username, password)

    async def request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        cache_key = (method, endpoint, frozenset(data.items()) if data else None)

        if method == "GET" and cache_key in self.__cache:
            return self.__cache[cache_key]

        async with aiohttp.ClientSession(auth=self.aio_http_auth) as session:
            url = self.base_url + endpoint
            async with session.request(method, url, json=data) as response:
                result = await response.json()

                if method == "GET":
                    self.__cache[cache_key] = result

                return result
