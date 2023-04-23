from fastapi import FastAPI
from langcorn import create_service

app: FastAPI = create_service("examples.ex2:chain", "examples.ex1:chain")
