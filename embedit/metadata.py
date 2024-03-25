from dataclasses import dataclass

# I would like to have used ``NamedTuple`` here, but it seems that might not
# be possible with inheritance.


@dataclass
class OpenGraphData:
    title: str
    description: str
    url: str
    author_name: str

    def to_template(self) -> str:
        return "image.html"


@dataclass
class OpenGraphVideoData(OpenGraphData):
    thumbnail: str
    width: int
    height: int

    def to_template(self) -> str:
        return "video.html"
