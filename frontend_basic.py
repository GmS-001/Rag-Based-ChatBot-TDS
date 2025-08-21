import streamlit as st
from langchain_core.messages import HumanMessage
from backend_basic import chatbot

# to store session state we make thread in a config dict
CONFIG = {'configurable' : {'thread_id' : 'thread-1'}}
if 'message_history' not in st.session_state : 
    st.session_state['message_history'] = []

# UI starts 
# loading messages..
st.title("✨Rag Based ChatBot✨")
for message in st.session_state['message_history'] :
    with st.chat_message(message['role']):
        st.text(message['content'])

#{'role': 'user', 'content': 'Hi'}
#{'role': 'assistant', 'content': 'Hi=ello'}
user_input = st.chat_input('Type here...')
if user_input :
    st.session_state['message_history'].append({'role' : 'user','content' : user_input})
    with st.chat_message('user') : 
        st.text(user_input)

    response = chatbot.invoke({'messages' : [HumanMessage(content = user_input)]}, config = CONFIG)
    message = response['messages'][-1].content
    # storing messages in the message history
    st.session_state['message_history'].append({'role': 'assistant', 'content': message})
    with st.chat_message('assistant') :
        st.text(message)


uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png","wav", "mp3", "m4a"])