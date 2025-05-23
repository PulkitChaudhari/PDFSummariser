# This python file is used to perform Semantic Similarity Search on a PDF file like a resume

import getpass
import os
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.tools.tavily_search import TavilySearchResults

# Setting API Keys
os.environ["LANGSMITH_TRACING"] = "true"
if not os.environ.get("LANGSMITH_API_KEY"):
    os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter Langsmith API Key: ")

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

if not os.environ.get("TAVILY_API_KEY"):
  os.environ["TAVILY_API_KEY"] = getpass.getpass("Enter Tavily API key: ")

# Creating a tool to search the web for the weather in Kalyan
search = TavilySearchResults(max_results=2)
# search_results = search.invoke("what is the weather in Kalyan?")
# print(search_results)

# Creating a list of tools that will be used by the agent
tools = [search]

# Creating a model to use for the agent
model = init_chat_model("gpt-4", model_provider="openai")

# Binding the tools to the model and calling the model with prompt that invokes the tool
# model_with_tools = model.bind_tools(tools)

# response = model_with_tools.invoke([HumanMessage(content="What's the weather in Kalyan?")])

# print(f"ContentString: {response.content}")
# print(f"ToolCalls: {response.tool_calls}")

#Creating an agent executor that will be used to invoke the model
agent_executor = create_react_agent(model, tools)

# response = agent_executor.invoke(
#     {"messages": [HumanMessage(content="Whats the weather in Kalyan?")]}
# )
# print(response["messages"])

# # Streaming the agent executor so as not to make the user wait for the response
# for step in agent_executor.stream(
#     {"messages": [HumanMessage(content="whats the weather in Kalyan?")]},
#     stream_mode="values",
# ):
#     step["messages"][-1].pretty_print()

# #Introducing memory saver to remember the conversation history
memory = MemorySaver()
agent_executor = create_react_agent(model, tools, checkpointer=memory)

config = {"configurable": {"thread_id": "abc123"}}
for chunk in agent_executor.stream(
    {"messages": [HumanMessage(content="hi im Pulkit!")]}, config
):
    print(chunk)
    print("----")

for chunk in agent_executor.stream(
    {"messages": [HumanMessage(content="whats my name?")]}, config
):
    print(chunk)
    print("----")

# #Changing the thread id to a new one so as to demonstrate the agent forgetting my name
config1 = {"configurable": {"thread_id": "xyz123"}}
for chunk in agent_executor.stream(
    {"messages": [HumanMessage(content="whats my name?")]}, config1
):
    print(chunk)
    print("----")