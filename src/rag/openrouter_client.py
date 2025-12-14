import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenRouterClient:
    """
    FREE LLM access via OpenRouter
    
    Free Models:
    - meta-llama/llama-3.2-3b-instruct:free (RECOMMENDED)
    - google/gemini-flash-1.5:free
    - mistralai/mistral-7b-instruct:free
    """
    
    def __init__(self, model="mistralai/mistral-7b-instruct:free"):
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            raise ValueError(
                "❌ OPENROUTER_API_KEY not found in .env file!\n"
                "Get your free key from: https://openrouter.ai/"
            )
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model
        
        # Better rate limits
        self.extra_headers = {
            "HTTP-Referer": os.getenv("SITE_URL", ""),
            "X-Title": os.getenv("SITE_NAME", "Health Compass"),
        }
        
        print(f"✅ OpenRouter initialized with: {model}")
    
    def generate(self, messages, temperature=0.3, max_tokens=2000):
        """Generate response"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                extra_headers=self.extra_headers
            )
            return response.choices[0].message.content
        
        except Exception as e:
            error_msg = str(e)
            if "credit balance" in error_msg.lower():
                return "❌ OpenRouter credits exhausted. Please add more credits or use a different API key."
            return f"❌ Error: {error_msg}"
    
    def test_connection(self):
        """Test if API key works"""
        try:
            messages = [{"role": "user", "content": "Say 'Hello!'"}]
            response = self.generate(messages, max_tokens=10)
            return "Hello" in response or "hello" in response
        except:
            return False

# Test
if __name__ == "__main__":
    print("Testing OpenRouter connection...")
    
    client = OpenRouterClient()
    
    if client.test_connection():
        print("✅ Connection successful!")
        
        # Test query
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain what diabetes is in one sentence."}
        ]
        
        response = client.generate(messages)
        print(f"\nTest Response:\n{response}")
    else:
        print("❌ Connection failed! Check your API key in .env file")