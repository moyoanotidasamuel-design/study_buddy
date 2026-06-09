from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

result = client.models.embed_content(
    model="gemini-embedding-001",
    contents="What is the exam schedule?",
)

print(result)
#testing check
