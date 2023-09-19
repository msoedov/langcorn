from fastapi import FastAPI

from langcorn import create_service

app: FastAPI = create_service(
    "examples.ex1:chain",
    "examples.ex2:chain",
    "examples.ex3:chain",
    "examples.ex4:sequential_chain",
    "examples.ex5:conversation",
    "examples.ex6:conversation_with_summary",
    "examples.ex7_agent:agent",
    "examples.ex8:qa",
    "examples.ex9_double_chain:chain1",
    "examples.ex9_double_chain:chain2",
    "examples.ex10_cc:chain",
    "examples.ex12:run",
    "examples.ex13:chain",
    "examples.ex14:chain",
)
