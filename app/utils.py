import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_pdf(file_path: str):
    """
    Loads a PDF file and splits its content into overlapping text chunks.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at {file_path}")

    # Load PDF text
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Split text into chunks for better context retrieval
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    return chunks