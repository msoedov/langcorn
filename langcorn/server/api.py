import os
import sys
import types
from typing import Any, Union

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.security.utils import get_authorization_scheme_param
from langchain.callbacks import get_openai_callback
from langchain.schema import messages_from_dict, messages_to_dict
from loguru import logger
from pydantic import BaseModel
from uvicorn.importer import import_from_string

TRACK_USAGE = True

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


class MemoryData(BaseModel):
    content: str
    additional_kwargs: dict[str, Any]


class Memory(BaseModel):
    type: str
    data: MemoryData


class LangResponse(BaseModel):
    output: Union[str, dict[str, str]]
    error: str
    memory: list[Memory]


class LangResponseDocuments(LangResponse):
    source_documents: list[str]


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


class FnWrapper:
    memory = []
    output_key = ["output"]
    input_variables = ["query"]
    output_variables = "output"
    output_keys = ["output"]

    def __init__(self, fn):
        self.fn = fn

    def run(self, prompt: str):
        r = self.fn(query=prompt)
        return r.dict()


def derive_fields(language_app) -> (list[str], list[str]):
    if hasattr(language_app, "input_variables"):
        return language_app.input_variables, language_app.output_variables
    elif hasattr(language_app, "prompt"):
        return language_app.prompt.input_variables, [language_app.output_key]
    elif hasattr(language_app, "input_keys"):
        return language_app.input_keys, [language_app.output_key]
    return [language_app.input_key], ["output"]


def derive_class(name, fields, add_memory=False):
    annotations = {f: str for f in fields}
    if add_memory:
        annotations["memory"] = list[dict]
    if "chat_history" in annotations:
        annotations["chat_history"] = list[list[str]]
    return type(f"Lang{name}", (BaseModel,), {"__annotations__": annotations})


def set_openai_key(new_key: str) -> str:
    if not new_key:
        return
    import openai

    prev = openai.api_key
    openai.api_key = new_key
    return prev


def extract_llm_kwargs(http_headers: dict[str, str]) -> dict[str, Any]:
    llm_kwargs = {}
    if "x-llm-temperature" in http_headers:
        llm_kwargs["temperature"] = float(http_headers["x-llm-temperature"])
    if "x-max-tokens" in http_headers:
        llm_kwargs["max_tokens"] = int(http_headers["x-max-tokens"])
    if "x-model-name" in http_headers:
        llm_kwargs["model_name"] = http_headers["x-model-name"]
    return llm_kwargs


def configure_llm(chain, http_headers: dict[str, str]):
    llm_kwargs = extract_llm_kwargs(http_headers)
    if not llm_kwargs:
        return
    # TODO: refactor to type switch
    if hasattr(chain, "llm_chain"):
        return configure_llm(chain.llm_chain, http_headers)
    elif hasattr(chain, "llm_kwargs"):
        chain.llm_kwargs = llm_kwargs
        return True
    elif hasattr(chain, "llm"):
        for k, v in llm_kwargs.items():
            setattr(chain.llm, k, v)
        return True
    return False


def add_chat_history(run_params):
    if "chat_history" in run_params:
        run_params["chat_history"] = [tuple(t) for t in run_params["chat_history"]]


def make_handler(request_cls, chain):
    async def handler(request: request_cls, http_request: Request):
        llm_api_key = http_request.headers.get("x-llm-api-key")
        retrieval_chain = len(chain.output_keys) > 1
        try:
            api_key = set_openai_key(llm_api_key)
            configure_llm(chain, http_request.headers)
            run_params = request.dict()
            memory = run_params.pop("memory", [])
            if chain.memory and memory and memory[0]:
                chain.memory.chat_memory.messages = messages_from_dict(memory)
            add_chat_history(run_params)
            with get_openai_callback() as cb:
                if not retrieval_chain:
                    output = chain.run(run_params)
                else:
                    output = chain(run_params)
                if TRACK_USAGE:
                    print(cb)

            # add error handling
            memory = (
                []
                if not chain.memory
                else messages_to_dict(chain.memory.chat_memory.messages)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=dict(error=str(e)))
        finally:
            set_openai_key(api_key)
        if retrieval_chain:
            return LangResponseDocuments(
                output=output.get("result", output),
                error="",
                memory=memory,
                source_documents=[str(t) for t in output.get("source_documents", [])],
            )
        return LangResponse(output=output, error="", memory=memory)

    return handler


def create_service(*lc_apps, auth_token: str = "", app: FastAPI = None):
    # Make local modules discoverable
    sys.path.append(os.path.dirname("."))
    logger.info("Creating service")
    app = app or FastAPI()
    endpoints = ["/docs"]

    _authenticate_or_401 = Depends(authenticate_or_401(auth_token=auth_token))
    if lc_apps and isinstance(import_from_string(lc_apps[0]), FastAPI):
        raise RuntimeError(
            "Improperly configured: FastAPI instance passed instead of LangChain interface"
        )
    for lang_app in lc_apps:
        chain = import_from_string(lang_app)
        if isinstance(chain, types.FunctionType):
            chain = FnWrapper(chain)
        inn, out = derive_fields(chain)
        logger.debug(f"inputs:{inn=}")
        logger.info(f"{lang_app=}:{chain.__class__.__name__}({inn})")
        endpoint_prefix = lang_app.replace(":", ".")
        cls_name = "".join([c.capitalize() for c in endpoint_prefix.split(".")])
        request_cls = derive_class(cls_name, inn, add_memory=chain.memory)
        logger.debug(f"{request_cls=}")

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
