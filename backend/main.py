from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import tempfile
import shutil

from pdf_processor import PDFProcessor
from vector_store import VectorStoreManager
from chatbot import ChatBot

app = FastAPI(title="PDF Q&A Chatbot API", version="2.0")

# Configure CORS to allow React dev server to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core Managers
vstore = VectorStoreManager()
chatbot = ChatBot(vstore)

INDEXED_FILES_TRACKER = "indexed_files.txt"

def get_indexed_files() -> List[str]:
    """Reads the list of currently indexed file names from the tracking file."""
    if os.path.exists(INDEXED_FILES_TRACKER):
        with open(INDEXED_FILES_TRACKER, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def save_indexed_files(filenames: List[str]):
    """Appends new filenames to the tracker if they aren't already listed."""
    existing = get_indexed_files()
    updated = list(set(existing + filenames))
    with open(INDEXED_FILES_TRACKER, "w", encoding="utf-8") as f:
        for name in updated:
            f.write(f"{name}\n")

class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None  # Base64 string of the attached image

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Ingests, page-extracts, chunks, and indexes uploaded PDF documents.
    Appends the new documents to the existing vector store index.
    """
    all_documents = []
    filenames = []
    
    for file in files:
        if not file.filename.endswith(".pdf"):
            continue
        filenames.append(file.filename)
        
        # Write UploadFile stream to a temp local file for PyMuPDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
            
        try:
            pages = PDFProcessor.extract_text_from_pdf(tmp_path, original_filename=file.filename)
            all_documents.extend(pages)
        finally:
            os.unlink(tmp_path)
            
    if not all_documents:
        raise HTTPException(status_code=400, detail="No text could be extracted from the uploaded files.")
        
    # Chunk and generate vector embeddings
    chunks = PDFProcessor.chunk_documents(all_documents, chunk_size=1000, chunk_overlap=100)
    success = vstore.create_or_update_index(chunks, append=True)
    
    if success:
        save_indexed_files(filenames)
        chatbot.build_rag_chain()
        return {"message": "Files successfully uploaded and indexed", "files_loaded": len(filenames)}
    else:
        raise HTTPException(status_code=500, detail="Failed to create or update search index.")

@app.post("/ask")
async def ask_question(request: QueryRequest):
    """
    Core Q&A routing endpoint.
    If an image is provided, routes query to local LLaVA vision model (stateless).
    If no image is provided, retrieves text context and runs Llama 3.2 (conversational).
    """
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    if request.image:
        # Stateless vision model query
        print("Routing request to local vision model (llava)...")
        response = chatbot.ask_vision(request.question, request.image)
    else:
        # Conversational text RAG query
        print("Routing request to local text model (llama3.2)...")
        response = chatbot.ask(request.question)
        
    # Format source document references
    sources = []
    scores = []
    for doc in response.get("source_documents", []):
        raw_score = doc.metadata.get("score", None)
        similarity_percentage = None
        if raw_score is not None:
            try:
                # FAISS/Chroma returns L2 distance; convert to cosine similarity percentage
                sim = 1.0 - (float(raw_score) / 2.0)
                similarity_percentage = round(max(0.0, min(1.0, sim)) * 100, 1)
                scores.append(similarity_percentage)
            except Exception as parse_err:
                print(f"Error parsing similarity score: {parse_err}")
                
        sources.append({
            "source": doc.metadata.get("source", "Unknown"),
            "page": doc.metadata.get("page", "?"),
            "text": doc.page_content.strip(),
            "score": similarity_percentage
        })
        
    # Compute overall RAG confidence as the average score of all retrieved sources
    overall_confidence = None
    if scores:
        overall_confidence = round(sum(scores) / len(scores), 1)
        
    return {
        "answer": response.get("answer", "No answer generated."),
        "sources": sources,
        "confidence": overall_confidence
    }

@app.get("/files")
async def get_files():
    """Returns the names of all indexed files."""
    return {"files": get_indexed_files()}

@app.delete("/clear")
async def clear_data():
    """Wipes the FAISS index, clears conversational history, and resets trackers."""
    vstore.clear_index()
    chatbot.clear_memory()
    if os.path.exists(INDEXED_FILES_TRACKER):
        os.remove(INDEXED_FILES_TRACKER)
    return {"message": "Local indexes and chat histories successfully cleared."}
