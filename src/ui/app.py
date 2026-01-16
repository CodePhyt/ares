"""
ARES Enterprise UI - Premium Enterprise AI Command Center
Features: Analytics Dashboard, System Health, PDF Export, Document Graph, Dark/Light Mode
"""

import streamlit as st
import httpx
import json
from typing import List, Dict, Any
from pathlib import Path
import time
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
import pandas as pd

# Page configuration with custom favicon
st.set_page_config(
    page_title="ARES | Enterprise AI Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "ARES v1.0.0 - Enterprise AI Command Center"
    }
)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_documents" not in st.session_state:
    st.session_state.uploaded_documents = []
if "pii_shield_count" not in st.session_state:
    st.session_state.pii_shield_count = 0
if "theme" not in st.session_state:
    st.session_state.theme = "dark"  # Default to premium dark theme
if "query_times" not in st.session_state:
    st.session_state.query_times = []
if "memory_usage" not in st.session_state:
    st.session_state.memory_usage = []

# Configuration
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")
API_BASE = f"{BACKEND_URL}/api/v1"

# Premium Theme CSS - Slate & Gold
SLATE_GOLD_THEME = """
<style>
    /* Premium Slate & Gold Theme */
    :root {
        --slate-900: #0f172a;
        --slate-800: #1e293b;
        --slate-700: #334155;
        --slate-600: #475569;
        --slate-500: #64748b;
        --slate-400: #94a3b8;
        --slate-300: #cbd5e1;
        --slate-200: #e2e8f0;
        --slate-100: #f1f5f9;
        --gold-600: #d97706;
        --gold-500: #f59e0b;
        --gold-400: #fbbf24;
        --gold-300: #fcd34d;
        --accent-primary: #f59e0b;
        --accent-secondary: #d97706;
    }

    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: linear-gradient(135deg, var(--slate-900) 0%, var(--slate-800) 100%);
    }

    /* Headers with gold accent */
    h1, h2, h3 {
        color: var(--gold-400) !important;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);
        letter-spacing: -0.5px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--slate-900) 0%, var(--slate-800) 100%);
        border-right: 2px solid var(--gold-600);
    }

    /* Cards */
    .stCard {
        background: var(--slate-800);
        border: 1px solid var(--slate-700);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--gold-500), var(--gold-600));
        color: var(--slate-900);
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(245, 158, 11, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(245, 158, 11, 0.5);
        background: linear-gradient(135deg, var(--gold-400), var(--gold-500));
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: var(--gold-400);
        font-size: 2.5rem;
        font-weight: 700;
    }

    [data-testid="stMetricLabel"] {
        color: var(--slate-300);
        font-size: 0.9rem;
    }

    /* Input fields */
    .stTextInput > div > div > input {
        background-color: var(--slate-800);
        color: var(--slate-100);
        border: 1px solid var(--slate-600);
        border-radius: 8px;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--gold-500);
        box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--slate-800);
        border-bottom: 2px solid var(--slate-700);
    }

    .stTabs [data-baseweb="tab"] {
        color: var(--slate-300);
    }

    .stTabs [aria-selected="true"] {
        color: var(--gold-400) !important;
        border-bottom: 2px solid var(--gold-500);
    }

    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }

    .status-active {
        background-color: var(--gold-400);
        box-shadow: 0 0 12px var(--gold-500);
    }

    .status-warning {
        background-color: #f59e0b;
        box-shadow: 0 0 12px #f59e0b;
    }

    .status-error {
        background-color: #ef4444;
        box-shadow: 0 0 12px #ef4444;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Premium badge */
    .premium-badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--gold-500), var(--gold-600));
        color: var(--slate-900);
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Chart containers */
    .chart-container {
        background: var(--slate-800);
        border: 1px solid var(--slate-700);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
</style>
"""

# Light theme (optional)
LIGHT_THEME = """
<style>
    :root {
        --bg-light: #ffffff;
        --bg-card-light: #f8fafc;
        --text-primary-light: #1e293b;
        --text-secondary-light: #64748b;
        --border-light: #e2e8f0;
    }
    .main .block-container {
        background: var(--bg-light);
    }
    h1, h2, h3 {
        color: var(--gold-600) !important;
    }
</style>
"""

# Apply theme
if st.session_state.theme == "dark":
    st.markdown(SLATE_GOLD_THEME, unsafe_allow_html=True)
