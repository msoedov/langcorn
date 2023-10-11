from typing import Any

from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chains.base import Chain


class CustomChain(Chain):
    input_key: str = "input"
    output_key: str = "output"

    def _call(
        self,
        inputs: dict[str, Any],
        run_manager: CallbackManagerForChainRun | None = None,
    ) -> dict[str, str]:
        print("input:", inputs)
        return {self.output_key: "Hello", "other": "test"}

    @property
    def input_keys(self) -> list[str]:
        return [self.input_key]

    @property
    def output_keys(self) -> list[str]:
        """Meta private."""
        return [self.output_key, "other"]


chain = CustomChain()
