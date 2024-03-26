from .providers import PROVIDERS, Provider


def find_provider(url: str) -> Provider | None:
    for provider in PROVIDERS:
        if provider.match_url(url):
            return provider
    return None


# Adapted from https://github.com/dylanpdx/vxtiktok/blob/main/vxtiktok.py#L18
# This just checks keywords in the user agent
def should_redirect(user_agent: str) -> bool:
    return False