else:
    st.markdown(LIGHT_THEME, unsafe_allow_html=True)


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


def get_system_health() -> Dict[str, Any]:
    """Fetch detailed system health metrics."""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{API_BASE}/system/health")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        st.error(f"Error fetching health: {e}")
    return {}


def get_document_graph() -> Dict[str, Any]:
    """Fetch document relationship graph."""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{API_BASE}/documents/graph")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        st.error(f"Error fetching graph: {e}")
    return {}


def query_ares(query: str, mask_pii: bool = True) -> Dict[str, Any]:
    """Query ARES backend."""
    start_time = time.time()
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{API_BASE}/query",
                json={"query": query, "mask_pii": mask_pii},
            )
            if response.status_code == 200:
                result = response.json()
                # Track query time
                query_time = time.time() - start_time
                st.session_state.query_times.append(query_time * 1000)  # ms
                # Track PII count
                if result.get("pii_masked"):
                    st.session_state.pii_shield_count += result.get("pii_count", 0)
                return result
            else:
                st.error(f"Error: {response.text}")
                return {}
    except Exception as e:
        st.error(f"Error querying ARES: {e}")
        return {}


def upload_document(file) -> Dict[str, Any]:
    """Upload document to ARES."""
    try:
        with httpx.Client(timeout=300.0) as client:
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


def export_audit_pdf(query: str, answer: str, citations: List[dict], confidence: float, pii_count: int, iterations: int):
    """Export audit report as PDF."""
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{API_BASE}/export/audit-pdf",
                json={
                    "query": query,
                    "answer": answer,
                    "citations": citations,
                    "confidence": confidence,
                    "pii_count": pii_count,
                    "iterations": iterations,
                }
            )
            if response.status_code == 200:
                # Save PDF file
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                pdf_path = Path("exports") / f"ARES_Audit_{timestamp}.pdf"
                pdf_path.parent.mkdir(exist_ok=True)
                with open(pdf_path, "wb") as f:
                    f.write(response.content)
                return {"status": "success", "file_path": str(pdf_path)}
    except Exception as e:
        st.error(f"Error exporting PDF: {e}")
        return {}


