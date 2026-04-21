import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file!")

def get_client():
    return genai.Client(api_key=api_key)

