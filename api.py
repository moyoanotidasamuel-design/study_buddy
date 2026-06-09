from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
from chat import chat
from loader import load_pdf
from chunker import chunk_pages
from embedder import embed_chunks
from store import store_in_chroma

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Store conversation histories per session
sessions = {}

class ChatRequest(BaseModel):
    question: str
    session_id: str = "default"

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Save uploaded file
    filepath = f"./uploads/{file.filename}"
    os.makedirs("./uploads", exist_ok=True)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Ingest into ChromaDB
    pages = load_pdf(filepath)
    chunks = chunk_pages(pages)
    embedded = embed_chunks(chunks)
    store_in_chroma(embedded)

    return {
        "message": f"Uploaded and indexed {file.filename}",
        "pages": len(pages),
        "chunks": len(chunks)
    }

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # Get or create session history
    if request.session_id not in sessions:
        sessions[request.session_id] = []

    history = sessions[request.session_id]
    answer, sources, updated_history = chat(request.question, history)
    sessions[request.session_id] = updated_history

    return {
        "answer": answer,
        "sources": sorted(set(sources)),
        "session_id": request.session_id
    }

@app.get("/")
async def root():
    return {"status": "Study Buddy API is running"}