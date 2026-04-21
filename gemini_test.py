"""
Simple Gemini 2.5 test script for beginners
"""
import os
from dotenv import load_dotenv
from google import genai

# Load API key từ .env file
load_dotenv()

# Tạo Gemini client
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file!")

client = genai.Client(api_key=api_key)



# Test 1: Hỏi câu đơn giản
print("=" * 50)
print("Test 1: Simple Question")
print("=" * 50)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Xin chào, bạn tên gì?"
)

print(response.text)

# Test 2: Hỏi về code Python
print("\n" + "=" * 50)
print("Test 2: Code Question")
print("=" * 50)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Giải thích async/await trong Python một cách đơn giản"
)

print(response.text)

# Test 3: Hỏi về FastAPI
print("\n" + "=" * 50)
print("Test 3: FastAPI Question")
print("=" * 50)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="FastAPI là gì? Tại sao nó nhanh?"
)

print(response.text)

print("\n✅ Tất cả test hoàn tất!")

