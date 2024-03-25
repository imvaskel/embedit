from typing import Any

from embedit import OpenGraphData

from .provider import Provider


class InstagramProvider(Provider):
    name = "Instagram"

    def match_url(self, url: str) -> bool:
        return url.startswith("https://www.instagram")

    async def parse_page(self, data: dict[str, Any]) -> OpenGraphData | None: ...
