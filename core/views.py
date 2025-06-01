import json
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from typing import Dict, List
from langchain_core.messages import AIMessage

class NotApproved(Exception):
    """Custom exception."""

def human_approval(msg):
    """Responsible for approving whether to send email to the candidate.

    Args:
        msg: output from the chat model

    Returns:
        msg: original output from the msg
    """
    tool_strs = "\n\n".join(
        json.dumps(tool_call, indent=2) for tool_call in msg.tool_calls
    )
    # Instead of using input(), we'll raise a special exception
    # that will be caught by the view to show the approval UI
    raise ApprovalRequired(f"Tool invocations require approval:\n\n{tool_strs}")

class ApprovalRequired(Exception):
    """Exception raised when human approval is required."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

@tool
def send_email(message: str, recipient: str) -> str:
    """Dummy function for Sending an e-mail to candidate."""
    print("Send mail called")
    return f"Successfully sent email to {recipient}."

tools = [send_email]

def call_tools(msg: AIMessage) -> List[Dict]:
    """Simple sequential tool calling helper."""
    tool_map = {tool.name: tool for tool in tools}
    tool_calls = msg.tool_calls.copy()
    for tool_call in tool_calls:
        tool_call["output"] = tool_map[tool_call["name"]].invoke(tool_call["args"])
    return tool_calls

def process_pdf(file_path: str):
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
    llm = init_chat_model("gpt-4o-mini", model_provider="openai")
    llm_with_tools = llm.bind_tools(tools)
    chain = llm_with_tools | human_approval | call_tools
    
    try:
        response = chain.invoke("Send email to this candidate for me saying He is hired.")
        return response.content
    except ApprovalRequired as e:
        return {
            "requires_approval": True,
            "approval_message": str(e)
        }

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
            # result = process_pdf(temp_path)
            result = {
                "requires_approval": True,
                "approval_message": "Tool invocations require approval:\n\n"
            }
            
            # Clean up the temporary file
            os.remove(temp_path)
            
            if isinstance(result, dict) and result.get("requires_approval"):
                return JsonResponse({
                    'status': 'success',
                    'summary': result["approval_message"],
                    'requires_approval': True
                })
            else:
                return JsonResponse({
                    'status': 'success',
                    'summary': result,
                    'requires_approval': False
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

@csrf_exempt
def handle_decision(request):
    if request.method == "POST":
        data = json.loads(request.body)
        decision = data.get('decision')
        
        if decision == "Y":
            # Handle Yes decision
            return JsonResponse({
                "status": "success",
                "message": "Candidate has been approved and email will be sent!"
            })
        elif decision == "N":
            # Handle No decision
            return JsonResponse({
                "status": "success",
                "message": "Candidate has been rejected. No email will be sent."
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": "Invalid decision"
            })
    
    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    })
