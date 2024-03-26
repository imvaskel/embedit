from fastapi import HTTPException

from embedit import Format, OpenGraphVideoData, YTDLOutput

from .provider import Provider

# Twitter is a complicated beast.
# Specifically, we have to do a lot of graphql, and yt-dlp can only fetch videos.


class TwitterProvider(Provider):
    name = "Twitter"

    def match_url(self, url: str) -> bool:
        return url.startswith("https://twitter") or url.startswith("https://x")

    async def parse(self, url: str) -> OpenGraphVideoData:
        data: YTDLOutput = await self._extract_info(url)
        fmt: Format
        for entry in data["formats"]:
            if entry["format_id"] == "http-2176":
                fmt = entry
                break
        else:
            raise HTTPException(400)

        description: str = data["description"]
        author: str = data["uploader"]
        author_url: str = data["uploader_url"]
        content_url: str = fmt["url"]
        width: int = fmt["width"]
        height: int = fmt["height"]
        thumbnail: str = data["thumbnail"]

        return OpenGraphVideoData(
            title="Twitter",
            description=description,
            url=content_url,
            author_name=author,
            thumbnail=thumbnail,
            width=width,
            height=height,
            author_url=author_url,
        )
