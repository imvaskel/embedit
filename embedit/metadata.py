import abc
from dataclasses import dataclass

# I would like to have used ``NamedTuple`` here, but it seems that might not
# be possible with inheritance.


@dataclass(kw_only=True)
class OpenGraphBaseData(abc.ABC):
    title: str
    description: str
    color: str | None = None

    @abc.abstractmethod
    def to_template(self) -> str: ...

    @abc.abstractmethod
    def to_type(self) -> str: ...


@dataclass(kw_only=True)
class OpenGraphTextData(OpenGraphBaseData):
    author_name: str
    author_url: str
    author_avatar: str | None = None

    def to_template(self) -> str:
        return "text.html"

    def to_type(self) -> str:
        return "text"


@dataclass(kw_only=True)
class OpenGraphImageData(OpenGraphBaseData):
    url: str
    author_name: str
    author_url: str
    width: int
    height: int

    def to_template(self) -> str:
        return "image.html"

    def to_type(self) -> str:
        return "image"


@dataclass(kw_only=True)
class OpenGraphVideoData(OpenGraphImageData):
    thumbnail: str

    def to_template(self) -> str:
        return "video.html"

    def to_type(self) -> str:
        return "video"
