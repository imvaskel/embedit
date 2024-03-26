import logging

import asqlite
import yt_dlp
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from embedit import CONFIG, cache_data, find_provider, is_bot, lifespan, try_cache
from embedit.providers import Provider

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


@app.get("/")
async def index():
    return RedirectResponse(CONFIG["repo"])


@app.get("/healthcheck")
async def healthcheck() -> str:
    return "i am alive!"


@app.get("/ograph/")
async def gen_ograph_json(url: str, title: str) -> dict[str, str]:
    async with asqlite.connect(CONFIG["sqlite"]["file"]) as conn:
        res = await try_cache(conn, url)
        if not res:
            raise HTTPException(404)

    return {
        "author_name": res.description,
        "author_url": url,
        "provider_name": "embedit",
        "provider_url": CONFIG["url"],
        "title": title,
        "type": "link",
        "version": "1.0",
    }


@app.exception_handler(yt_dlp.DownloadError)
async def handle_ytdlp_error(request: Request, exc: yt_dlp.DownloadError):
    logger.warning("encountered an error when downloading with yt_dlp: %s", exc)
    return Response(status_code=400)


@app.middleware("http")
async def pull_from_cache(request: Request, call_next):
    """Attempts to pull from the cache if the url exists there, else it lets the function fetch."""
    path: str = request.url.path
    if path != "/":
        async with asqlite.connect(CONFIG["sqlite"]["file"]) as conn:
            url = path.lstrip("/")
            info = await try_cache(conn, url)
            if info:
                logger.info("cache hit on endpoint %s, returning cache.", url)
                if is_bot(request.headers.get("User-Agent", "")):
                    return templates.TemplateResponse(
                        request, info.to_template(), {"info": info, "url": url, "color": CONFIG["color"]}
                    )
                else:
                    return RedirectResponse(url)
    return await call_next(request)


@app.get("/{url:path}")
async def get_url(request: Request, url: str):
    provider: Provider | None = find_provider(url)
    if not provider:
        raise HTTPException(404)

    info = await provider.parse(url)

    async with asqlite.connect(CONFIG["sqlite"]["file"]) as conn:
        await cache_data(conn, info, url)

    if is_bot(request.headers["User-Agent"]):
        return templates.TemplateResponse(
            request, info.to_template(), {"info": info, "url": url, "color": CONFIG["color"]}
        )
    return RedirectResponse(url)
