from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage
from typing import Annotated,TypedDict
from dotenv import load_dotenv

load_dotenv()
llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash")

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state : ChatState) : 
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

checkpointer = InMemorySaver()
graph = StateGraph(ChatState)
graph.add_node('Chat Node',chat_node)
graph.add_edge(START, "Chat Node")
graph.add_edge("Chat Node", END)

chatbot = graph.compile(checkpointer=checkpointer)

