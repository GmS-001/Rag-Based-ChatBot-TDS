from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain.retrievers import MultiQueryRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from typing import Annotated, TypedDict
from prompts import RAG_PROMPT, INITIAL_PROMPT
from dotenv import load_dotenv
from config import CONFIG

load_dotenv()
llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash", temperature=0.2)
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001",transport="rest")
vector_store = FAISS.load_local("tds_index", embedding_model, allow_dangerous_deserialization=True)
multiqueryretriver = MultiQueryRetriever.from_llm(
    retriever = vector_store.as_retriever(search_type="similarity",search_kwargs = {'k' : 4}),
    llm = llm
)
parser = StrOutputParser()
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def format_docs(retrieved_docs):
  context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
  return context_text

async def process_image(image):
    if not isinstance(image, str):
        print(f"[ERROR] Expected base64 string, but got: {type(image)}")
        return ""

    if image is None or image == "":
        return None
    

def chat_node(state : ChatState) : 
    if len(state['messages']) == 1 :
        state["messages"].insert(0,SystemMessage(content= INITIAL_PROMPT))
    messages = state['messages']
    history = messages[:-1]
    question = messages[-1].content
    print('\nHistory : ',history)
    print('\nQuestion : ',question)
    # Get context separately
    try : 
        retrieved_docs = multiqueryretriver.invoke(question)
        context = format_docs(retrieved_docs)   
        # Format prompt with all required variables
        formatted_prompt = RAG_PROMPT.invoke({
            "question": question,
            "context": context,
            "history": history
        })
        chain = llm | parser
        response = chain.invoke(formatted_prompt)
    except Exception as e :
        print("Error : ",e)
    return {"messages": [AIMessage(content=response)]}



checkpointer = InMemorySaver()
graph = StateGraph(ChatState)
graph.add_node('Chat Node',chat_node)
graph.add_edge(START, "Chat Node")
graph.add_edge("Chat Node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# # ---- Seed the INITIAL PROMPT once ----
# initial_state = {"messages": [SystemMessage(content=INITIAL_PROMPT)]}
# chatbot.invoke(initial_state,CONFIG)   # writes the initial prompt to memory