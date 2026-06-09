from dotenv import load_dotenv
import os
from google import genai
from loader import load_pdf
from chunker import chunk_pages

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def embed_chunks(chunks):
    embedded = []

    for chunk in chunks:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=chunk["text"]
        )

        embedded.append({
            "text": chunk["text"],
            "page": chunk["page"],
            "chunk_index": chunk["chunk_index"],
            "embedding": result.embeddings[0].values
        })

        print(f"Embedded chunk {chunk['chunk_index'] + 1}/{len(chunks)} (page {chunk['page']})")

    return embedded


if __name__ == "__main__":
    pages = load_pdf("The Public History of Westeros Brethorst.pdf")
    chunks = chunk_pages(pages)
    embedded_chunks = embed_chunks(chunks)

    print(f"\nDone! {len(embedded_chunks)} chunks embedded.")
    print(f"Embedding size: {len(embedded_chunks[0]['embedding'])} dimensions")