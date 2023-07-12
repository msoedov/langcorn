import os
import sys

import fire
import uvicorn

from langcorn.server import api


class T:
    def server(self, *lc: str, port=8718, auth_token=""):
        sys.path.append(os.path.dirname("."))
        app = api.create_service(*lc, auth_token=auth_token)
        config = uvicorn.Config(app, port=port, log_level="info")
        server = uvicorn.Server(config)
        server.run()
        return


def entrypoint():
    fire.Fire(T())


if __name__ == "__main__":
    entrypoint()
