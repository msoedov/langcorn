import os

from langchain.chains import LLMMathChain
from langchain.llms import OpenAI

os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "sk-********")

llm = OpenAI(temperature=0)
chain = LLMMathChain.from_llm(llm=llm, verbose=True)

if __name__ == "__main__":
    chain.run("What is 13 raised to the .3432 power?")
