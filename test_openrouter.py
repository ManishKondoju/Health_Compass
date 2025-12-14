import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

print(f"API Key found: {api_key[:20]}..." if api_key else "❌ No API key found")
print()

if not api_key:
    print("Please set OPENROUTER_API_KEY in your .env file")
    exit(1)

try:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    print("Testing connection...")
    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct:free",
        messages=[
            {"role": "user", "content": "Say 'Hello!'"}
        ],
        max_tokens=10
    )
    
    print(f"✅ Success! Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPossible issues:")
    print("1. Check if your API key is correct")
    print("2. Visit https://openrouter.ai/ and verify your account")
    print("3. Check if you have free credits remaining")