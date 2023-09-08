from langchain.chains import create_extraction_chain
from langchain.llms import OpenAI

schema = {
    "properties": {
        "name": {"type": "string"},
        "height": {"type": "integer"},
        "hair_color": {"type": "string"},
    },
    "required": ["name", "height"],
}

# Input
inp = """Alex is 5 feet tall. Claudia is 1 feet taller Alex and jumps higher than him. Claudia is a brunette and Alex is blonde."""

# Run chain

llm = OpenAI(temperature=0)

chain = create_extraction_chain(schema, llm, verbose=True)

if __name__ == "__main__":
    chain.run(input=inp)
