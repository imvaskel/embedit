from .providers import PROVIDERS, Provider


def find_provider(url: str) -> Provider | None:
    for provider in PROVIDERS:
        if provider.match_url(url):
            return provider
    return None
