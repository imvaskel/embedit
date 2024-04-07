# This file is based off of: https://github.com/Britmoji/tiktxk/blob/main/src/util/tiktok.ts
# And https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/tiktok.py

from __future__ import annotations

import datetime
import math
import random
import re
import uuid
from typing import TYPE_CHECKING

import aiohttp
import yarl
from fastapi import HTTPException

if TYPE_CHECKING:
    from typing import Any

__all__: tuple[str, ...] = ("get_id", "api_request", "video_id_regex")


# Turns https://tiktok.com/<whatever> into a video ID.
async def get_id(url: str) -> str | None:
    async with session.get(url) as res:
        if match := video_id_regex.match(str(res.url)):
            return match.group("id")

    return None


async def api_request(vid_id: str) -> dict[str, Any]:
    for ids in app_install_ids:
        dynamic_query: dict[str, Any] = {
            "aweme_id": vid_id,
            "iid": ids,
            "last_install_time": math.floor(datetime.datetime.now().timestamp() // 1000)
            - random.randint(86400, 1123200),
            "aid": str(app_id),
            "app_name": app_name,
            "version_code": "".join(i.rjust(2, "0") for i in app_version.split(".")),  # x.y.z => x.0y.0z
            "version_name": app_version,
            "manifest_version_code": app_manifest_version,
            "update_version_code": app_manifest_version,
            "ab_version": app_version,
            "build_number": app_version,
            "_rticket": str(math.floor(datetime.datetime.now().timestamp())),
            "cdid": str(uuid.uuid4()),
            # Random 16 length hex, slice off ``0x``
            "opeuid": "".join(hex(random.randint(0x1000000000000000, 0x1111111111111111)))[2:],
            "ts": str(math.floor(datetime.datetime.now().timestamp() / 1000)),
            "device_id": str(random.randint(7250000000000000000, 7351147085025500000)),
            "device_type": "Pixel 7",
            "device_brand": "Google",
            "device_platform": "android",
        }
        query = base_query | dynamic_query

        async with session.get(
            base_url.with_query(query),
        ) as res:
            if res.headers.get("Content-Length") == "0":
                continue
            return await res.json()

    raise HTTPException(500, "There was an error fetching tiktok.")


# This is a dictionary of basic query params that do not change.
base_query: dict[str, Any] = {
    "ssmix": "a",
    "channel": "googleplay",
    "resolution": "1080*2400",
    "dpi": "420",
    "language": "en",
    "os": "android",
    "os_api": "29",
    "os_version": "13",
    "ac": "wifi",
    "is_pad": "0",
    "current_region": "US",
    "app_type": "normal",
    "sys_region": "US",
    "timezone_name": "America/New_York",
    "residence": "US",
    "app_language": "en",
    "timezone_offset": "-14400",
    "host_abi": "armeabi-v7a",
    "locale": "en",
    "ac2": "wifi5g",
    "uoo": "1",
    "op_region": "US",
    "region": "US",
}

app_name = "musical_ly"
app_id = 0
app_version = "34.1.2"
app_manifest_version = "2023401020"
user_agent = f"com.zhiliaoapp.musically/${app_version} (Linux; U; Android 13; en_US; Pixel 7; Build/TD1A.220804.031; Cronet/58.0.2991.0)"  # noqa: E501
app_install_ids = [
    "7351144126450059040",
    "7351149742343391009",
    "7351153174894626592",
]
base_url = yarl.URL("https://api22-normal-c-useast2a.tiktokv.com/aweme/v1/feed/")
session = aiohttp.ClientSession(headers={"User-Agent": user_agent})
video_id_regex = re.compile(r"https?://(www)?.tiktok.com/@[A-Za-z_]+/(video|photo)/(?P<id>\d+)")
