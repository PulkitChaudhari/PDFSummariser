# This python file is used to perform Semantic Similarity Search on a PDF file like a resume

import getpass
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore


os.environ["LANGSMITH_TRACING"] = "true"
if not os.environ.get("LANGSMITH_API_KEY"):
    os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter Langsmith API Key: ")

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

# Load the PDF file
file_path = "/Users/pulkitchaudhari/Downloads/PulkitChaudhariResume.pdf"
loader = PyPDFLoader(file_path)

docs = loader.load()

print("Length of docs: ", len(docs))

# Split the documents into chunks based on seperator
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200, chunk_overlap=10, add_start_index=True
)

all_splits = text_splitter.split_documents(docs)
for split in all_splits:
   print(split.page_content + "\n\n")

# Create embeddings for the chunks
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Create a vector store to store the embeddings
vector_store = InMemoryVectorStore(embeddings)

# Add the chunks to the vector store
ids = vector_store.add_documents(documents=all_splits)

# # Search for the most similar chunks
# results = vector_store.similarity_search_with_score(
#     "Tell me about MFkarr project?"
# )

# print(results[0])

# # Search for the most similar chunks
# results = vector_store.similarity_search_with_score(
#     "Give me a skills summary of the person in the resume?"
# )

# print(results[0])



