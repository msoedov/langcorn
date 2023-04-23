from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryMemory

llm = OpenAI(temperature=0)
conversation_with_summary = ConversationChain(
    llm=llm, memory=ConversationSummaryMemory(llm=OpenAI()), verbose=True
)

if __name__ == "__main__":
    conversation_with_summary.predict(input="Hi, what's up?")
