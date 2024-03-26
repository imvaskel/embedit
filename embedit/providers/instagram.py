from fastapi import HTTPException

from embedit import OpenGraphData  # , YTDLOutput

from .provider import Provider


class InstagramProvider(Provider):
    name = "Instagram"

    def match_url(self, url: str) -> bool:
        return url.startswith("https://www.instagram")

    async def parse(self, url: str) -> OpenGraphData:
        # data: YTDLOutput = await self._extract_info(url)
        # TODO: Fix this whenever yt-dlp fixes instagram downloads.

        raise HTTPException(400)
