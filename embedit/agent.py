# Credit to https://github.com/Wikidepia/InstaFix/blob/main/utils/crawlerdetect.go for the list of crawlers used here.

known_bots: list[str] = [
    "bot",
    "facebook",
    "embed",
    "got",
    "firefox/92",
    "firefox/38",
    "curl",
    "wget",
    "go-http",
    "yahoo",
    "generator",
    "whatsapp",
    "preview",
    "link",
    "proxy",
    "vkshare",
    "images",
    "analyzer",
    "index",
    "crawl",
    "spider",
    "python",
    "cfnetwork",
    "node",
    "mastodon",
    "http.rb",
    "discord",
    "ruby",
    "bun/",
    "fiddler",
    "revoltchat",
]


def is_bot(ua: str) -> bool:
    return any(bot in ua for bot in known_bots)
