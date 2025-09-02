import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, AIMessageChunk
from backend_basic import chatbot
from database_utils import add_user, verify_user, add_thread_for_user, retrieve_user_threads, create_tables
import uuid
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()  # Loads .env for local dev

GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))
create_tables()

def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread_for_user(thread_id, st.session_state['username'])
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].insert(0, thread_id)
    st.session_state['message_history'] = []
    st.session_state['current_thread_id'] = thread_id 

def load_conversation(thread_id):
    """Loads a past conversation from the selected thread."""
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    st.session_state['message_history'] = state.values.get('messages', [])
    st.session_state['current_thread_id'] = thread_id # Set the active thread



st.title("✨ RAG-Based ChatBot ✨")


if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.header("Login / Register")
    login_tab, register_tab = st.tabs(["Login", "Register"])

   
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if verify_user(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.rerun() # Rerun the script to show the main chat UI
                else:
                    st.error("Invalid username or password.")

   
    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("Choose a Username")
            new_password = st.text_input("Choose a Password", type="password")
            submitted = st.form_submit_button("Register")
            if submitted:
                success, message = add_user(new_username, new_password)
                if success:
                    st.success(message)
                    st.info("Please go to the Login tab to sign in.")
                else:
                    st.error(message)


else:
   
    if 'username' in st.session_state:
        st.sidebar.success(f"Logged in as **{st.session_state['username']}**")

        # Load user's threads for the first time
        if 'chat_threads' not in st.session_state:
            st.session_state['chat_threads'] = retrieve_user_threads(st.session_state['username'])

        # If no current thread is selected, or on first login, create one
        if 'current_thread_id' not in st.session_state:
            if not st.session_state['chat_threads']:
                reset_chat() # Create the first chat thread
            else:
                load_conversation(st.session_state['chat_threads'][-1])

    
    st.sidebar.header('My Conversations')
    st.sidebar.button('Start a New Chat', on_click=reset_chat, key="new_chat_btn")

    # Use enumerate to create a numbered list of chats for the sidebar buttons
    total = len(st.session_state['chat_threads'])
    for i, thread_id in enumerate(reversed(st.session_state['chat_threads'])):
        is_current = (thread_id == st.session_state.get('current_thread_id'))
        button_label = f"🔵 Chat {total - i}" if is_current else f"Chat {total - i}"
        if st.sidebar.button(button_label, key=thread_id):
            load_conversation(thread_id)
            st.rerun()

            
    
    if st.sidebar.button("Logout"):
        # Clear the entire session state
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

# Display past messages first (not the new one)
    if 'message_history' in st.session_state:
        for message in st.session_state['message_history']:
            if isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.write(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message("assistant"):
                    st.write(message.content)

    # If user types something new
    user_input = st.chat_input("Type here...")
    if user_input:
        # Show user message
        st.session_state['message_history'].append(HumanMessage(content=user_input))
        with st.chat_message("user"):
            st.write(user_input)

        # Stream assistant response
        response_text = ""
        with st.chat_message("assistant"):
            response_box = st.empty()
            CONFIG = {'configurable': {'thread_id': st.session_state['current_thread_id']}}
            for message_chunk, _ in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            ):
                if isinstance(message_chunk, AIMessageChunk) and message_chunk.content:
                    response_text += message_chunk.content
                    response_box.markdown(response_text)

        # Append only once
        st.session_state['message_history'].append(AIMessage(content=response_text))