from typing import Any

from embedit import OpenGraphData, OpenGraphVideoData

from .provider import Provider


class TikTokProvider(Provider):
    name = "TikTok"

    def match_url(self, url: str) -> bool:
        # TODO: Do this
        return url.startswith("https://www.tiktok")

    def alter_url(self, url: str) -> str:
        # https://github.com/dylanpdx/vxtiktok/blob/05ac76fbef6469423350cabf76cca22debcf744f/vxtiktok.py#L197
        return url.replace("/photo/", "/video/")

    async def parse_page(self, data: dict[str, Any]) -> OpenGraphData | None:
        title: str = data["title"]
        author: str = data["channel"]
        formats: list[dict[str, Any]] = data["formats"]
        url: str = formats[0]["url"]
        width: int = formats[0]["width"]
        height: int = formats[0]["height"]
        thumbnail: str = data["thumbnail"]

        return OpenGraphVideoData("TikTok", title, url, author, thumbnail, width, height)
