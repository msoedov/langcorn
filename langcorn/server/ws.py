from fastapi import Depends, FastAPI, Request, WebSocket, WebSocketDisconnect
from loguru import logger

from .api import (
    LangResponse,
    create_service,
    derive_class,
    derive_fields,
    import_from_string,
)


def make_ws_handler(request_cls, chain):
    async def websocket_endpoint(websocket: WebSocket) -> LangResponse:
        await websocket.accept()
        memory = chain.memory
        while True:
            try:
                # Receive and send back the client message
                question = await websocket.receive_json()
                output = await chain.arun(question)
                await websocket.send_json(dict(output=output))
            except WebSocketDisconnect:
                logger.info("websocket disconnect")
                break
            except Exception as e:
                logger.error(e)
                resp = dict(
                    message="Sorry, something went wrong. Try again.",
                    type="error",
                )
                await websocket.send_json(resp)

    return websocket_endpoint


def create_ws_service(*lc_apps, auth_token: str = "", app: FastAPI = None):
    app = app or FastAPI()
    endpoints = []

    for lang_app in lc_apps:
        chain = import_from_string(lang_app)
        inn, out = derive_fields(chain)
        logger.debug(f"inputs:{inn=}")
        logger.info(f"{lang_app=}:{chain.__class__.__name__}({inn})")
        endpoint_prefix = lang_app.split(":")[0]
        cls_name = "".join([c.capitalize() for c in endpoint_prefix.split(".")])
        request_cls = derive_class(cls_name, inn)
        logger.debug(f"{request_cls=}")

        endpoints.append(f"/{endpoint_prefix}/ws")
        # avoid hoisting issues with handler(request)
        app.websocket(
            f"/{endpoint_prefix}/ws",
        )(make_ws_handler(request_cls, chain))

    logger.info("Serving")
    for endpoint in endpoints:
        logger.info(f"Endpoint: {endpoint}")
    return app
