import json

import asqlite
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.templating import Jinja2Templates

from embedit import OpenGraphData, OpenGraphVideoData, cache_data, find_provider, lifespan
from embedit.providers import Provider

app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def health_check():
    return "hi"


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
        raise HTTPException(404)

    info = await provider.parse(url)

    async with asqlite.connect("cache.db") as conn:
        await cache_data(conn, info, url)

    return templates.TemplateResponse(request, info.to_template(), {"info": info, "url": url})
