from typing import Any, ClassVar, Protocol

from embedit import OpenGraphData

__all__ = ("Provider",)


class Provider(Protocol):
    name: ClassVar[str]

    def match_url(self, url: str) -> bool:
        """Matches whether the given url is for this provider.

        Args:
            url (str): The url.

        Returns:
            bool: Whether or not the given url matches this provider.
        """
        ...

    def alter_url(self, url: str) -> str:
        """Alters a url if need be. This should be implemented by subclasses to alter the urls, as the main
        webserver calls this.

        Args:
            url (str): The url.

        Returns:
            str: The URL to the post, potentially altered.
        """
        return url

    async def parse_page(self, data: dict[str, Any]) -> OpenGraphData | None:
        """Parses the page and generates the opengraph metadata for embedding.

        Args:
            data (dict[str, Any]): The data extracted from yt-dl's ``YoutubeDL.extract_info``.

        Returns:
            OpenGraphData | None: The open graph object representing the data parsed. ``None`` if the parsing
            failed for whatever reason.
        """
        ...
