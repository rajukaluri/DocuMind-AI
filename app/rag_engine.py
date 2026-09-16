from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings


def _get_vector_store():
    if not settings.GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY must be configured before using the RAG system.")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=settings.GOOGLE_API_KEY
    )
    return Chroma(
        persist_directory=settings.CHROMA_PERSIST_DIR,
        embedding_function=embeddings
    )

def add_documents_to_vectorstore(chunks):
    """Embeds and indexes document chunks in ChromaDB."""
    _get_vector_store().add_documents(chunks)

def query_rag_system(question: str):
    """Retrieves relevant chunks and generates an answer using Gemini."""
    retriever = _get_vector_store().as_retriever(search_kwargs={"k": 3})
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.2
    )

    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise.\n\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    response = rag_chain.invoke({"input": question})
    return response["answer"]