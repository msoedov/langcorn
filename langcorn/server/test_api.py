import numpy as np
import pytest
from fastapi.testclient import TestClient
from loguru import logger

from .api import create_service


FN_PORT = 7172


client = TestClient(create_service("examples.ex1:chain"))


@pytest.fixture(
    scope="session",
)
def fn_executor():
    yield None


class TestRoutes:
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
