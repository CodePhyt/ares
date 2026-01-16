"""
Streamlit UI for ARES - Cyber-Enterprise Dark Theme
Features: Real-time token streaming, Source citations, Privacy status indicator
"""

import streamlit as st
import httpx
import json
from typing import List, Dict, Any
from pathlib import Path
import time

# Page configuration
st.set_page_config(
    page_title="ARES - AI Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for cyber-enterprise dark theme
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #00ff88;
        --secondary-color: #00d4ff;
        --bg-dark: #0a0e27;
        --bg-darker: #050811;
        --bg-card: #0f1629;
        --text-primary: #e0e6ed;
        --text-secondary: #8b95a6;
        --border-color: #1a2332;
        --accent-red: #ff3366;
    }

    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: var(--bg-dark);
    }

    /* Headers */
    h1, h2, h3 {
        color: var(--primary-color) !important;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: var(--bg-darker);
    }

    [data-testid="stSidebar"] {
        background-color: var(--bg-darker);
        border-right: 1px solid var(--border-color);
    }

    /* Cards and containers */
    .stCard {
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    /* Text inputs */
    .stTextInput > div > div > input {
        background-color: var(--bg-card);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: var(--bg-dark);
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 0.5rem 2rem;
        transition: all 0.3s;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 255, 136, 0.4);
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: var(--primary-color);
        font-size: 2rem;
    }

    /* Code blocks */
    .stCodeBlock {
        background-color: var(--bg-darker);
        border: 1px solid var(--border-color);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--bg-card);
        color: var(--text-primary);
    }

    /* File uploader */
    .uploadedFile {
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
    }

    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }

    .status-active {
        background-color: var(--primary-color);
        box-shadow: 0 0 8px var(--primary-color);
    }

    .status-warning {
        background-color: #ffaa00;
        box-shadow: 0 0 8px #ffaa00;
    }

    .status-error {
        background-color: var(--accent-red);
        box-shadow: 0 0 8px var(--accent-red);
    }
</style>
""", unsafe_allow_html=True)

# Configuration
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")
API_BASE = f"{BACKEND_URL}/api/v1"

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_documents" not in st.session_state:
    st.session_state.uploaded_documents = []


def get_system_stats() -> Dict[str, Any]:
    """Fetch system statistics from backend."""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{API_BASE}/stats")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        st.error(f"Error fetching stats: {e}")
    return {}


def query_ares(query: str, mask_pii: bool = True) -> Dict[str, Any]:
    """Query ARES backend."""
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{API_BASE}/query",
                json={"query": query, "mask_pii": mask_pii},
            )
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error: {response.text}")
                return {}
    except Exception as e:
        st.error(f"Error querying ARES: {e}")
        return {}


def upload_document(file) -> Dict[str, Any]:
    """Upload document to ARES."""
    try:
        with httpx.Client(timeout=60.0) as client:
            files = {"file": (file.name, file.read(), file.type)}
            response = client.post(f"{API_BASE}/upload", files=files)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error: {response.text}")
                return {}
    except Exception as e:
        st.error(f"Error uploading document: {e}")
        return {}


def display_citation(citation: Dict[str, Any], index: int):
    """Display a citation card."""
    filename = citation.get("filename", "Unknown")
    page = citation.get("page", "N/A")
    score = citation.get("score", 0.0)
    
    st.markdown(f"""
    <div style="background-color: var(--bg-card); border: 1px solid var(--border-color); 
                border-radius: 6px; padding: 1rem; margin: 0.5rem 0;">
        <strong style="color: var(--primary-color);">[{index}]</strong> 
        <span style="color: var(--text-primary);">{filename}</span>
        <span style="color: var(--text-secondary); margin-left: 1rem;">Seite: {page}</span>
        <span style="color: var(--text-secondary); margin-left: 1rem;">Relevanz: {score:.2f}</span>
    </div>
    """, unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    st.title("🛡️ ARES")
    st.markdown("**Autonomous Resilient Enterprise Suite**")
    st.markdown("---")
    
    # System Status
    st.subheader("System Status")
    stats = get_system_stats()
    
    if stats:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Documents", stats.get("documents_indexed", 0))
        with col2:
            st.metric("Chunks", stats.get("chunks_indexed", 0))
        
        st.markdown(f"""
        <div style="margin-top: 1rem;">
            <span class="status-indicator status-active"></span>
            <span style="color: var(--text-primary);">PII Masking: {'Enabled' if stats.get('pii_masking_enabled') else 'Disabled'}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Settings
    st.subheader("Settings")
    mask_pii = st.checkbox("Enable PII Masking", value=True)
    
    st.markdown("---")
    
    # Document Upload
    st.subheader("Upload Documents")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "txt", "md", "xlsx"],
        help="Supported formats: PDF, DOCX, TXT, MD, XLSX",
    )
    
    if uploaded_file is not None:
        if st.button("Upload & Index", type="primary"):
            with st.spinner("Uploading and indexing document..."):
                result = upload_document(uploaded_file)
                if result:
                    st.success(f"✅ Document indexed: {result.get('filename')}")
                    st.info(f"Chunks created: {result.get('chunks_created', 0)}")
                    if result.get('pii_detected', 0) > 0:
                        st.warning(f"⚠️ PII detected: {result.get('pii_detected')} entities")
                    st.session_state.uploaded_documents.append(result)
    
    # Uploaded Documents List
    if st.session_state.uploaded_documents:
        st.markdown("---")
        st.subheader("Indexed Documents")
        for doc in st.session_state.uploaded_documents:
            st.markdown(f"📄 {doc.get('filename', 'Unknown')}")


