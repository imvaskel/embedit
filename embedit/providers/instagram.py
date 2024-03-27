from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException

from .provider import Provider

if TYPE_CHECKING:
    from embedit import OpenGraphBaseData


class InstagramProvider(Provider):
    name = "Instagram"

    def match_url(self, url: str) -> bool:
        return url.startswith("https://www.instagram")

    async def parse(self, url: str) -> OpenGraphBaseData:
        # data: YTDLOutput = await self._extract_info(url)
        # TODO: Fix this whenever yt-dlp fixes instagram downloads.

        raise HTTPException(400)
