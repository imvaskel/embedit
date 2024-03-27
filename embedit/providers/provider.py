from __future__ import annotations

import abc
import asyncio
from typing import TYPE_CHECKING, ClassVar

import yt_dlp
from fastapi import HTTPException

if TYPE_CHECKING:
    from embedit import OpenGraphBaseData, YTDLOutput

__all__ = ("Provider",)


class Provider(abc.ABC):
    name: ClassVar[str]

    async def _extract_info(self, url: str) -> YTDLOutput:
        """Uses ytdlp to extract the given url. This is wrapped in to_thread
        to make it async and if it does not return anything, it raises a 404.
        """
        with yt_dlp.YoutubeDL() as ytdl:
            res = await asyncio.to_thread(ytdl.extract_info, url, download=False)
            if not res:
                raise HTTPException(404)
            return res  # type: ignore - due to circular imports i cannot cast

    @abc.abstractmethod
    def match_url(self, url: str) -> bool:
        """Matches whether the given url is for this provider.

        Args:
            url (str): The url.

        Returns:
            bool: Whether or not the given url matches this provider.
        """
        ...

    @abc.abstractmethod
    async def parse(self, url: str) -> OpenGraphBaseData:
        """Parses the page and generates the opengraph metadata for embedding. This should
        throw a :class:`fastapi.HttpException` if an error occurs.

        Args:
            url (str): The url to parse.

        Returns:
            OpenGraphData: The open graph object representing the data parsed.
        """
        ...
