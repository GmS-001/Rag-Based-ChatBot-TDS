import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage
from backend_basic import chatbot, retrieve_all_threads
import uuid


#utility functions
def generate_thread_id() :
    return uuid.uuid4()


def reset_chat() :
    thread_id = generate_thread_id() 
    st.session_state['thread_id'] = thread_id 
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id) :
    if thread_id not in st.session_state['chat_threads'] : 
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])


# Initial Setup
if 'message_history' not in st.session_state : 
    st.session_state['message_history'] = []
# generating new thread id using uuid()
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
# creating list of all thread ids
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

add_thread(st.session_state['thread_id'])

# UI starts 
st.title("✨Rag Based ChatBot✨")

# Sidebar
st.sidebar.header('My Conversations')
# all convos
for thread_id in st.session_state['chat_threads'][::-1] :
    if st.sidebar.button(str(thread_id)) : 
        st.session_state['message_history']  = load_conversation(thread_id)

st.sidebar.button('Start a New Chat', on_click=reset_chat, key="new_chat_btn")
 


# loading messages..
for message in st.session_state['message_history'] :
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(message.content)

user_input = st.chat_input('Type here...')
if user_input :

    st.session_state['message_history'].append(HumanMessage(content = user_input))
    with st.chat_message('user') : 
        st.text(user_input)


    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    # neha part implemented
    response_text = ""
    with st.chat_message('assistant'):
        response_box = st.empty()
        for message_chunk, _ in chatbot.stream({'messages': [HumanMessage(content = user_input)]}, config=CONFIG, stream_mode='messages'):
            response_text += message_chunk.content
            response_box.markdown(response_text)

    st.session_state['message_history'].append(AIMessage(content = response_text))

    # my part _GMS
    # with st.chat_message('assistant') :
    #     ai_message = st.write_stream(
    #         message_chunk.content for message_chunk,metadata in chatbot.stream(
    #             {'messages' : [HumanMessage(content = user_input)]},
    #             config = CONFIG,
    #             stream_mode = 'messages'
    #         )
    #     )
    # print('Message from AI : ',ai_message)
    
    # st.session_state['message_history'].append(AIMessage(content=ai_message))