# Sidebar
with st.sidebar:
    st.title("🛡️ ARES")
    st.markdown('<span class="premium-badge">Enterprise</span>', unsafe_allow_html=True)
    st.markdown("**Autonomous Resilient Enterprise Suite**")
    st.markdown("---")
    
    # Theme Toggle
    theme_options = ["🌙 Dark (Slate & Gold)", "☀️ Light"]
    selected_theme = st.selectbox(
        "Theme",
        theme_options,
        index=0 if st.session_state.theme == "dark" else 1,
        label_visibility="collapsed"
    )
    st.session_state.theme = "dark" if "Dark" in selected_theme else "light"
    
    st.markdown("---")
    
    # System Status
    st.subheader("⚡ System Status")
    stats = get_system_stats()
    
    if stats:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Documents", stats.get("documents_indexed", 0))
        with col2:
            st.metric("Chunks", stats.get("chunks_indexed", 0))
        
        # Privacy Shield Counter
        st.markdown("---")
        st.metric(
            "🛡️ Privacy Shield",
            f"{st.session_state.pii_shield_count}",
            help="Total PII entities masked in this session"
        )
        
        st.markdown(f"""
        <div style="margin-top: 1rem;">
            <span class="status-indicator status-active"></span>
            <span style="color: var(--slate-300);">PII Masking: {'Enabled' if stats.get('pii_masking_enabled') else 'Disabled'}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Settings
    st.subheader("⚙️ Settings")
    mask_pii = st.checkbox("Enable PII Masking", value=True)
    
    st.markdown("---")
    
    # Document Upload
    st.subheader("📤 Upload Documents")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "txt", "md", "xlsx"],
        help="Supported formats: PDF, DOCX, TXT, MD, XLSX",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        if st.button("Upload & Index", type="primary"):
            with st.spinner("Uploading and indexing document..."):
                result = upload_document(uploaded_file)
                if result:
                    st.success(f"✅ {result.get('filename')}")
                    st.info(f"Chunks: {result.get('chunks_created', 0)}")
                    if result.get('pii_detected', 0) > 0:
                        st.warning(f"⚠️ PII: {result.get('pii_detected')} entities")
                        st.session_state.pii_shield_count += result.get('pii_detected', 0)
                    st.session_state.uploaded_documents.append(result)
                    st.rerun()
    
    # Uploaded Documents List
    if st.session_state.uploaded_documents:
        st.markdown("---")
        st.subheader("📚 Indexed Documents")
        for doc in st.session_state.uploaded_documents:
            st.markdown(f"📄 {doc.get('filename', 'Unknown')}")


# Main Content with Tabs
st.title("🛡️ ARES | Enterprise AI Command Center")
st.markdown("**GDPR-Compliant Document Intelligence Platform**")
st.markdown("---")

# Navigation Tabs
selected = option_menu(
    menu_title=None,
    options=["💬 Query", "📊 Analytics", "🗺️ Discovery", "📄 Export"],
    icons=["chat", "graph-up", "diagram-3", "file-pdf"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "var(--slate-800)"},
        "icon": {"color": "var(--gold-400)", "font-size": "18px"},
        "nav-link": {
            "font-size": "16px",
            "text-align": "center",
            "margin": "0px",
            "color": "var(--slate-300)",
            "background-color": "var(--slate-800)",
        },
        "nav-link-selected": {
            "background-color": "var(--slate-700)",
            "color": "var(--gold-400)",
        },
    }
)

# Query Tab
if selected == "💬 Query":
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
                        filename = citation.get("filename", "Unknown")
                        page = citation.get("page", "N/A")
                        score = citation.get("score", 0.0)
                        st.markdown(f"**[{idx}]** {filename} | Page: {page} | Relevance: {score:.2f}")
            
            # Display metadata
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                confidence = chat.get('confidence', 0.0)
                confidence_color = "#10b981" if confidence > 0.7 else "#f59e0b" if confidence > 0.5 else "#ef4444"
                st.markdown(f"**Confidence:** <span style='color: {confidence_color};'>{confidence:.2%}</span>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**Iterations:** {chat.get('iterations', 0)}")
            with col3:
                if chat.get("pii_masked"):
                    st.markdown(f"**🛡️ PII:** {chat.get('pii_count', 0)} masked")
                else:
                    st.markdown("**🛡️ PII:** None")
            with col4:
                # Export button for this query
                if st.button("📄 Export PDF", key=f"export_{i}"):
                    export_result = export_audit_pdf(
                        chat["query"],
                        chat["answer"],
                        chat.get("citations", []),
                        chat.get("confidence", 0.0),
                        chat.get("pii_count", 0),
                        chat.get("iterations", 0),
                    )
                    if export_result:
                        st.success(f"PDF exported: {export_result.get('file_path', '')}")
    
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
                    time.sleep(0.01)
                
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
                            filename = citation.get("filename", "Unknown")
                            page = citation.get("page", "N/A")
                            score = citation.get("score", 0.0)
                            st.markdown(f"**[{idx}]** {filename} | Page: {page} | Relevance: {score:.2f}")
                
                # Display metadata
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    confidence = response.get("confidence", 0.0)
                    confidence_color = "#10b981" if confidence > 0.7 else "#f59e0b" if confidence > 0.5 else "#ef4444"
                    st.markdown(f"**Confidence:** <span style='color: {confidence_color};'>{confidence:.2%}</span>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"**Iterations:** {response.get('iterations', 0)}")
                with col3:
                    if response.get("pii_masked"):
                        st.markdown(f"**🛡️ PII:** {response.get('pii_count', 0)} masked")
                    else:
                        st.markdown("**🛡️ PII:** None")
                with col4:
                    if st.button("📄 Export PDF", key="export_current"):
                        export_result = export_audit_pdf(
                            query,
                            answer,
                            citations,
                            confidence,
                            response.get("pii_count", 0),
                            response.get("iterations", 0),
                        )
                        if export_result:
                            st.success(f"✅ PDF exported: {export_result.get('file_path', '')}")
            else:
                st.error("Failed to get response from ARES backend.")

# Analytics Tab
elif selected == "📊 Analytics":
    st.subheader("📊 System Health & Analytics")
    
    health_data = get_system_health()
    
    if health_data:
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            inference_speed = health_data.get("performance", {}).get("inference_speed_tokens_per_sec", 0)
            st.metric("⚡ Inference Speed", f"{inference_speed:.1f}", "tokens/sec")
        
        with col2:
            avg_query_time = health_data.get("performance", {}).get("avg_query_time_ms", 0)
            st.metric("⏱️ Avg Query Time", f"{avg_query_time:.0f}", "ms")
        
        with col3:
            memory_info = health_data.get("memory", {})
            process_memory = memory_info.get("process_mb", 0)
            st.metric("💾 Process Memory", f"{process_memory:.0f}", "MB")
        
        with col4:
            chromadb_size = memory_info.get("chromadb_size_mb", 0)
            st.metric("🗄️ ChromaDB Size", f"{chromadb_size:.0f}", "MB")
        
        st.markdown("---")
        
        # Memory Usage Visualization
        st.subheader("💾 Memory Usage")
        col1, col2 = st.columns(2)
        
        with col1:
            if memory_info:
                memory_data = {
                    "Component": ["Process", "ChromaDB", "Available"],
                    "Memory (MB)": [
                        memory_info.get("process_mb", 0),
                        memory_info.get("chromadb_size_mb", 0),
                        memory_info.get("system_available_gb", 0) * 1024,
                    ]
                }
                df_memory = pd.DataFrame(memory_data)
                fig_memory = px.bar(
                    df_memory,
                    x="Component",
                    y="Memory (MB)",
                    color="Component",
                    color_discrete_map={
                        "Process": "#f59e0b",
                        "ChromaDB": "#d97706",
                        "Available": "#64748b"
                    },
                    title="Memory Distribution"
                )
                fig_memory.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#cbd5e1"
                )
                st.plotly_chart(fig_memory, use_container_width=True)
        
        with col2:
            # System Memory Pie Chart
            if memory_info.get("system_used_percent"):
                system_used = memory_info.get("system_used_percent", 0)
                system_available = 100 - system_used
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=["Used", "Available"],
                    values=[system_used, system_available],
                    hole=0.4,
                    marker_colors=["#f59e0b", "#64748b"]
                )])
                fig_pie.update_layout(
                    title="System Memory Usage",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#cbd5e1"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        st.markdown("---")
        
        # Performance Metrics
        st.subheader("⚡ Performance Metrics")
        
        # Query Time History
        if st.session_state.query_times:
            df_times = pd.DataFrame({
                "Query": range(1, len(st.session_state.query_times) + 1),
                "Time (ms)": st.session_state.query_times
            })
            
            fig_times = px.line(
                df_times,
                x="Query",
                y="Time (ms)",
                title="Query Response Time History",
                markers=True
            )
            fig_times.update_traces(line_color="#f59e0b", marker_color="#d97706")
            fig_times.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#cbd5e1"
            )
            st.plotly_chart(fig_times, use_container_width=True)
        
        # Privacy Shield Statistics
        st.markdown("---")
        st.subheader("🛡️ Privacy Shield Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total PII Masked", f"{st.session_state.pii_shield_count}", "this session")
        with col2:
            st.metric("Queries Processed", len(st.session_state.query_times))
        with col3:
            avg_pii = st.session_state.pii_shield_count / len(st.session_state.query_times) if st.session_state.query_times else 0
            st.metric("Avg PII per Query", f"{avg_pii:.1f}")
        
        # API Metrics
        api_metrics = health_data.get("api_metrics", {})
        if api_metrics:
            st.markdown("---")
            st.subheader("📈 API Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Requests", api_metrics.get("total_requests", 0))
            with col2:
                st.metric("Error Rate", f"{api_metrics.get('error_rate', 0):.2%}")
            with col3:
                uptime = api_metrics.get("uptime_formatted", "0:00:00")
                st.metric("Uptime", uptime)
            with col4:
                req_timing = api_metrics.get("request_timing", {})
                st.metric("Avg Response", f"{req_timing.get('avg_ms', 0):.0f} ms")

# Discovery Tab (Document Relationship Map)
elif selected == "🗺️ Discovery":
    st.subheader("🗺️ Document Relationship Discovery")
    st.markdown("Visualize how your documents are connected through shared keywords and topics.")
    
    graph_data = get_document_graph()
    
    if graph_data and graph_data.get("nodes"):
        # Graph Statistics
        stats = graph_data.get("stats", {})
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Documents", stats.get("total_nodes", 0))
        with col2:
            st.metric("Connections", stats.get("total_edges", 0))
        with col3:
            density = stats.get("density", 0)
            st.metric("Network Density", f"{density:.2%}")
        
        st.markdown("---")
        
        # Network Graph Visualization
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        
        if nodes:
            # Create network graph using Plotly
            node_x = []
            node_y = []
            node_text = []
            node_sizes = []
            
            # Simple layout (in production, use networkx layout algorithms)
            import math
            num_nodes = len(nodes)
            for i, node in enumerate(nodes):
                angle = 2 * math.pi * i / num_nodes
                node_x.append(math.cos(angle))
                node_y.append(math.sin(angle))
                node_text.append(node.get("label", node.get("id", "Unknown")))
                node_sizes.append(20 + len(node.get("keywords", [])) * 5)
            
            # Create edge traces
            edge_x = []
            edge_y = []
            for edge in edges:
                from_idx = next((i for i, n in enumerate(nodes) if n["id"] == edge["from"]), -1)
                to_idx = next((i for i, n in enumerate(nodes) if n["id"] == edge["to"]), -1)
                if from_idx >= 0 and to_idx >= 0:
                    edge_x.extend([node_x[from_idx], node_x[to_idx], None])
                    edge_y.extend([node_y[from_idx], node_y[to_idx], None])
            
            # Create plotly figure
            fig = go.Figure()
            
            # Add edges
            fig.add_trace(go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=1, color="#64748b"),
                hoverinfo='none',
                mode='lines',
                showlegend=False
            ))
            
            # Add nodes
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                name='Documents',
                text=node_text,
                textposition="middle center",
                hovertext=[f"Keywords: {', '.join(n.get('keywords', [])[:5])}" for n in nodes],
                marker=dict(
                    size=node_sizes,
                    color="#f59e0b",
                    line=dict(width=2, color="#d97706")
                ),
                showlegend=False
            ))
            
            fig.update_layout(
                title="Document Relationship Network",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=[
                    dict(
                        text="Documents are connected based on shared keywords",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002,
                        xanchor="left", yanchor="bottom",
                        font=dict(color="#94a3b8", size=12)
                    )
                ],
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#cbd5e1"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Document Details Table
            st.markdown("---")
            st.subheader("📋 Document Details")
            
            doc_table_data = []
            for node in nodes:
                doc_table_data.append({
                    "Document": node.get("label", "Unknown"),
                    "ID": node.get("id", "N/A"),
                    "Keywords": ", ".join(node.get("keywords", [])[:10]),
                    "Connections": len([e for e in edges if e["from"] == node["id"] or e["to"] == node["id"]])
                })
            
            df_docs = pd.DataFrame(doc_table_data)
            st.dataframe(df_docs, use_container_width=True, hide_index=True)
        else:
            st.info("No documents indexed yet. Upload documents to see relationships.")
    else:
        st.info("📚 Upload documents to visualize relationships and discover connections.")

# Export Tab
elif selected == "📄 Export":
    st.subheader("📄 Export Audit Reports")
    st.markdown("Generate professional PDF reports with ARES watermark and complete audit trails.")
    
    if st.session_state.chat_history:
        st.markdown("### Recent Queries")
        
        for i, chat in enumerate(st.session_state.chat_history):
            with st.expander(f"Query {i+1}: {chat['query'][:50]}..."):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Answer:**", chat["answer"][:200] + "...")
                    st.write(f"**Confidence:** {chat.get('confidence', 0.0):.2%}")
                    st.write(f"**Sources:** {len(chat.get('citations', []))}")
                with col2:
                    if st.button("📄 Export PDF", key=f"export_tab_{i}"):
                        export_result = export_audit_pdf(
                            chat["query"],
                            chat["answer"],
                            chat.get("citations", []),
                            chat.get("confidence", 0.0),
                            chat.get("pii_count", 0),
                            chat.get("iterations", 0),
                        )
                        if export_result:
                            st.success(f"✅ Exported: {export_result.get('file_path', '')}")
    else:
        st.info("No queries to export. Start querying documents to generate audit reports.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--slate-400); padding: 2rem;">
    <p><strong>ARES v1.0.0</strong> | Enterprise AI Command Center</p>
    <p>100% Offline | GDPR-Compliant | Privacy-First | Built for German Enterprise Data Sovereignty</p>
    <p style="margin-top: 1rem; font-size: 0.85rem;">© 2024 ARES Development Team | All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
