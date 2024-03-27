from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from embedit import OpenGraphBaseData, YTDLOutput


from embedit import Format, OpenGraphVideoData

from .provider import Provider


class TikTokProvider(Provider):
    name = "TikTok"

    def match_url(self, url: str) -> bool:
        # TODO: Do this
        return url.startswith("https://www.tiktok")

    async def parse(self, url: str) -> OpenGraphBaseData:
        data: YTDLOutput = await self._extract_info(url)

        description: str = data["description"]
        author: str = f"{data['channel']} (@{data['uploader']})"
        author_url: str = data["uploader_url"]
        formats: list[Format] = data["formats"]
        content_url: str = formats[0]["url"]
        width: int = formats[0]["width"]
        height: int = formats[0]["height"]
        thumbnail: str = data["thumbnail"]

        return OpenGraphVideoData(
            title=self.name,
            description=description,
            url=content_url,
            author_name=author,
            thumbnail=thumbnail,
            width=width,
            height=height,
            author_url=author_url,
        )
