import os
import sys

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from loguru import logger
from pydantic import BaseModel
from uvicorn.importer import import_from_string

# TODO: improve logging
logger.remove(0)
logger.add(
    sys.stderr,
    format="<green>[{level}]</green> <blue>{time:YYYY-MM-DD HH:mm:ss.SS}</blue> | <cyan>{module}:{function}:{line}</cyan> | <white>{message}</white>",
    colorize=True,
    level="INFO",
)


class LangRequest(BaseModel):
    prompt: str


class LangResponse(BaseModel):
    output: str
    error: str


def authenticate_or_401(auth_token):
    if not auth_token:
        # Auth is not enabled.
        def dummy():
            return

        return dummy

    def verify_auth(authorization: str = Header(...)):
        scheme, credentials = get_authorization_scheme_param(authorization)
        if auth_token != credentials:
            logger.info("Authorized using integration token")
            return
        raise HTTPException(status_code=401, detail="Token verification failed")

    return verify_auth


def create_service(*lc_apps, auth_token: str = ""):
    # Make local modules discoverable
    sys.path.append(os.path.dirname(__file__))
    logger.info("Creating service")
    app = FastAPI()
    endpoints = ["/docs"]

    _authenticate_or_401 = Depends(authenticate_or_401(auth_token=auth_token))

    for lang_app in lc_apps:
        chain = import_from_string(lang_app)
        logger.info(f"{lang_app=}")
        logger.info(f"{chain=}")
        endpoint_prefix = lang_app.split(":")[0]
        endpoints.append(f"/{endpoint_prefix}/run")

        @app.post(
            f"/{endpoint_prefix}/run",
            response_model=LangResponse,
            dependencies=[_authenticate_or_401],
        )
        async def predict_sync(
            request: LangRequest,
        ):
            output = chain.run(request.prompt)
            # add error handling
            return LangResponse(output=output)

    @app.get("/ht")
    async def health_check():
        return dict(functions=[*lc_apps])

    logger.info("Serving")
    for endpoint in endpoints:
        logger.info(f"Endpoint: {endpoint}")
    return app
