import os

import gradio as gr
import spaces

from app.rag_engine import add_documents_to_vectorstore, query_rag_system
from app.utils import process_pdf


@spaces.GPU
def process_document(file_path):
    if not file_path:
        return "Please upload a PDF document first."
    if not file_path.lower().endswith(".pdf"):
        return "Only PDF files are supported."

    chunks = process_pdf(file_path)
    add_documents_to_vectorstore(chunks)
    return f"Successfully indexed {len(chunks)} chunks from {os.path.basename(file_path)}."


@spaces.GPU
def answer_question(question, history):
    if not question.strip():
        return history, "Please enter a question."

    answer = query_rag_system(question)
    history = history or []
    history.append((question, answer))
    return history, ""


with gr.Blocks(title="DocuMind AI") as demo:
    gr.Markdown("# DocuMind AI\nUpload a PDF and ask grounded questions about its contents.")

    with gr.Row():
        document = gr.File(label="Upload PDF", file_types=[".pdf"], type="filepath")
        process_button = gr.Button("Process document", variant="primary")
    status = gr.Markdown()
    process_button.click(process_document, inputs=document, outputs=status)

    chatbot = gr.Chatbot(label="Document Q&A")
    question = gr.Textbox(label="Question", placeholder="Ask a question about your document")
    ask_button = gr.Button("Ask", variant="primary")
    ask_button.click(answer_question, inputs=[question, chatbot], outputs=[chatbot, question])
    question.submit(answer_question, inputs=[question, chatbot], outputs=[chatbot, question])


if __name__ == "__main__":
    demo.launch()