from dotenv import load_dotenv
import os
import traceback
from google import genai
from retriever import retrieve

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# List of models to try in order (first available will be used)
# Based on check_models.py output
FALLBACK_MODELS = [
    "gemini-2.5-flash",      # ⭐ Fastest & newest
    "gemini-2.5-pro",        # More capable
    "gemini-2.0-flash",      # Stable
    "gemini-2.0-flash-001",  # Backup
]

def chat(question, history=[]):
    try:
        # Retrieve relevant chunks
        chunks = retrieve(question, n_results=3)

        context = ""
        sources = []
        for chunk in chunks:
            context += f"[Page {chunk['page']}]: {chunk['text']}\n\n"
            sources.append(chunk['page'])

        # Build conversation history string
        history_text = ""
        for turn in history:
            history_text += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n\n"

        # Prompt includes history + context
        prompt = f"""You are a study assistant. Answer using ONLY the context below.
Always cite which page the information came from.
If the answer isn't in the context, say "I couldn't find that in the document."

Previous conversation:
{history_text}
Context:
{context}

Question: {question}

Answer:"""

        # Try models with fallback support
        response = None
        last_error = None
        
        for model in FALLBACK_MODELS:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                break  # Exit if successful
            except Exception as e:
                last_error = e
                continue  # Try next model
        
        if response is None:
            raise last_error  # All models failed

        answer = response.text

        # Add this turn to history
        history.append({
            "user": question,
            "assistant": answer
        })

        return answer, sources, history
    
    except Exception as e:
        # Error handling
        print(f"\n❌ Error: {type(e).__name__}")
        print(f"Message: {str(e)}")
        
        # Return error message but keep history intact
        error_message = f"Sorry, I encountered an error: {str(e)[:100]}"
        return error_message, [], history


if __name__ == "__main__":
    print("Study Buddy — type 'quit' to exit\n")
    history = []

    while True:
        question = input("You: ").strip()
        if question.lower() == "quit":
            break
        if not question:
            continue

        answer, sources, history = chat(question, history)
        print(f"\nAssistant: {answer}")
        print(f"Sources: Pages {sorted(set(sources)) if sources else 'N/A'}\n")