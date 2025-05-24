
import getpass
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain import hub
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain.chat_models import init_chat_model

os.environ["LANGSMITH_TRACING"] = "true"
if not os.environ.get("LANGSMITH_API_KEY"):
    os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter Langsmith API Key: ")

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

# Load the PDF file
file_path = "/Users/pulkitchaudhari/Downloads/PulkitChaudhariResume.pdf"
loader = PyPDFLoader(file_path)

docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100, chunk_overlap=0, add_start_index=True
)

all_splits = text_splitter.split_documents(docs)
print(all_splits)

# Create embeddings for the chunks
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Create a vector store to store the embeddings
vector_store = InMemoryVectorStore(embeddings)

# Add the chunks to the vector store
ids = vector_store.add_documents(documents=all_splits)
llm = init_chat_model("gpt-4o-mini", model_provider="openai")

prompt = hub.pull("rlm/rag-prompt")

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
   

def retrieve(state: State):
   results = vector_store.similarity_search(state["question"])
   return {"context": results}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

response = graph.invoke({"question": "Summarise skills of this candidate for me."})
print(response["answer"])