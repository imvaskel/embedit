from __future__ import annotations

import asyncio
import html
import logging
import re
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from fastapi import HTTPException
from twitter.scraper import Scraper
from twitter.util import init_session

from .provider import Provider

if TYPE_CHECKING:
    from embedit import OpenGraphBaseData

logger = logging.getLogger(__name__)


# Twitter is a complicated beast.
# Specifically, we have to do a lot of graphql, and yt-dlp can only fetch videos.
class ScraperWrapper:
    """A wrapper for the twitter scraper that invalidates the scraper every 2.5h
    as twitter invalidates guest sessions after 3h. This also wraps some methods for
    convenience as methods here need to be wrapped in to_thread
    """

    _scraper: Scraper
    _created: datetime

    def __init__(self) -> None:
        self._scraper = Scraper(session=init_session(), save=False)
        self._created = datetime.now()

    @property
    def scraper(self) -> Scraper:
        now = datetime.now()
        if self._created + timedelta(hours=2.5) < now:
            # Create new scraper
            logger.info("old scraper expired, creating a new one.")
            self._scraper = Scraper(session=init_session(), save=False)
        return self._scraper

    async def tweets(self, tweet: int) -> list[dict[Any, Any]]:
        return await asyncio.to_thread(self.scraper.tweets_by_id, [tweet])


scraper = ScraperWrapper()

regex = re.compile(r"https?:\/\/(x|twitter)\.com\/[A-Za-z0-9_]+\/status\/(?P<id>\d+)")
size_regex = re.compile(r"(?P<width>\d+)x(?P<height>\d+)")


class TwitterProvider(Provider):
    name = "Twitter"
    color = "#1DA1F2"

    def match_url(self, url: str) -> bool:
        return url.startswith("https://twitter") or url.startswith("https://x")

    async def parse(self, url: str) -> OpenGraphBaseData:
        from embedit import OpenGraphImageData, OpenGraphTextData, OpenGraphVideoData

        match = regex.match(url)
        if not match:
            raise HTTPException(404)
        tweet_id: str = match.group("id")
        data = await scraper.tweets(int(tweet_id))
        # So, after parsing this a bit with jq, we get the following:
        # .[0].data.tweetResult.result
        # .legacy gives us access to the tweet's data, while .core.user_results.result.legacy
        # gives us the user data we want
        # .full_text seems to be what we want and
        # to get media we can then do .entities.media[0], then we can do ``media_url_https``
        # also applicable is ``type``
        # if it is just text, then ``media`` won't even exist.
        # if it doesn't exist, then [0].data.tweetResult is just an empty dict.
        result = data[0]["data"]["tweetResult"]
        if not result:
            raise HTTPException(404)
        result = result["result"]
        legacy = result["legacy"]
        user = result["core"]["user_results"]["result"]["legacy"]

        text = html.escape(legacy["full_text"])
        author = f"{user['name']} (@{user['screen_name']})"
        author_url = f"https://twitter.com/{user['screen_name']}"

        if "media" in legacy["entities"]:
            media = legacy["entities"]["media"][0]
            url = media["media_url_https"]
            if media["type"] == "photo":
                size = media["sizes"]["medium"]
                height = size["h"]
                width = size["w"]
                return OpenGraphImageData(
                    title="Twitter",
                    description=text,
                    media_url=url,
                    author_name=author,
                    author_url=author_url,
                    height=height,
                    width=width,
                    url=url,
                    color=self.color,
                )
            elif media["type"] == "video":
                variants = media["video_info"]["variants"]
                variant = {}
                for v in variants:
                    if v["content_type"] == "video/mp4":
                        variant = v
                if not variant:
                    raise HTTPException(400, detail="unable to find video variant.")
                video_url = variant["url"]
                match = size_regex.findall(
                    video_url
                )  # kinda rigged, but for some reason it doesn't provide default size
                if not match:
                    raise HTTPException(400, detail="unable to find match for width and height in the video url.")
                width, height = (int(f) for f in match[0])
                return OpenGraphVideoData(
                    title="Twitter",
                    description=text,
                    media_url=video_url,
                    author_name=author,
                    author_url=author_url,
                    thumbnail_url=url,
                    width=width,
                    height=height,
                    url=url,
                    color=self.color,
                )

        author_avatar = user["profile_image_url_https"]
        return OpenGraphTextData(
            title="Twitter",
            description=text,
            author_name=author,
            author_url=author_url,
            author_avatar=author_avatar,
            url=url,
            color=self.color,
        )
