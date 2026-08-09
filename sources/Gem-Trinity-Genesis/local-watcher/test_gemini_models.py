
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("LLM_API_KEY")

print(f"Testing API Key: {api_key[:5]}...{api_key[-5:]}")

if not api_key:
    print("Error: No API Key found")
    exit(1)

genai.configure(api_key=api_key)

print("\nListing available models:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
