import os

import requests
import streamlit as st

API_URL = os.getenv("RAG_API_URL", "").rstrip("/")

if not API_URL:
    from app.rag_engine import add_documents_to_vectorstore, query_rag_system


def upload_document(file_name, file_bytes):
    if API_URL:
        return requests.post(
            f"{API_URL}/upload",
            files={"file": (file_name, file_bytes, "application/pdf")},
            timeout=120,
        )

    from app.utils import process_pdf

    os.makedirs("data", exist_ok=True)
    file_path = os.path.join("data", file_name)
    with open(file_path, "wb") as document_file:
        document_file.write(file_bytes)
    chunks = process_pdf(file_path)
    add_documents_to_vectorstore(chunks)
    return {"message": f"Successfully processed '{file_name}'", "chunks_indexed": len(chunks)}


def query_document(question):
    if API_URL:
        return requests.post(f"{API_URL}/query", json={"question": question}, timeout=120)
    return {"answer": query_rag_system(question)}

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
                    result = upload_document(uploaded_file.name, uploaded_file.getvalue())
                    success = result.status_code == 200 if API_URL else True

                    if success:
                        data = result.json() if API_URL else result
                        st.session_state.indexed_file = uploaded_file.name
                        st.session_state.chunks = data.get("chunks_indexed", 0)
                        status.update(label="Document indexed successfully!", state="complete", expanded=False)
                        st.toast("ChromaDB Vector Store Updated!", icon="✅")
                    else:
                        status.update(label="Processing Failed", state="error")
                        st.error(result.json().get("detail", "Error uploading file."))
                except Exception as e:
                    status.update(label="Processing Failed", state="error")
                    st.error(f"Document processing failed: {e}")
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
                result = query_document(user_query)
                success = result.status_code == 200 if API_URL else True
                if success:
                    answer = (result.json() if API_URL else result).get("answer", "No answer returned.")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    err = result.json().get("detail", "Error retrieving context.")
                    st.error(f"Backend Error: {err}")
            except Exception as e:
                st.error(f"Question processing failed: {e}")