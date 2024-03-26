import abc
from dataclasses import dataclass

# I would like to have used ``NamedTuple`` here, but it seems that might not
# be possible with inheritance.


class OpenGraphBaseData(abc.ABC):
    @abc.abstractmethod
    def to_template(self) -> str: ...

    @abc.abstractmethod
    def to_type(self) -> str: ...


@dataclass(kw_only=True)
class OpenGraphData(OpenGraphBaseData):
    title: str
    description: str
    url: str
    author_name: str
    author_url: str

    def to_template(self) -> str:
        return "image.html"

    def to_type(self) -> str:
        return "text"


@dataclass(kw_only=True)
class OpenGraphVideoData(OpenGraphData):
    thumbnail: str
    width: int
    height: int

    def to_template(self) -> str:
        return "video.html"

    def to_type(self) -> str:
        return "video"
