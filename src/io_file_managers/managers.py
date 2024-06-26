from typing import AsyncGenerator

import aiofiles
import aiohttp
from aiohttp_socks import ProxyConnector

from core.exceptions import StreamFail
from core.settings import settings

from .abstract import IOFileManagerABC


class IOTorFileManager(IOFileManagerABC):

    def __init__(self):
        self.headers = {
            "Accept": r"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": r"gzip, deflate, br",
            "Connection": "keep-alive",
        }

    async def download_file(self, url: str) -> None:
        socks_conn = ProxyConnector(host=settings.proxy_host, port=settings.proxy_port)
        async with aiohttp.ClientSession(connector=socks_conn) as tor_session:
            async with tor_session.get(url, headers=self.headers):
                async with aiofiles.open(hash(url), "wb") as f:
                    async for chunk in tor_session.content.iter_chunked(
                        settings.chunk_size
                    ):
                        await f.write(chunk)

    async def stream_file(self, url: str) -> AsyncGenerator[bytes, None]:
        socks_conn = ProxyConnector(host=settings.proxy_host, port=settings.proxy_port)
        async with aiohttp.ClientSession(connector=socks_conn) as tor_session:
            async with tor_session.get(url, headers=self.headers) as response:
                async for chunk in response.content.iter_chunked(settings.chunk_size):
                    try:
                        yield chunk
                    except Exception:
                        raise StreamFail(detail=Exception)
