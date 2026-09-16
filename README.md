title: DocuMind AI
emoji: 📄
colorFrom: indigo
colorTo: blue
sdk: gradio
app_file: app_gradio.py
pinned: false

## Features

- PDF text extraction and chunking with PyPDF
- Semantic search with ChromaDB
- Gemini embeddings and chat generation
- FastAPI endpoints for document upload and questions
- Streamlit interface for local use
- Gradio interface for Hugging Face ZeroGPU Spaces
- Local persistence for the vector store

## Architecture

```text
PDF upload
		|
		v
PyPDFLoader -> Text chunks -> Gemini embeddings -> ChromaDB
																										|
Question -> Retriever -> Relevant context -> Gemini -> Answer
```

## Requirements

- Python 3.11 or newer
- A Google Gemini API key

## Local Setup

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create a local environment file at `data/.env`:

```dotenv
GOOGLE_API_KEY=your_gemini_api_key
```

Never commit this file or expose the key publicly. Use a newly generated key if an existing key has been exposed.

## Run the FastAPI Backend

```powershell
python -m uvicorn app.main:app --reload
```

Open the API documentation at http://127.0.0.1:8000/docs.

Available endpoints:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Health check |
| `POST` | `/upload` | Upload and index a PDF |
| `POST` | `/query` | Ask a question about indexed documents |

Example query:

```powershell
Invoke-RestMethod -Method Post `
	-Uri http://127.0.0.1:8000/query `
	-ContentType "application/json" `
	-Body '{"question":"What are the main points in the document?"}'
```

## Run the Local Streamlit UI

Start the FastAPI backend first, then run:

```powershell
streamlit run app_ui.py
```

The Streamlit interface uses `RAG_API_URL` when it is set. Otherwise, it runs the RAG pipeline in-process.

## Hugging Face Deployment

The Hugging Face Space uses the Gradio entrypoint and is compatible with ZeroGPU:

https://huggingface.co/spaces/Raju2004/DocuMind-AI

To configure the Space:

1. Add `GOOGLE_API_KEY` under Settings > Variables and secrets.
2. Keep the Space SDK set to `gradio`.
3. Use the free CPU or ZeroGPU hardware supported by the Space account.

The Space entrypoint is `app_gradio.py`. Its document processing and question-answering handlers use `@spaces.GPU` for ZeroGPU execution.

## Security

- Do not commit `.env` files, API keys, uploaded PDFs, `storage/`, or virtual environments.
- Rotate any API key that has appeared in a commit, screenshot, chat, or public repository.
- Store production secrets in Hugging Face Space Secrets or another secret manager.
- Review uploaded documents before sharing a deployed app with end users.

## Project Structure

```text
app/
	config.py       Environment and directory configuration
	main.py         FastAPI application and API routes
	rag_engine.py   Gemini, ChromaDB, retrieval, and answer generation
	utils.py        PDF loading and text splitting
app_ui.py         Streamlit client
app_gradio.py     Hugging Face Gradio client
requirements.txt  Python dependencies
data/             Local PDFs and environment file, ignored by Git
storage/          Local ChromaDB data, ignored by Git
```