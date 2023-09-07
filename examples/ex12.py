from typing import List

from langchain import LLMChain, PromptTemplate
from langchain.llms import HuggingFacePipeline, OpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, validator


class Joke(BaseModel):
    setup: str = Field(description="question to set up a joke")
    punchline: str = Field(description="answer to resolve the joke")

    # You can add custom validation logic easily with Pydantic.
    @validator("setup")
    def question_ends_with_question_mark(cls, field):
        if field[-1] != "?":
            raise ValueError("Badly formed question!")
        return field


llm = OpenAI(temperature=0)
joke_query = "Tell me a joke."

parser = PydanticOutputParser(pydantic_object=Joke)

prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

_input = prompt.format_prompt(query=joke_query)

chain = LLMChain(llm=llm, prompt=prompt, verbose=True)


# Run the chain only specifying the input variable.


def run(query: str) -> Joke:
    output = chain.run(query)
    return parser.parse(output)


if __name__ == "__main__":
    print(run(joke_query))
