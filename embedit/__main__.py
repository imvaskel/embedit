import base64
import logging
from typing import Annotated

import asqlite
import yt_dlp
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from embedit import (
    CONFIG,
    cache_data,
    ensure_database,
    find_provider,
    generate_html,
    is_bot,
    try_cache,
)
from embedit.providers import Provider

pool: asqlite.Pool | None = None


async def database() -> asqlite.Pool:
    global pool
    if pool is None:
        pool = await asqlite.create_pool(CONFIG["sqlite"]["file"])
        async with pool.acquire() as conn:
            logger.info("creating shared pool and ensuring it.")
            await ensure_database(conn)
    return pool


app = FastAPI()
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


@app.get("/")
async def index():
    return RedirectResponse(CONFIG["repo"])


@app.get("/healthcheck")
async def healthcheck() -> str:
    return "i am alive!"


@app.get("/ograph/")
async def gen_ograph_json(author_name: str, title: str, url: str) -> dict[str, str]:
    return {
        "author_name": base64.b64decode(author_name).decode(),
        "author_url": url,
        "provider_name": "embedit",
        "provider_url": CONFIG["repo"],
        "title": f"Embedit - {title}",
        "type": "link",
        "version": "1.0",
    }


@app.exception_handler(yt_dlp.DownloadError)
async def handle_ytdlp_error(request: Request, exc: yt_dlp.DownloadError):
    logger.warning("encountered an error when downloading with yt_dlp: %s", exc)
    return Response(status_code=400)


@app.get("/{url:path}", response_class=HTMLResponse)
async def get_url(pool: Annotated[asqlite.Pool, Depends(database)], request: Request, url: str):
    async with pool.acquire() as conn:
        url = request.url.path.lstrip("/")
        info = await try_cache(conn, url)
        if info:
            logger.info("cache hit on endpoint %s, returning cache.", url)
        else:
            provider: Provider | None = find_provider(url)
            if not provider:
                raise HTTPException(404)

            info = await provider.parse(url)

            await cache_data(conn, info, url)

    if is_bot(request.headers["User-Agent"]):
        return generate_html(head_children=info.to_meta(), body_children=None)
    return RedirectResponse(url)
