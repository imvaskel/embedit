import datetime
import json
from contextlib import asynccontextmanager
from dataclasses import asdict

import asqlite
from fastapi import FastAPI

from .metadata import OpenGraphData, OpenGraphVideoData

__all__ = ("ensure_database", "lifespan", "cache_data")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with asqlite.connect("cache.db") as conn:
        await ensure_database(conn)
    yield


async def ensure_database(conn: asqlite.Connection):
    with open("./schema.sql") as fp:
        sql = fp.read()
    async with conn.cursor() as cursor:
        await cursor.executescript(sql)
        await conn.commit()


async def cache_data(conn: asqlite.Connection, info: OpenGraphData, url: str):
    # Yes, i know this is cursed. But I'm lazy.
    async with conn.cursor() as cursor:
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        await cursor.execute(
            "INSERT INTO cache(url, data, expiry, type) VALUES(?, ?, ?, ?)",
            url,
            json.dumps(asdict(info)),
            tomorrow.timestamp(),
            info.to_type(),
        )


async def try_cache(conn: asqlite.Connection, url: str) -> OpenGraphData | None:
    async with conn.cursor() as cursor:
        res = await cursor.execute("SELECT * FROM cache WHERE url = ?", url)
        row = await res.fetchone()
        if not row:
            return None

        data_type: str = row["type"]
        data = json.loads(row["data"])
        match data_type:
            case "video":
                return OpenGraphVideoData(**data)
            case "text":
                return OpenGraphData(**data)
            case _:
                raise Exception("Invalid data type.")  # noqa: TRY002, TRY003
