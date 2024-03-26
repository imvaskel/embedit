import inspect
import logging
import sys

from .instagram import InstagramProvider as InstagramProvider
from .provider import Provider as Provider
from .tiktok import TikTokProvider as TikTokProvider
from .twitter import TwitterProvider as TwitterProvider

logger = logging.getLogger(__name__)

PROVIDERS: list[Provider] = []

for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass):
    if issubclass(obj, Provider) and name != "Provider":
        logger.info("found provider with name %s, adding to all providers.", obj.__name__)
        PROVIDERS.append(obj())

del obj, inspect, logging, sys, logger
