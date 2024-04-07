from __future__ import annotations

import html
from typing import TYPE_CHECKING

from fastapi import HTTPException

if TYPE_CHECKING:
    from embedit import OpenGraphBaseData

from ..provider import Provider
from .utils import api_request, get_id, video_id_regex


class TikTokProvider(Provider):
    name = "TikTok"
    color = "#ff0050"

    def match_url(self, url: str) -> bool:
        # TODO: Do this
        return url.startswith("https://www.tiktok")

    async def parse(self, url: str) -> OpenGraphBaseData:
        # TODO: Figure out if i can fix the circular imports.
        from embedit import OpenGraphVideoData

        if match := video_id_regex.match(url):
            video_id = match.group("id")
        else:
            video_id = await get_id(url)

        if not video_id:
            raise HTTPException(404)

        data = await api_request(video_id)
        aweme = data["aweme_list"][0]
        description: str = aweme["desc"]
        author_at: str = f"@{aweme['author']['unique_id']}"
        author_url: str = f"https://tiktok.com/{author_at}"
        author = f"{html.escape(aweme['author']['nickname'])} [{author_at}]"

        urls: list[str] = aweme["video"]["play_addr"]["url_list"]
        content_url = urls[len(urls) - 1]
        width: int = aweme["video"]["play_addr"]["width"]
        height: int = aweme["video"]["play_addr"]["height"]

        cover_urls = aweme["video"]["cover"]["url_list"]
        thumbnail = cover_urls[len(cover_urls) - 1]
        new_url = f"https://tiktok.com/{author_at}/video/{video_id}"

        return OpenGraphVideoData(
            title=self.name,
            description=description,
            media_url=content_url,
            author_name=author,
            thumbnail_url=thumbnail,
            width=width,
            height=height,
            author_url=author_url,
            url=new_url,
            color=self.color,
        )
