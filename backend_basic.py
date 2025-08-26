from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage 
from langchain.retrievers import MultiQueryRetriever
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langsmith import traceable
from typing import Annotated, TypedDict
from prompts import RAG_PROMPT, INITIAL_PROMPT
from dotenv import load_dotenv
import os
import sqlite3 # to maka sqlite db


os.environ["LANGCHAIN_PROJECT"] = 'Checking Prompts'

load_dotenv()
llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash", temperature=0.2)
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001",transport="rest")
vector_store = FAISS.load_local("tds_index", embedding_model, allow_dangerous_deserialization=True)
compressor = LLMChainExtractor.from_llm(llm)
parser = StrOutputParser()

retriever = vector_store.as_retriever(search_type="similarity",search_kwargs = {'k':4})
mmr = vector_store.as_retriever(search_type="mmr",search_kwargs = {'k' : 5,'lambda_mult' : 0.5})
multiqueryretriver = MultiQueryRetriever.from_llm(retriever = retriever,llm = llm)

ccr_retriever = ContextualCompressionRetriever(base_retriever = retriever,base_compressor = compressor)
ccr_mmr = ContextualCompressionRetriever(base_retriever = mmr,base_compressor = compressor)
ccr_multiqueryretriver = ContextualCompressionRetriever(base_retriever = multiqueryretriver,base_compressor = compressor)

@traceable(name = 'get_final_prompt',metadata = {'k' : 4})
def get_final_prompt(retriever,question,history) :
    retrieved_docs = retriever.invoke(question)
    context = format_docs(retrieved_docs)
    formatted_prompt = RAG_PROMPT.invoke({"question": question,"context": context, "history": history})
    return formatted_prompt

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

@traceable(name = 'format_docs')
def format_docs(retrieved_docs):
  context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
  return context_text


def chat_node(state : ChatState) : 
    if len(state['messages']) == 1 :
        state["messages"].insert(0,SystemMessage(content= INITIAL_PROMPT))
    messages = state['messages']
    history = messages[:-1]
    question = messages[-1].content
    try : 
        formatted_prompt =  get_final_prompt(retriever, question, history) 
        chain = llm | parser
        response = chain.invoke(formatted_prompt)

        if not response or response.strip() == "":
            response = "I'm sorry, I couldn't generate a proper response. Could you please rephrase your question?"
            
    except Exception as e:
        print(f"Error in chat_node: {e}")
        response = "I encountered an error processing your request. Please try again."

    return {"messages": [AIMessage(content=response)]}


conn = sqlite3.connect(database = 'chatbot.db', check_same_thread = False) # check_same_thread - this does not give error because we will work on multiple threads but sqlite workd on just one thread
checkpointer = SqliteSaver(conn = conn)
graph = StateGraph(ChatState)
graph.add_node('Chat Node',chat_node)
graph.add_edge(START, "Chat Node")
graph.add_edge("Chat Node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# def retrieve_all_threads():
#     all_threads = set()
#     for checkpoint in checkpointer.list(None):
#         all_threads.add(checkpoint.config['configurable']['thread_id'])

#     return list(all_threads)
# --- Database Setup and User Management ---

