import chromadb
from dotenv import load_dotenv
import os
from google import genai
from loader import load_pdf
from chunker import chunk_pages
from embedder import embed_chunks

load_dotenv()

def store_in_chroma(embedded_chunks, collection_name="study_buddy"):
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Create or load collection
    collection = client.get_or_create_collection(name=collection_name)

    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for chunk in embedded_chunks:
        ids.append(f"chunk_{chunk['chunk_index']}")
        embeddings.append(chunk["embedding"])
        documents.append(chunk["text"])
        metadatas.append({"page": chunk["page"]})

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    print(f"Stored {collection.count()} chunks in ChromaDB")
    return collection


if __name__ == "__main__":
    pages = load_pdf("The Public History of Westeros Brethorst.pdf")
    chunks = chunk_pages(pages)
    embedded_chunks = embed_chunks(chunks)
    collection = store_in_chroma(embedded_chunks)
    print("ChromaDB ready at ./chroma_db")