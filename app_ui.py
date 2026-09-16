import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Enterprise DocAI | RAG Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Dark glassmorphism card container */
    .metric-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    /* Clean chat message styling */
    [data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }
    
    /* Custom button tweaks */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
</style>
""", unsafe_allow_html=True)

# Application Sidebar
with st.sidebar:
    st.markdown("### ⚡ **Enterprise RAG Engine**")
    st.caption("Powered by FastAPI, ChromaDB & Gemini 1.5")
    st.divider()

    st.markdown("#### 📄 **Document Management**")
    uploaded_file = st.file_uploader("Upload Knowledge Source (PDF)", type=["pdf"])
    
    if st.button("🚀 Process & Vectorize", use_container_width=True):
        if uploaded_file is not None:
            with st.status("Ingesting document...", expanded=True) as status:
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    response = requests.post(f"{API_URL}/upload", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.indexed_file = uploaded_file.name
                        st.session_state.chunks = data.get("chunks_indexed", 0)
                        status.update(label="Document indexed successfully!", state="complete", expanded=False)
                        st.toast("ChromaDB Vector Store Updated!", icon="✅")
                    else:
                        status.update(label="Processing Failed", state="error")
                        st.error(response.json().get("detail", "Error uploading file."))
                except Exception as e:
                    status.update(label="Connection Error", state="error")
                    st.error(f"Cannot connect to FastAPI server: {e}")
        else:
            st.warning("Please attach a PDF document first.")

    st.divider()
    
    # Live System Status Metrics
    st.markdown("#### 📊 **Pipeline Status**")
    indexed_doc = st.session_state.get("indexed_file", "None")
    chunk_count = st.session_state.get("chunks", 0)

    st.markdown(f"""
    <div class="metric-card">
        <small style="color: #94A3B8;">ACTIVE SOURCE</small><br>
        <strong style="color: #6366F1;">{indexed_doc}</strong>
    </div>
    <div class="metric-card">
        <small style="color: #94A3B8;">INDEXED VECTOR CHUNKS</small><br>
        <strong style="color: #10B981;">{chunk_count} Chunks</strong>
    </div>
    """, unsafe_allow_html=True)

# Main Chat Interface Header
st.title("📄 AI Document Knowledge Assistant")
st.caption("Ask questions and extract insights directly grounded in your document vector store.")

# Chat Session History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Upload a document in the sidebar, and I will help you analyze its contents."}
    ]

for msg in st.session_state.messages:
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Process User Input
if user_query := st.chat_input("Ask a question about your uploaded document..."):
    # Display user query
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_query)

    # Fetch RAG Response from Backend
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Retrieving relevant chunks & generating answer..."):
            try:
                res = requests.post(f"{API_URL}/query", json={"question": user_query})
                if res.status_code == 200:
                    answer = res.json().get("answer", "No answer returned.")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    err = res.json().get("detail", "Error retrieving context.")
                    st.error(f"Backend Error: {err}")
            except Exception as e:
                st.error(f"Failed to communicate with FastAPI: {e}")