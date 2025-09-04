import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
from engine.ingestion import load_and_process_documents
from engine.query import user_input
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="QueryVerse v2.0",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    st.error("GOOGLE_API_KEY environment variable not set. Please create a .env file with your key.")
    st.stop()

# --- SETUP DIRECTORIES ---
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

VECTOR_STORE_DIR = Path("vector_store")
VECTOR_STORE_DIR.mkdir(exist_ok=True)

# --- ENHANCED MODERN STYLES ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main App Styling */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    
    /* Enhanced Sidebar */
    .st-emotion-cache-16txtl3, .st-emotion-cache-1cypcdb {
        background: rgba(15, 23, 42, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(148, 163, 184, 0.1) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Custom Chat Message Styling */
        .stChatMessage {
            background: #fff !important;
            color: #1e293b !important;
            border: 2px solid #3b82f6 !important;
            border-radius: 16px !important;
            margin-bottom: 1rem !important;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.10) !important;
            font-size: 1.08rem !important;
            padding: 1.1rem 1.2rem !important;
        }

        .stChatMessage[data-testid="chat-message-user"] {
            background: linear-gradient(135deg, #e0e7ff 60%, #f3f4f6 100%) !important;
            color: #1e293b !important;
            border-color: #6366f1 !important;
            font-weight: 600 !important;
        }

        .stChatMessage[data-testid="chat-message-assistant"] {
            background: linear-gradient(135deg, #f0fdf4 60%, #f3f4f6 100%) !important;
            color: #0f172a !important;
            border-color: #22c55e !important;
            font-weight: 500 !important;
        }
    
    /* Chat Input Enhancement */
    .stChatInput {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 2px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(20px) !important;
    }
    
    .stChatInput:focus-within {
        border-color: rgba(59, 130, 246, 0.5) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Button Enhancements */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.25) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important;
    }
    
    /* File Uploader */
    .st-emotion-cache-1erivf3 {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 2px dashed rgba(148, 163, 184, 0.3) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        text-align: center !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
        border-radius: 8px !important;
    }
    
    /* Welcome Screen */
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 70vh;
        text-align: center;
        padding: 4rem 2rem;
        background: rgba(15, 23, 42, 0.3);
        border-radius: 24px;
        border: 1px solid rgba(148, 163, 184, 0.1);
        backdrop-filter: blur(20px);
    }
    
    .welcome-logo {
        width: 120px;
        height: 120px;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        border-radius: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 2rem auto;
        box-shadow: 0 25px 50px rgba(59, 130, 246, 0.4);
        animation: float 4s ease-in-out infinite;
    }
    
    .welcome-logo span {
        color: white;
        font-size: 4rem;
        font-weight: 700;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        25% { transform: translateY(-8px) rotate(1deg); }
        50% { transform: translateY(-15px) rotate(0deg); }
        75% { transform: translateY(-8px) rotate(-1deg); }
    }
    
    .welcome-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .welcome-subtitle {
        font-size: 1.375rem;
        color: #cbd5e1;
        margin-bottom: 2.5rem;
        max-width: 700px;
        line-height: 1.6;
    }
    
    /* Status Cards */
    .status-card {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(16, 185, 129, 0.1));
        border: 1px solid rgba(34, 197, 94, 0.2);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        backdrop-filter: blur(10px);
    }
    
    .status-icon {
        width: 32px;
        height: 32px;
        background: rgba(34, 197, 94, 0.2);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #22c55e;
        font-weight: 600;
    }
    
    /* Chat Header */
    .chat-header {
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 20px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    .chat-header-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 1.5rem;
    }
    
    /* Sidebar Improvements */
    .sidebar-header {
        text-align: center;
        padding: 2rem 1rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        margin-bottom: 2rem;
    }
    
    .sidebar-logo {
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem auto;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
    }
    
    .sidebar-title {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 1.75rem;
        margin: 0;
    }
    
    .sidebar-version {
        color: #94a3b8;
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }
    
    /* Example Buttons */
    .example-btn {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        color: #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 0.875rem 1rem !important;
        margin-bottom: 0.5rem !important;
        text-align: left !important;
        font-weight: 400 !important;
        font-size: 0.875rem !important;
        transition: all 0.3s ease !important;
        box-shadow: none !important;
    }
    
    .example-btn:hover {
        background: rgba(59, 130, 246, 0.1) !important;
        border-color: rgba(59, 130, 246, 0.3) !important;
        transform: translateX(4px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15) !important;
    }
    
    /* Info boxes for welcome screen */
    .stAlert {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 16px !important;
        margin: 0.75rem 0 !important;
        backdrop-filter: blur(10px) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'doc_ready' not in st.session_state:
    st.session_state.doc_ready = False
    st.session_state.doc_name = None
    st.session_state.messages = []
    st.session_state.processing = False

# --- ENHANCED SIDEBAR ---
with st.sidebar:
    # Clean Header
    st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem; border-bottom: 1px solid rgba(148, 163, 184, 0.1); margin-bottom: 2rem;">
            <div style="width: 64px; height: 64px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); border-radius: 16px; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);">
                <span style="color: white; font-weight: 700; font-size: 1.75rem;">Q</span>
            </div>
            <h1 style="background: linear-gradient(135deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; font-size: 1.75rem; margin: 0;">QueryVerse</h1>
            <p style="color: #94a3b8; font-size: 0.875rem; margin-top: 0.25rem;">v2.0 Enhanced</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("""
            <div style="text-align: center; padding: 2.5rem 1rem 2rem 1rem; border-bottom: 2px solid #6366f1; margin-bottom: 2rem; background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); box-shadow: 0 8px 25px rgba(59, 130, 246, 0.18); border-radius: 0 0 24px 24px;">
                <div style="width: 70px; height: 70px; background: linear-gradient(135deg, #fff 0%, #e0e7ff 100%); border-radius: 18px; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; box-shadow: 0 8px 25px rgba(59, 130, 246, 0.18);">
                    <span style="color: #3b82f6; font-weight: 700; font-size: 2.2rem;">Q</span>
                </div>
                <h1 style="background: linear-gradient(135deg, #fff 0%, #e0e7ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; font-size: 2rem; margin: 0;">QueryVerse</h1>
                <p style="color: #e0e7ff; font-size: 1rem; margin-top: 0.25rem; font-weight: 500;">v2.0 Enhanced</p>
            </div>
        """, unsafe_allow_html=True)

    # Document Upload Section
    st.markdown("### 📁 **Knowledge Base**")
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload Document",
        type=["pdf", "txt", "md"],
        help="Supports PDF, TXT, and Markdown files",
        key="file_uploader",
        label_visibility="collapsed"
    )

    if uploaded_file and not st.session_state.processing:
        st.session_state.processing = True
        file_path = UPLOADS_DIR / uploaded_file.name
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        with st.spinner("🔄 Processing document..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.02)
                progress_bar.progress(i + 1)
            
            try:
                load_and_process_documents(str(file_path))
                st.session_state.doc_ready = True
                st.session_state.doc_name = uploaded_file.name
                st.session_state.messages = []
                st.session_state.processing = False
                st.success(f"✅ **{st.session_state.doc_name}** is ready!")
            except Exception as e:
                st.error(f"❌ **Error**: {str(e)}")
                st.session_state.doc_ready = False
                st.session_state.processing = False

    # Document Status
    if st.session_state.doc_ready and not st.session_state.processing:
        st.markdown(f"""
            <div class="status-card">
                <div class="status-icon">✓</div>
                <div>
                    <div style="font-weight: 600; color: #22c55e;">Ready</div>
                    <div style="font-size: 0.875rem; color: #94a3b8; margin-top: 2px;">{st.session_state.doc_name}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Example Queries (only when document is ready)
    if st.session_state.doc_ready:
        st.markdown("<div style='margin: 2rem 0 1rem 0;'></div>", unsafe_allow_html=True)
        st.markdown("### 💡 **Quick Actions**")
        
        example_queries = [
            "📄 Summarize this document",
            "🎯 What are the main conclusions?", 
            "📊 Extract key statistics",
            "❓ Ask me anything about this doc"
        ]
        
        for i, query in enumerate(example_queries):
            clean_query = query.split(" ", 1)[1]  # Remove emoji for actual query
            if st.button(query, key=f"example_{i}", use_container_width=True):
                if i == 3:  # "Ask me anything" - just focus on input
                    st.rerun()
                else:
                    st.session_state.messages.append({"role": "user", "content": clean_query})
                    with st.spinner("🤔 Analyzing..."):
                        response = user_input(clean_query)
                        answer = response['answer']
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.rerun()

    # Footer
    st.markdown("""
        <div style="position: fixed; bottom: 1rem; left: 1rem; right: 280px; 
                    color: #64748b; font-size: 0.75rem; text-align: center; 
                    padding: 1rem; border-top: 1px solid rgba(148, 163, 184, 0.1);">
            <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                <span>⚡ Powered by</span>
                <strong>Google Gemini</strong>
                <span>•</span>
                <strong>LangChain</strong>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- MAIN CONTENT ---
if not st.session_state.doc_ready:
    # Enhanced Welcome Screen
    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    with col2:
        st.markdown("""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 70vh; text-align: center; padding: 4rem 2rem; background: rgba(15, 23, 42, 0.3); border-radius: 24px; border: 1px solid rgba(148, 163, 184, 0.1); backdrop-filter: blur(20px);">
                <div style="width: 120px; height: 120px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); border-radius: 30px; display: flex; align-items: center; justify-content: center; margin: 0 auto 2rem auto; box-shadow: 0 25px 50px rgba(59, 130, 246, 0.4); animation: float 4s ease-in-out infinite;">
                    <span style="color: white; font-size: 4rem; font-weight: 700;">Q</span>
                </div>
                <h1 style="font-size: 3.5rem; font-weight: 800; background: linear-gradient(135deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem;">Welcome to QueryVerse</h1>
                <p style="font-size: 1.375rem; color: #cbd5e1; margin-bottom: 2.5rem; max-width: 700px; line-height: 1.6;">
                    Transform your documents into intelligent conversations. Upload any PDF, TXT, or Markdown file and unlock its knowledge through natural language queries.
                </p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; width: 100%; max-width: 600px; margin-top: 2rem;">
                    <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 16px; padding: 1.5rem; text-align: center;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">📄</div>
                        <div style="font-weight: 600; color: #e2e8f0; margin-bottom: 0.5rem;">Smart Analysis</div>
                        <div style="font-size: 0.875rem; color: #94a3b8;">Extract insights from your documents</div>
                    </div>
                    <div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 16px; padding: 1.5rem; text-align: center;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">💬</div>
                        <div style="font-weight: 600; color: #e2e8f0; margin-bottom: 0.5rem;">Natural Chat</div>
                        <div style="font-size: 0.875rem; color: #94a3b8;">Ask questions in plain language</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Feature Cards using Streamlit columns
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        feat_col1, feat_col2 = st.columns(2)
        
        with feat_col1:
            st.markdown("""
                <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); 
                           border-radius: 16px; padding: 1.5rem; text-align: center; height: 140px; display: flex; 
                           flex-direction: column; justify-content: center;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📄</div>
                    <div style="font-weight: 600; color: #e2e8f0; margin-bottom: 0.5rem; font-size: 1.1rem;">Smart Analysis</div>
                    <div style="font-size: 0.875rem; color: #94a3b8;">Extract insights from your documents</div>
                </div>
            """, unsafe_allow_html=True)
        
        with feat_col2:
            st.markdown("""
                <div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.2); 
                           border-radius: 16px; padding: 1.5rem; text-align: center; height: 140px; display: flex; 
                           flex-direction: column; justify-content: center;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">💬</div>
                    <div style="font-weight: 600; color: #e2e8f0; margin-bottom: 0.5rem; font-size: 1.1rem;">Natural Chat</div>
                    <div style="font-size: 0.875rem; color: #94a3b8;">Ask questions in plain language</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style="margin-top: 2rem; color: #64748b; font-size: 0.875rem; text-align: center;">
                👈 Start by uploading a document in the sidebar
            </div>
        """, unsafe_allow_html=True)

else:
    # Enhanced Chat Interface
    st.markdown(f"""
        <div class="chat-header">
            <div class="chat-header-icon">Q</div>
            <div>
                <h2 style="margin: 0; color: #f8fafc; font-size: 1.5rem; font-weight: 700;">QueryVerse Chat</h2>
                <p style="margin: 0; color: #94a3b8; font-size: 1rem;">
                    📄 <strong style="color: #e2e8f0;">{st.session_state.doc_name}</strong> • Ready for questions
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Chat Messages Container
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    content = message["content"]
                    if not content.endswith("*"):
                        content += f"\n\n---\n💡 *Source: {st.session_state.doc_name}*"
                    st.markdown(content)
                else:
                    st.markdown(message["content"])

    # Enhanced Chat Input
    if prompt := st.chat_input("Ask anything about your document...", key="chat_input"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching through your document..."):
                try:
                    response = user_input(prompt)
                    answer = response['answer']
                    formatted_answer = f"{answer}\n\n---\n💡 *Source: {st.session_state.doc_name}*"
                    st.markdown(formatted_answer)
                    st.session_state.messages.append({"role": "assistant", "content": formatted_answer})
                except Exception as e:
                    error_msg = f"❌ **Unable to process your question**\n\n*Error: {str(e)}*\n\nPlease try rephrasing your question or check your document."
                    st.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})