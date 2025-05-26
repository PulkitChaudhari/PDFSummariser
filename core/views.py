from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain import hub
from langchain.chat_models import init_chat_model

def process_pdf(file_path):
    # Load the PDF file
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    # Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100, chunk_overlap=0, add_start_index=True
    )
    all_splits = text_splitter.split_documents(docs)

    # Create embeddings and vector store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(documents=all_splits)

    # Initialize LLM and get summary
    llm = init_chat_model("gpt-4", model_provider="openai")
    prompt = hub.pull("rlm/rag-prompt")
    
    # Get summary of skills
    messages = prompt.invoke({
        "question": "Summarise skills of this candidate for me.",
        "context": "\n\n".join(doc.page_content for doc in all_splits)
    })
    response = llm.invoke(messages)
    
    return response.content

@csrf_exempt
def home(request):
    if request.method == 'POST' and request.FILES.get('pdf'):
        pdf_file = request.FILES['pdf']
        
        # Create a temporary file to store the uploaded PDF
        temp_path = f"/tmp/{pdf_file.name}"
        with open(temp_path, 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)
        
        try:
            # Process the PDF and get summary
            summary = process_pdf(temp_path)
            
            # Clean up the temporary file
            os.remove(temp_path)
            
            return JsonResponse({
                'status': 'success',
                'summary': summary
            })
        except Exception as e:
            # Clean up the temporary file in case of error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return render(request, 'home.html')
