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

def generate_answer(question):
    try:
        # Step 1: retrieve relevant chunks
        print("📚 Retrieving relevant chunks...")
        chunks = retrieve(question, n_results=3)
        
        if not chunks:
            return {
                "answer": "No relevant information found in the document.",
                "sources": []
            }

        # Step 2: build context from chunks
        context = ""
        sources = []
        for chunk in chunks:
            context += f"[Page {chunk['page']}]: {chunk['text']}\n\n"
            sources.append(chunk['page'])

        # Step 3: build the prompt
        prompt = f"""You are a study assistant. Answer the question using ONLY the context provided below.
If the answer is not in the context, say "I couldn't find that in the document."
Always mention which page the information came from.

Context:
{context}

Question: {question}

Answer:"""

        # Step 4: send to Gemini with fallback models
        response = None
        last_error = None
        
        for model in FALLBACK_MODELS:
            try:
                print(f"🤖 Trying model: {model}...")
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                print(f"✅ Success with {model}")
                break  # Exit loop if successful
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                print(f"   ⚠️  {model} unavailable: {str(e)[:80]}")
                continue  # Try next model
        
        if response is None:
            raise last_error  # All models failed

        return {
            "answer": response.text,
            "sources": sorted(set(sources))
        }
    
    except Exception as e:
        # Detailed error reporting
        print("\n❌ ERROR OCCURRED")
        print("=" * 60)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print("=" * 60)
        print("\nFull Traceback:")
        traceback.print_exc()
        print("=" * 60)
        
        # Provide helpful suggestions
        error_str = str(e).lower()
        
        if "api key" in error_str or "authentication" in error_str or "403" in error_str:
            print("\n💡 Suggestion: Check your GOOGLE_API_KEY in .env file")
            print("   - Is it set correctly?")
            print("   - Is it a valid Google API key with Gemini access?")
        
        elif "404" in error_str or "not found" in error_str or "no longer available" in error_str:
            print("\n💡 Suggestion: All Gemini models are currently unavailable")
            print("   - Check Google's AI Studio for available models: https://aistudio.google.com")
            print("   - Your API key may not have access to newer models")
            print("   - Try enabling Gemini API in Google Cloud Console")
        
        elif "rate" in error_str or "quota" in error_str:
            print("\n💡 Suggestion: You may have hit rate limits or exceeded quota")
            print("   - Wait a few minutes before retrying")
            print("   - Check your Google Cloud billing/quotas")
        
        elif "network" in error_str or "connection" in error_str or "timeout" in error_str:
            print("\n💡 Suggestion: Network connection issue")
            print("   - Check your internet connection")
            print("   - Try again in a moment")
        
        return {
            "answer": f"Error: {type(e).__name__} - {str(e)}",
            "sources": []
        }


if __name__ == "__main__":
    question = "What role do songs play in Westeros history?"

    print(f"Question: {question}\n")
    result = generate_answer(question)

    print(f"\n✅ Answer:\n{result['answer']}")
    print(f"\n📖 Sources: Pages {result['sources'] if result['sources'] else 'Unknown'}")