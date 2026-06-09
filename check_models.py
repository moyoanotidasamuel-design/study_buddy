from dotenv import load_dotenv
import os
from google import genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found in .env file!")
    print("   Please add: GOOGLE_API_KEY=your_key_here")
    exit(1)

print("🔍 Checking available models...\n")

try:
    client = genai.Client(api_key=api_key)
    
    # List all available models
    models = client.models.list()
    
    print("✅ SUCCESS! Found available models:\n")
    
    available_models = []
    for model in models:
        model_name = model.name
        # Extract the short name (e.g., "gemini-1.5-flash" from "models/gemini-1.5-flash")
        short_name = model_name.replace("models/", "")
        available_models.append(short_name)
        print(f"   • {short_name}")
    
    print(f"\n📊 Total: {len(available_models)} models available")
    
    if available_models:
        print(f"\n💡 Recommended: Use '{available_models[0]}' in your code")
        print(f"\n📝 Update your generator.py with:")
        print(f'   FALLBACK_MODELS = ["{available_models[0]}"]')

except Exception as e:
    print(f"❌ ERROR: Could not list models")
    print(f"   Error: {str(e)}")
    print(f"\n💡 Possible fixes:")
    print(f"   1. Check your API key is correct")
    print(f"   2. Enable the Generative Language API in Google Cloud Console")
    print(f"   3. Create a new API key from https://aistudio.google.com/app/apikey")