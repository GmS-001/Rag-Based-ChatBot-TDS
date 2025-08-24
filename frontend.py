# frontend_basic.py (replace the entire file with this)

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
# --- Import the new backend functions ---
from backend_basic import (
    chatbot, 
    add_user, 
    verify_user, 
    add_thread_for_user, 
    retrieve_user_threads
)
import uuid

# --- Utility Functions (mostly unchanged) ---
def generate_thread_id():
    return str(uuid.uuid4())

# --- Modified Functions to handle the logged-in user ---

def reset_chat():
    """Creates a new chat thread for the logged-in user."""
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    # Link the new thread to the current user
    add_thread_for_user(thread_id, st.session_state['username'])
    # Add the new thread to the list of threads for the UI
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].insert(0, thread_id)
    st.session_state['message_history'] = []
    st.session_state['current_thread_id'] = thread_id # Track the active thread

def load_conversation(thread_id):
    """Loads a past conversation from the selected thread."""
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    st.session_state['message_history'] = state.values.get('messages', [])
    st.session_state['current_thread_id'] = thread_id # Set the active thread

# --- Main Application Logic ---

st.title("✨ RAG-Based ChatBot ✨")

# === 1. LOGIN/REGISTRATION UI ===
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.header("Login / Register")
    login_tab, register_tab = st.tabs(["Login", "Register"])

    # --- Login Form ---
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

    # --- Registration Form ---
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

# === 2. MAIN CHATBOT UI (shown only after login) ===
else:
    # --- Session State Initialization for a logged-in user ---
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
                # Load the most recent conversation by default
                load_conversation(st.session_state['chat_threads'][0])

    # --- Sidebar for Conversations ---
    st.sidebar.header('My Conversations')
    st.sidebar.button('Start a New Chat', on_click=reset_chat, key="new_chat_btn")

    for thread_id in st.session_state['chat_threads']:
        # Use a more descriptive name, like the first user message, or just keep it simple
        if st.sidebar.button(f"Chat {thread_id[:8]}...", key=thread_id):
            load_conversation(thread_id)
            
    # --- Logout Button ---
    if st.sidebar.button("Logout"):
        # Clear the entire session state
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()


    # --- Chat Interface ---
    
    # Display message history
    if 'message_history' in st.session_state:
        for message in st.session_state['message_history']:
            if isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.write(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message("assistant"):
                    st.write(message.content)

    # Handle new user input
    user_input = st.chat_input('Type here...')
    if user_input:
        # Append and display the new user message
        st.session_state['message_history'].append(HumanMessage(content=user_input))
        with st.chat_message('user'):
            st.write(user_input)

        # Configure LangGraph with the current thread ID
        CONFIG = {'configurable': {'thread_id': st.session_state['current_thread_id']}}

        # Stream and display the AI response
        with st.chat_message('assistant'):
            ai_message_content = ""
            for chunk in chatbot.stream({'messages': [HumanMessage(content=user_input)]}, config=CONFIG):
                # The response from your graph is in chunk['Chat Node']['messages'][-1].content
                content_part = chunk.get('Chat Node', {}).get('messages', [{}])[-1].content
                if content_part:
                    ai_message_content += content_part
                    st.write(ai_message_content)

        # Append the complete AI message to history
        if ai_message_content:
            st.session_state['message_history'].append(AIMessage(content=ai_message_content))