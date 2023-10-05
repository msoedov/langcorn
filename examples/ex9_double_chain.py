import os

from langchain.chains import LLMMathChain
from langchain.llms import OpenAI

os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "sk-********")

llm = OpenAI(temperature=0)
chain1 = LLMMathChain.from_llm(llm=llm, verbose=True)
chain2 = LLMMathChain.from_llm(llm=llm, verbose=True)
