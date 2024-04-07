import abc
import base64
import html
from dataclasses import dataclass

from .config import CONFIG
from .html import generate_attribute, generate_meta_tag, generate_tag

# I would like to have used ``NamedTuple`` here, but it seems that might not
# be possible with inheritance.


@dataclass(kw_only=True)
class OpenGraphBaseData(abc.ABC):
    title: str
    description: str
    color: str | None = None
    url: str
    author_name: str
    author_url: str

    @abc.abstractmethod
    def to_type(self) -> str: ...

    def to_meta(self) -> list[str]:
        """Generates the metadata for the page. This should be overriden by children to add extra
        meta tags if applicable.

        Returns:
            list[str]: The list of metadata tags.
        """
        meta = [
            generate_meta_tag(prop="theme-color", value=self.color or CONFIG["color"]),
            generate_meta_tag(
                prop="og:description", value=html.escape(self.description) if self.title == "Twitter" else None
            ),
            generate_meta_tag(value=f"content = 0; url = {self.url}", extras={"http-equiv": "refresh"}),
            generate_meta_tag(prop="og:site_name", value=f"Embedit - {self.title}"),
            generate_meta_tag(prop="og:url", value=self.url),
        ]

        return meta


@dataclass(kw_only=True)
class OpenGraphTextData(OpenGraphBaseData):
    author_avatar: str | None = None

    def to_type(self) -> str:
        return "text"

    def to_meta(self) -> list[str]:
        meta = super().to_meta()
        meta += [
            generate_meta_tag(prop="og:type", value="website"),
            generate_meta_tag(prop="og:title", value=self.author_name),
        ]

        if self.author_avatar:
            meta += [
                generate_meta_tag(prop="og:image", value=self.author_avatar),
                generate_meta_tag(prop="twitter:image", value=self.author_avatar),
            ]

        return meta


@dataclass(kw_only=True)
class OpenGraphImageData(OpenGraphBaseData):
    media_url: str
    width: int
    height: int

    def to_type(self) -> str:
        return "image"

    def to_meta(self) -> list[str]:
        meta = super().to_meta()
        meta += [
            generate_meta_tag(prop="og:type", value="website"),
            generate_meta_tag(prop="og:title", value=self.author_name),
            generate_meta_tag(prop="twitter:card", value="summary_large_image"),
            generate_meta_tag(prop="twitter:card:image", value=self.media_url),
            generate_meta_tag(prop="twitter:card:height", value=self.height),
            generate_meta_tag(prop="twitter:card:width", value=self.width),
            generate_meta_tag(prop="og:image", value=self.media_url),
            generate_meta_tag(prop="og:image:height", value=self.height),
            generate_meta_tag(prop="og:image:width", value=self.width),
        ]

        return meta


@dataclass(kw_only=True)
class OpenGraphVideoData(OpenGraphImageData):
    thumbnail_url: str
    extra_video_url: str | None = None

    def to_type(self) -> str:
        return "video"

    def to_meta(self) -> list[str]:
        meta = OpenGraphBaseData.to_meta(self)
        meta += [
            generate_meta_tag(prop="og:type", value="video.other"),
            generate_meta_tag(prop="og:video", value=self.media_url),
            generate_meta_tag(prop="og:video:type", value="video/mp4"),
            generate_meta_tag(prop="og:video:width", value=self.width),
            generate_meta_tag(prop="og:video:height", value=self.height),
            generate_meta_tag(prop="og:title", value=self.author_name),
            generate_meta_tag(prop="og:image", value=self.thumbnail_url),
            generate_tag(
                name="link",
                value="".join(
                    [
                        generate_attribute("rel", "alternate"),
                        generate_attribute(
                            "href",
                            f"{CONFIG['url']}/ograph/?author_name={str(base64.b64encode(self.author_name.encode()), 'utf-8')}&title={self.title}&url={self.url}",  # noqa: E501
                        ),
                    ]
                ),
            ),
        ]

        return meta
