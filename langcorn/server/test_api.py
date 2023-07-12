from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from langchain.llms.fake import FakeListLLM

from examples import app

from .api import create_service

client = TestClient(create_service("examples.ex1:chain"))


@pytest.fixture(autouse=True)
def suppress_openai():
    llm = FakeListLLM(responses=["FakeListLLM" for i in range(100)])
    with patch("langchain.llms.OpenAI._generate", new=llm._generate), patch(
        "langchain.llms.OpenAI._agenerate", new=llm._agenerate
    ):
        yield


@pytest.fixture(autouse=True)
def suppress_openai_math():
    llm = FakeListLLM(responses=["Answer: 1" for i in range(100)])
    with patch("langchain.llms.OpenAI._generate", new=llm._generate), patch(
        "langchain.llms.OpenAI._agenerate", new=llm._agenerate
    ):
        yield


@pytest.fixture(autouse=True)
def example_app():
    yield TestClient(app.app)


@pytest.fixture(
    scope="session",
)
def fn_executor():
    yield None


class TestRoutes:
    def test_examples(self, example_app):
        response = example_app.get("/")
        assert response.status_code == 404

    def test_read_main(self):
        response = client.get("/")
        assert response.status_code == 404

    def test_state(self):
        response = client.get("/ht")
        assert response.status_code == 200
        assert response.json()

    # TODO: add error handling
    @pytest.mark.parametrize(
        "apps",
        [("examples.ex1:chain",), ("examples.ex2:chain", "examples.ex1:chain")],
    )
    def test_create_service(self, apps):
        client = TestClient(create_service(*apps))
        response = client.get("/")
        assert response.status_code == 404

    def test_chain_x(self, suppress_openai, example_app):
        response = example_app.post("/examples.ex8.qa/run", json=dict(query="query"))
        assert response.status_code == 200, response.text
        assert response.json()

    @pytest.mark.parametrize(
        "endpoint, query",
        [
            ("/examples.ex1.chain/run", dict(product="QUERY")),
            (
                "/examples.ex2.chain/run",
                dict(
                    input="QUERY",
                    url="https://github.com/msoedov/langcorn/blob/main/examples/ex7_agent.py",
                ),
            ),
            # ("/examples.ex3.chain/run", dict(question="QUERY")),  # requires llm response format
            (
                "/examples.ex4.sequential_chain/run",
                dict(
                    query="QUERY",
                    url="https://github.com/msoedov/langcorn/blob/main/examples/ex7_agent.py",
                ),
            ),
            (
                "/examples.ex5.conversation/run",
                dict(input="QUERY", history="", memory=[]),
            ),
            (
                "/examples.ex6.conversation_with_summary/run",
                dict(input="QUERY", history="", memory=[]),
            ),
            # ("/examples.ex7_agent.agent/run", dict(input="QUERY")), # requires llm response format
            ("/examples.ex8.qa/run", dict(query="QUERY")),
        ],
    )
    def test_chain_e2e(self, suppress_openai, example_app, endpoint, query):
        response = example_app.post(endpoint, json=dict(**query))
        assert response.status_code == 200, response.text
        assert response.json()

    def test_double_chain(self, suppress_openai_math, example_app):
        client = TestClient(
            create_service(
                "examples.ex9_double_chain:chain1", "examples.ex9_double_chain:chain2"
            )
        )
        response = client.post(
            "/examples.ex9_double_chain.chain1/run", json=dict(question="QUERY")
        )
        assert response.status_code == 200, response.text
        assert response.json()
        response = client.post(
            "/examples.ex9_double_chain.chain2/run", json=dict(question="QUERY")
        )
        assert response.status_code == 200, response.text
        assert response.json()
