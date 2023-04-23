from fastapi import FastAPI
from langcorn import create_service
from langcorn import create_ws_service

app: FastAPI = create_service(
    "examples.ex1:chain",
    "examples.ex2:chain",
    "examples.ex3:chain",
    "examples.ex4:sequential_chain",
    "examples.ex5:conversation",
    "examples.ex6:conversation_with_summary",
)

app = create_ws_service(
    "examples.ex5:conversation",
    "examples.ex6:conversation_with_summary",
    app=app,
)
