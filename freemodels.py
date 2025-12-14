import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

FREE_MODELS = [
    "google/gemini-flash-1.5:free",
    "google/gemini-flash-1.5-8b:free",
    "mistralai/mistral-7b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "meta-llama/llama-3.2-1b-instruct:free",
]

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

print("Testing all free models...\n")

for model in FREE_MODELS:
    try:
        print(f"Testing {model}...")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say 'Hello!'"}],
            max_tokens=10
        )
        print(f"✅ SUCCESS: {response.choices[0].message.content}\n")
        print(f"🎉 RECOMMENDED MODEL: {model}\n")
        break
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate" in error_str.lower():
            print(f"⚠️  Rate limited\n")
        else:
            print(f"❌ Error: {str(e)[:100]}\n")

print("=" * 60)