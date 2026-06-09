import chromadb
from dotenv import load_dotenv
import os
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def get_collection(collection_name="study_buddy"):
    chroma = chromadb.PersistentClient(path="./chroma_db")
    return chroma.get_collection(name=collection_name)

def retrieve(question, n_results=3):
    # Embed the question
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=question
    )
    question_embedding = result.embeddings[0].values

    # Search ChromaDB for nearest chunks
    collection = get_collection()
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=n_results
    )

    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "page": results["metadatas"][0][i]["page"],
            "distance": results["distances"][0][i]
        })

    return chunks


if __name__ == "__main__":
    question = "What role do songs play in Westeros history?"

    print(f"Question: {question}\n")
    chunks = retrieve(question)

    for i, chunk in enumerate(chunks):
        print(f"--- Result {i+1} (Page {chunk['page']}, distance: {chunk['distance']:.4f}) ---")
        print(chunk["text"][:300])
        print()