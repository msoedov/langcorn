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


def derive_fields(language_app) -> (list[str], list[str]):
    if hasattr(language_app, "input_variables"):
        return language_app.input_variables, language_app.output_variables
    elif hasattr(language_app, "prompt"):
        return language_app.prompt.input_variables, [language_app.output_key]
    return [language_app.input_key], ["output"]


def derive_class(name, fields):
    return type(
        f"Lang{name}", (BaseModel,), {"__annotations__": {f: str for f in fields}}
    )


def make_handler(request_cls, chain):
    async def handler(
        request: request_cls,
    ):
        output = chain.run(request.dict())
        # add error handling
        return LangResponse(output=output, error="")

    return handler


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
        inn, out = derive_fields(chain)
        logger.info(f"{inn=}")
        endpoint_prefix = lang_app.split(":")[0]
        cls_name = "".join([c.capitalize() for c in endpoint_prefix.split(".")])
        request_cls = derive_class(cls_name, inn)
        logger.info(f"{request_cls=}")

        endpoints.append(f"/{endpoint_prefix}/run")
        # avoid hoisting issues with handler(request)
        app.post(
            f"/{endpoint_prefix}/run",
            response_model=LangResponse,
            dependencies=[_authenticate_or_401],
            name=lang_app,
        )(make_handler(request_cls, chain))

    @app.get("/ht")
    async def health_check():
        return dict(functions=[*lc_apps])

    logger.info("Serving")
    for endpoint in endpoints:
        logger.info(f"Endpoint: {endpoint}")
    return app
