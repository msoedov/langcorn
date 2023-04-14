import asyncio
import random
import sys
import time
from collections import defaultdict

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from loguru import logger
from pydantic import BaseModel

from uvicorn.importer import import_from_string

logger.remove(0)
logger.add(
    sys.stderr,
    format="<red>[{level}]</red>: <green>{message}</green> @ {time:HH:mm:ss.SS}",
    colorize=True,
)


class LangRequest(BaseModel):
    prompt: str


class LangResponse(BaseModel):
    output: str


def create_service(*lc_apps):
    app = FastAPI()
    for lc in lc_apps:
        lca = import_from_string(lc)
        print(f"{lc=}")
        print(f"{lca=}")
        endpoint_prefix = lc.split(":")[0]

        @app.post(f"/{endpoint_prefix}/run", response_model=LangResponse)
        async def predict_sync(
            request: LangRequest,
        ):
            output = lca.run(request.prompt)
            # add error handling
            return LangResponse(output=output)

    @app.get("/state")
    async def state():
        return dict(functions=[*lc_apps])

    return app
