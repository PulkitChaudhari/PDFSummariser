import getpass
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.schema import Document
from langchain import hub
from langgraph.graph import START, StateGraph
from typing import List, TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

class PDFAgent:
   
    textSplitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0, add_start_index=True)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = InMemoryVectorStore(embeddings)
    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = hub.pull("rlm/rag-prompt")

    def __init__(self):
        os.environ["LANGSMITH_TRACING"] = "true"
        if not os.environ.get("LANGSMITH_API_KEY"):
            os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter Langsmith API Key: ")

        if not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

    def retrieve(self,state: State):
        results = self.vector_store.similarity_search(state["question"])
        return {"context": results}

    def generate(self,state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = self.prompt.invoke({"question": state["question"], "context": docs_content})
        response = self.llm.invoke(messages)
        return {"answer": response.content}
    
    def build_graph(self):
        graph_builder = StateGraph(State).add_sequence([self.retrieve, self.generate])
        graph_builder.add_edge(START, "retrieve")
        graph = graph_builder.compile()
        return graph

    
    def process_pdf(self,filepath):
        loader = PyPDFLoader(filepath)
        docs = loader.load()

        all_splits = self.textSplitter.split_documents(docs)
        _ = self.vector_store.add_documents(documents=all_splits)

        graph = self.build_graph()

        response = graph.invoke({"question": "What is this file about?"})
        print(response["answer"])
        return response["answer"]