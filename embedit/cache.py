import datetime
import json
from contextlib import asynccontextmanager
from dataclasses import asdict

import asqlite
from fastapi import FastAPI

from .metadata import OpenGraphData

__all__ = ("ensure_database", "lifespan", "insert_data")


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


async def insert_data(conn: asqlite.Connection, info: OpenGraphData, url: str):
    # Yes, i know this is cursed. But I'm lazy.
    async with conn.cursor() as cursor:
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        await cursor.execute(
            "INSERT INTO cache(url, data, expiry) VALUES(?, ?, ?)", url, json.dumps(asdict(info)), tomorrow.timestamp()
        )
