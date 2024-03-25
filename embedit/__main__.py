import json
from typing import Any

import asqlite
from fastapi import FastAPI, Request, Response
from fastapi.templating import Jinja2Templates

from embedit import OpenGraphData, OpenGraphVideoData, extract_info, find_provider, insert_data, lifespan
from embedit.providers import Provider

app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def health_check():
    return "hi"


@app.get("/json/{url:path}")
async def get_json(response: Response, url: str):
    provider: Provider | None = find_provider(url)
    if not provider:
        response.status_code = 404
        return


@app.middleware("http")
async def pull_from_cache(request: Request, call_next):
    """Attempts to pull from the cache if the url exists there, else it lets the function fetch."""
    path: str = request.url.path
    if path != "/":
        async with asqlite.connect("cache.db") as conn:
            url = path.lstrip("/json/")  # noqa: B005
            res = await conn.fetchone("SELECT * FROM cache WHERE url = ?", url)
            info: OpenGraphData
            if res:
                print(f"cache hit on endpoint {path}, returning cache.")
                hit = json.loads(res["data"])
                info = OpenGraphVideoData(**hit) if hit.get("width") else OpenGraphData(**hit)
                if not path.startswith("/json/"):
                    return templates.TemplateResponse(request, info.to_template(), {"info": info, "url": url})
                # else:
                # ... # TODO:
    return await call_next(request)


@app.get("/ograph")
async def gen_ograph_json(text: str, url: str):
    return {
        "author_name": text,
        "author_url": url,
        "provider_name": "embedit",
        "provider_url": "https://embedit.vaskel.gay",
        "title": "TikTok",
        "type": "link",
        "version": "1.0",
    }


@app.get("/{url:path}")
async def get_url(request: Request, response: Response, url: str):
    provider: Provider | None = find_provider(url)
    if not provider:
        response.status_code = 404
        return

    data: dict[str, Any] | None = await extract_info(url)
    if not data:
        response.status_code = 404
        return

    info = await provider.parse_page(data)
    if not info:
        response.status_code = 500
        return

    async with asqlite.connect("cache.db") as conn:
        await insert_data(conn, info, url)

    return templates.TemplateResponse(request, info.to_template(), {"info": info, "url": url})
