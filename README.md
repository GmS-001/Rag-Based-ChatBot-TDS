# ✨ RAG-Based Virtual Teaching Assistant

A **Retrieval-Augmented Generation (RAG)** powered chatbot built for the **Tools in Data Science (TDS)** course at **IIT Madras**.  
This virtual assistant provides **accurate, context-aware answers** to students' queries using course materials, while also being capable of answering general knowledge questions gracefully.  

Built with **LangGraph**, **LangChain**, **LangSmith**, **Streamlit**,**Selenium** and a **SQLite backend**, this project demonstrates a **production-grade RAG application** with authentication, conversation threading, and persistent chat history.

---

## 🚀 Features

- **Context-Aware Responses (RAG)**  
  Answers are based on retrieved chunks from course content first, ensuring accuracy and reliability.

- **Fallback General Knowledge Answers**  
  When no course context is available, the bot clearly states this and provides helpful responses using general reasoning.

- **LangSmith-Backed LLM Tracing & Analysis**  
  Used **LangSmith** to monitor, debug, and optimize LLM calls for better transparency and reliability in production.

- **Interactive Streamlit Frontend**  
  - Chat-like UI for students.  
  - Live message streaming.  
  - Sidebar for switching between chat threads.  

- **User Authentication & Conversation Management**  
  - Login/registration system with secure password storage.  
  - Each user has multiple conversation threads, all persisted in a SQLite database.

- **Well-Structured Backend**  
  - Modular design (`frontend`, `backend`, `database_utils`, `prompts`) for scalability.  
  - Easy to extend with new models, retrievers, or UI features.

---

## 🗂️ Project Structure

```plaintext
├── backend_basic.py      # Core RAG pipeline: retrieval & LLM integration
├── database_utils.py     # SQLite utilities: user auth, chat history, threads
├── frontend.py           # Streamlit app for chat interface
├── prompts.py            # System prompts and configurations
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
└── .gitignore            # Ignored files (db, cache, venv, etc.)
