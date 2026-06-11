import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

# Load environmental variables
load_dotenv()

from pdf_processor import PDFProcessor
from vector_store import VectorStoreManager
from chatbot import ChatBot

# Page configuration
st.set_page_config(
    page_title="PDF QA Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Custom Premium CSS Injection for Glassmorphic Dark UI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

/* Main App Wrapper */
.stApp {
    background: radial-gradient(circle at 50% 50%, #0f172a 0%, #020617 100%) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #f8fafc !important;
}

/* Force light/white text colors on all standard text wrappers to prevent black text */
.stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp li {
    color: #f8fafc !important;
}

/* Glassmorphic Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: rgba(2, 6, 23, 0.9) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
    color: #e2e8f0 !important;
}

/* Custom Header Card */
.header-container {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(167, 139, 250, 0.08) 100%);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
    backdrop-filter: blur(10px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.title-gradient {
    background: linear-gradient(135deg, #a5b4fc 0%, #c084fc 50%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 2.85rem;
    margin-bottom: 0.5rem;
    letter-spacing: -0.025em;
    display: inline-block;
}

.subtitle {
    color: #94a3b8 !important;
    font-size: 1.15rem;
    font-weight: 400;
}

/* Chat Message Card */
[data-testid="stChatMessage"] {
    background-color: rgba(30, 41, 59, 0.45) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 16px !important;
    padding: 1.25rem !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
    transition: transform 0.2s ease, border-color 0.2s ease !important;
}

[data-testid="stChatMessage"]:hover {
    transform: translateY(-1px);
    border-color: rgba(139, 92, 246, 0.3) !important;
}

/* Highlight user chat message */
[data-testid="stChatMessageUser"] {
    background-color: rgba(99, 102, 241, 0.1) !important;
    border: 1px solid rgba(99, 102, 241, 0.25) !important;
}

/* Fix chat message input box styling */
[data-testid="stChatInput"] textarea {
    background-color: rgba(30, 41, 59, 0.6) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
}

/* Fix standard text inputs, textareas, and select box styling for contrast */
div[data-baseweb="input"] {
    background-color: rgba(15, 23, 42, 0.6) !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}
div[data-baseweb="input"] input {
    color: #f8fafc !important;
}

div[data-baseweb="select"] {
    background-color: rgba(15, 23, 42, 0.6) !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #f8fafc !important;
}

/* Dropdown list items */
div[role="listbox"] {
    background-color: #0f172a !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}
div[role="option"] {
    color: #e2e8f0 !important;
    background-color: transparent !important;
}
div[role="option"]:hover {
    background-color: rgba(99, 102, 241, 0.2) !important;
}

/* File Uploader styling */
[data-testid="stFileUploader"] {
    background-color: rgba(15, 23, 42, 0.5) !important;
    border: 1px dashed rgba(167, 139, 250, 0.3) !important;
    border-radius: 12px !important;
    padding: 1.25rem !important;
}
[data-testid="stFileUploader"] section {
    background-color: transparent !important;
}

/* Custom source citations */
.source-card {
    background-color: rgba(15, 23, 42, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.15);
}

.source-meta {
    font-size: 0.8rem;
    font-weight: 600;
    color: #c084fc !important;
    margin-bottom: 0.35rem;
    display: flex;
    justify-content: space-between;
}

.source-text {
    font-size: 0.85rem;
    color: #cbd5e1 !important;
    font-style: italic;
    line-height: 1.6;
}

/* Custom side button sizes */
div.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    margin-bottom: 0.5rem;
}

/* Primary buttons hover effects */
button[kind="primary"] {
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%) !important;
    color: white !important;
    border: none !important;
}

button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStoreManager()
    
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
if "processed_files" not in st.session_state:
    st.session_state.processed_files = []

# Sidebar Config
st.sidebar.title("📚 Document Portal")

# Sidebar Model Selection
selected_model = st.sidebar.selectbox(
    "🤖 LLM Model",
    ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.5-flash", "gemini-3.5-pro"],
    help="Select the Gemini model version. Gemini 2.5 Flash is recommended for its high free daily quota (1,500 requests/day)."
)

# Reinitialize chatbot if model changes or chatbot is not yet in session state
if "chatbot" not in st.session_state or st.session_state.get("current_model") != selected_model:
    st.session_state.current_model = selected_model
    st.session_state.chatbot = ChatBot(st.session_state.vector_store, model=selected_model)
    if st.session_state.processed_files:
        st.session_state.chatbot.build_rag_chain()

# Check/Get API Key
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    st.sidebar.warning("🔑 GOOGLE_API_KEY not found in .env")
    api_key_input = st.sidebar.text_input("Enter Gemini API Key:", type="password")
    if api_key_input:
        os.environ["GOOGLE_API_KEY"] = api_key_input
        st.sidebar.success("API Key loaded for this session!")
        api_key = api_key_input
        # Re-initialize chatbot to load the new API key and model
        st.session_state.chatbot = ChatBot(st.session_state.vector_store, model=selected_model)
        if st.session_state.processed_files:
            st.session_state.chatbot.build_rag_chain()

# PDF Uploader
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF files", 
    type=["pdf"], 
    accept_multiple_files=True
)

if uploaded_files:
    new_files = [f.name for f in uploaded_files]
    if new_files != st.session_state.processed_files:
        with st.sidebar.status("🔄 Ingesting PDF content...", expanded=True) as status:
            all_documents = []
            for uploaded_file in uploaded_files:
                status.write(f"Extracting text from: `{uploaded_file.name}`")
                
                # Write to temp file for PyMuPDF loading
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                try:
                    pages = PDFProcessor.extract_text_from_pdf(tmp_path)
                    all_documents.extend(pages)
                finally:
                    os.unlink(tmp_path)
                    
            if all_documents:
                status.write("Splitting documents into chunks...")
                chunks = PDFProcessor.chunk_documents(all_documents, chunk_size=1000, chunk_overlap=100)
                
                status.write("Embedding and building index...")
                success = st.session_state.vector_store.create_or_update_index(chunks)
                
                if success:
                    status.update(label="✅ Documents indexed successfully!", state="complete", expanded=False)
                    st.session_state.processed_files = new_files
                    st.session_state.chatbot.build_rag_chain()
                    st.toast("Vector database updated!", icon="✅")
                else:
                    status.update(label="❌ Failed to create vector index.", state="error")
            else:
                status.update(label="⚠️ Could not extract text from uploaded files.", state="error")

# Display Current Database Status
if st.session_state.vector_store.db is not None:
    st.sidebar.markdown("### 📊 Index Status")
    st.sidebar.info(
        f"**Engine**: {st.session_state.vector_store.vector_store_type}\n\n"
        f"**Files Indexed**: {len(st.session_state.processed_files)}"
    )

# Control Center
st.sidebar.markdown("### ⚙️ Control Panel")
if st.sidebar.button("🗑️ Clear Conversation", use_container_width=True):
    st.session_state.chat_history = []
    st.session_state.chatbot.clear_memory()
    st.toast("Conversation memory cleared!", icon="🗑️")
    st.rerun()

if st.sidebar.button("🔄 Reset Application", use_container_width=True):
    st.session_state.chat_history = []
    st.session_state.processed_files = []
    st.session_state.vector_store.clear_index()
    st.session_state.chatbot.clear_memory()
    st.toast("Application reset successfully!", icon="🔄")
    st.rerun()

# Main Q&A Content
st.markdown(f"""
<div class="header-container">
    <div class="title-gradient">PDF Q&A Chatbot</div>
    <div class="subtitle">Secure Retrieval Augmented Generation (RAG) with {selected_model}</div>
</div>
""", unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("🔍 View Sources"):
                for idx, src in enumerate(message["sources"]):
                    st.markdown(f"""
                    <div class="source-card">
                        <div class="source-meta">
                            <span>Source {idx+1}: {src['source']}</span>
                            <span>Page {src['page']}</span>
                        </div>
                        <div class="source-text">"{src['text']}"</div>
                    </div>
                    """, unsafe_allow_html=True)

# Chat Input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add User message
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Generate response
    with st.chat_message("assistant"):
        if not api_key:
            st.error("🔑 Google Gemini API Key is missing. Add it to `.env` or input it in the sidebar.")
        elif not st.session_state.processed_files:
            st.warning("📂 No documents uploaded. Please upload a PDF in the portal first.")
        else:
            with st.spinner("Searching context & generating answer..."):
                response = st.session_state.chatbot.ask(prompt)
                answer = response["answer"]
                source_docs = response["source_documents"]
                
                # Format sources for UI
                sources = []
                for doc in source_docs:
                    sources.append({
                        "source": doc.metadata.get("source", "Unknown"),
                        "page": doc.metadata.get("page", "?"),
                        "text": doc.page_content.strip()
                    })
                
                # Render answer
                st.markdown(answer)
                
                # Render source card expander
                if sources:
                    with st.expander("🔍 View Sources"):
                        for idx, src in enumerate(sources):
                            st.markdown(f"""
                            <div class="source-card">
                                <div class="source-meta">
                                    <span>Source {idx+1}: {src['source']}</span>
                                    <span>Page {src['page']}</span>
                                </div>
                                <div class="source-text">"{src['text']}"</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                # Save to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
