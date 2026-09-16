import shutil
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.config import settings
from app.utils import process_pdf
from app.rag_engine import add_documents_to_vectorstore, query_rag_system

app = FastAPI(
    title="RAG Document Q&A API",
    description="A FastAPI service for PDF Document Ingestion and Context-Aware Q&A using ChromaDB and Gemini."
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.get("/")
def read_root():
    return {"message": "RAG Document Q&A API is live and running!"}

@app.post("/upload", summary="Upload and index a PDF document")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_path = os.path.join(settings.DATA_DIR, file.filename)
    
    # Save uploaded file locally
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process and index chunks into ChromaDB
    try:
        chunks = process_pdf(file_path)
        add_documents_to_vectorstore(chunks)
        return {
            "message": f"Successfully processed '{file.filename}'", 
            "chunks_indexed": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse, summary="Query indexed documents")
async def query_pdf(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        answer = query_rag_system(request.question)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))