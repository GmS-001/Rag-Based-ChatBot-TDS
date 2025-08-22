import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage
from backend_basic import chatbot
from prompts import INITIAL_PROMPT
from config import CONFIG

# to store session state we make thread in a config dict

if 'message_history' not in st.session_state : 
    st.session_state['message_history'] = [SystemMessage(content = INITIAL_PROMPT)]

# UI starts 
st.title("✨Rag Based ChatBot✨")
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

    response = chatbot.invoke({"messages": [HumanMessage(content=user_input)]}, config=CONFIG)
    message = response['messages'][-1].content
    print('Response',message)
    # message = response.content if hasattr(response, "content") else response['messages'][-1].content
    # storing messages in the message history
    st.session_state['message_history'].append(AIMessage(content=message))

    with st.chat_message('assistant') :
        st.text(message)


# uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png","wav", "mp3", "m4a"])