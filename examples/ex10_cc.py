from typing import Any, Dict, List, Optional

from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chains.base import Chain


class CustomChain(Chain):
    input_key: str = "input"
    output_key: str = "output"

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        print("input:", inputs)
        return {self.output_key: "Hello", "other": "test"}

    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """:meta private:"""
        return [self.output_key, "other"]


chain = CustomChain()
