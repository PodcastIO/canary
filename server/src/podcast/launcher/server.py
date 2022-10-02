import os
import time

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette_context import context, plugins
from starlette_context.middleware import ContextMiddleware

from podcast.pkg.errors.biz_error import BizException, SystemException
from podcast.router import podcast, resource, category
import podcast.pkg.client.log as logging
from podcast.router import user
from podcast.router.user import token_is_valid


origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]


app = FastAPI()
app.include_router(podcast.router)
app.include_router(resource.router)
app.include_router(category.router)
app.include_router(user.router)


@app.middleware("http")
async def exception(request: Request, call_next):
    try:
        response = await call_next(request)
    except BizException as ex:
        logging.warning("[biz] %s", ex.msg)
        response = Response(ex.get_response(), status_code=200)
    except Exception as ex:
        logging.exception(ex)
        response = Response(SystemException().get_response(), status_code=500)
    return response

@app.middleware("http")
async def auth(request: Request, call_next):
    context.data["base_url"] = str(request.headers.get("origin", "")).strip("/")
    for uri in ["/api/web/user/login",
                "/api/web/user/check_login",
                "/api/web/user/confirm_login",
                "/api/web/resource",
                "/api/web/podcast/rss"]:
        if request.scope.get("path").startswith(uri):
            return await call_next(request)

    _, user_id = token_is_valid(request)
    context.data["user_id"] = user_id
    return await call_next(request)


@app.middleware("http")
async def cost_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_credentials=True,
    allow_methods=["Set-Cookie", "Content-Type"],
    allow_headers=["GET", "POST", "PUT", "OPTIONS"],
)

app.add_middleware(
    ContextMiddleware,
    plugins=(
        plugins.RequestIdPlugin(),
        plugins.CorrelationIdPlugin()
    )
)


def launch(host: str, port: int, reload: bool):
    uvicorn.run("podcast.launcher.server:app",
                host=host, port=port, reload=reload)
