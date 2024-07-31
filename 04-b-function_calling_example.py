import random
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import END
from typing import Any, Dict, Type, TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator
from langchain_core.tools import tool
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain.prompts import PromptTemplate
# Import tools from tools.py
from tools import get_current_weather, get_system_time

# using OllamaFunctions from experimental because it supports function binding with llms
model = OllamaFunctions(
    base_url="http://ai.mtcl.lan:11436",
    model="gemma2:27b", #dolphin-llama3:70b #gemma2:27b-instruct-q8_0 #qwen2:72b
    format="json"
    )

model_with_tools = model.bind_tools(
    tools=[get_current_weather, get_system_time],
)

tool_mapping = {
    'get_current_weather': get_current_weather,
    'get_system_time': get_system_time,
}

messages = [HumanMessage("What is the weather in Chicago IL?")]
llm_response = model_with_tools.invoke(messages)
messages.append(llm_response)


# Define prompt
prompt = PromptTemplate(
    template="""system
    You are a smart Agent. You are a master at understanding what a customer wants and utilize available tools only if you have to.

    user
    Conduct a comprehensive analysis of the request provided\

    USER REQUEST:\n\n {initial_request} \n\n
    
    assistant
    """,
    input_variables=["initial_request"],
)

agent_request_generator = prompt | model_with_tools

result = agent_request_generator.invoke(
    {"initial_request": "What is the weather in woodbury in MN?"}
    )

# Extract the last AI message from messages
last_ai_message = None
if isinstance(result, AIMessage):
    last_ai_message = result

# print("Last AI Message:", last_ai_message)

if last_ai_message and hasattr(last_ai_message, 'tool_calls'):
    # print("Tool Calls:", last_ai_message.tool_calls)
    print("tool name :: ", last_ai_message.tool_calls[-1]["name"])
    print("tool args :: ", last_ai_message.tool_calls[-1]["args"])
else:
    print("No tool calls found.")