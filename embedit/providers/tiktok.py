from embedit import Format, OpenGraphData, OpenGraphVideoData, YTDLOutput

from .provider import Provider


class TikTokProvider(Provider):
    name = "TikTok"

    def match_url(self, url: str) -> bool:
        # TODO: Do this
        return url.startswith("https://www.tiktok")

    async def parse(self, url: str) -> OpenGraphData:
        data: YTDLOutput = await self._extract_info(url)

        title: str = data["title"]
        author: str = data["channel"]
        formats: list[Format] = data["formats"]
        content_url: str = formats[0]["url"]
        width: int = formats[0]["width"]
        height: int = formats[0]["height"]
        thumbnail: str = data["thumbnail"]

        return OpenGraphVideoData("TikTok", title, content_url, author, thumbnail, width, height)
