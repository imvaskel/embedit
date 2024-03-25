import asyncio
from typing import Any

from yt_dlp import YoutubeDL

from .providers import PROVIDERS, Provider

YTDL = YoutubeDL()


# TODO: Typing
async def extract_info(url: str) -> dict[str, Any] | None:
    return await asyncio.to_thread(YTDL.extract_info, url, download=False)


def find_provider(url: str) -> Provider | None:
    for provider in PROVIDERS:
        if provider.match_url(url):
            return provider
    return None


# Adapted from https://github.com/dylanpdx/vxtiktok/blob/main/vxtiktok.py#L18
# This just checks keywords in the user agent
def should_redirect(user_agent: str) -> bool:
    return False
