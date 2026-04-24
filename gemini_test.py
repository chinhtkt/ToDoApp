"""
Simple Gemini 2.5 test script for beginners
"""
import os
from dotenv import load_dotenv
from google import genai

# Load API key from .env file
load_dotenv()

# Create Gemini client
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file!")

client = genai.Client(api_key=api_key)



# Test 1: Simple question
print("=" * 50)
print("Test 1: Simple Question")
print("=" * 50)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hello, what's your name?"
)

print(response.text)

# Test 2: Question about Python code
print("\n" + "=" * 50)
print("Test 2: Code Question")
print("=" * 50)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain async/await in Python in a simple way"
)

print(response.text)

# Test 3: Question about FastAPI
print("\n" + "=" * 50)
print("Test 3: FastAPI Question")
print("=" * 50)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is FastAPI? Why is it fast?"
)

print(response.text)

print("\n✅ All tests completed!")