# Main Content
st.title("🛡️ ARES - AI Command Center")
st.markdown("**GDPR-Compliant Document Intelligence Platform**")
st.markdown("---")

# Chat Interface
st.subheader("💬 Query Documents")

# Display chat history
for i, chat in enumerate(st.session_state.chat_history):
    with st.chat_message("user"):
        st.write(chat["query"])
    
    with st.chat_message("assistant"):
        st.write(chat["answer"])
        
        # Display citations
        if chat.get("citations"):
            with st.expander(f"📚 Sources ({len(chat['citations'])})"):
                for idx, citation in enumerate(chat["citations"], 1):
                    display_citation(citation, idx)
        
        # Display metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"Confidence: {chat.get('confidence', 0.0):.2%}")
        with col2:
            st.caption(f"Iterations: {chat.get('iterations', 0)}")
        with col3:
            if chat.get("pii_masked"):
                st.caption(f"🛡️ PII Masked: {chat.get('pii_count', 0)} entities")

# Query input
query = st.chat_input("Ask a question about your documents...")

if query:
    # Add user message to history
    st.session_state.chat_history.append({"query": query, "answer": "", "citations": []})
    
    # Display user message
    with st.chat_message("user"):
        st.write(query)
    
    # Process query
    with st.chat_message("assistant"):
        with st.spinner("🤔 Reasoning..."):
            response = query_ares(query, mask_pii=mask_pii)
        
        if response:
            # Display answer with streaming effect
            answer_placeholder = st.empty()
            answer = response.get("answer", "")
            
            # Simulate streaming
            full_answer = ""
            for char in answer:
                full_answer += char
                answer_placeholder.write(full_answer)
                time.sleep(0.01)  # Small delay for streaming effect
            
            # Update chat history
            st.session_state.chat_history[-1]["answer"] = answer
            st.session_state.chat_history[-1]["citations"] = response.get("citations", [])
            st.session_state.chat_history[-1]["confidence"] = response.get("confidence", 0.0)
            st.session_state.chat_history[-1]["iterations"] = response.get("iterations", 0)
            st.session_state.chat_history[-1]["pii_masked"] = response.get("pii_masked", False)
            st.session_state.chat_history[-1]["pii_count"] = response.get("pii_count", 0)
            
            # Display citations
            citations = response.get("citations", [])
            if citations:
                with st.expander(f"📚 Sources ({len(citations)})"):
                    for idx, citation in enumerate(citations, 1):
                        display_citation(citation, idx)
            
            # Display metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                confidence = response.get("confidence", 0.0)
                confidence_color = "green" if confidence > 0.7 else "orange" if confidence > 0.5 else "red"
                st.markdown(f"**Confidence:** <span style='color: {confidence_color};'>{confidence:.2%}</span>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**Iterations:** {response.get('iterations', 0)}")
            with col3:
                if response.get("pii_masked"):
                    st.markdown(f"**🛡️ PII Masked:** {response.get('pii_count', 0)} entities")
                else:
                    st.markdown("**🛡️ PII:** None detected")
        else:
            st.error("Failed to get response from ARES backend.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-secondary); padding: 2rem;">
    <p>ARES v1.0.0 | Built for German Enterprise Data Sovereignty</p>
    <p>100% Offline | GDPR-Compliant | Privacy-First</p>
</div>
""", unsafe_allow_html=True)
