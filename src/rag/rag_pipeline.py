from .vector_db import FreeVectorDB
from .openrouter_client import OpenRouterClient
from ..utils.safety import SafetyChecker

class HealthCompassRAG:
    """Complete RAG pipeline for Health Compass"""
    
    def __init__(self):
        print("🚀 Initializing Health Compass RAG System...\n")
        
        # Initialize components
        self.vector_db = FreeVectorDB()
        self.llm = OpenRouterClient(
            model="mistralai/mistral-7b-instruct:free"
        )
        self.safety = SafetyChecker()
        
        print("\n✅ RAG System ready!")
    
    def create_health_prompt(self, query: str, context_docs: list) -> list:
        """Create medical-safe prompt with context"""
        
        # Format context from retrieved documents
        context_parts = []
        for i, doc in enumerate(context_docs, 1):
            context_parts.append(
                f"[Source {i}] {doc['metadata']['source']} - {doc['metadata']['title']}\n"
                f"Organization: {doc['metadata']['organization']}\n"
                f"Credibility: {doc['metadata']['credibility']}\n"
                f"Content: {doc['document']}\n"
            )
        
        context_text = "\n".join(context_parts)
        
        # System prompt with safety rules
        system_message = """You are Health Compass, an educational health information assistant.

🔴 CRITICAL SAFETY RULES (NEVER VIOLATE):

1. ❌ NEVER diagnose medical conditions
2. ❌ NEVER provide medical advice or treatment recommendations
3. ❌ NEVER suggest medications or dosages
4. ✅ ALWAYS recommend consulting healthcare professionals
5. ✅ Use ONLY the provided context from trusted sources
6. ✅ Cite sources clearly (e.g., "According to MedlinePlus..." or "The CDC states...")
7. ✅ Use simple, clear language accessible to general public
8. ✅ Include appropriate disclaimers

Your ONLY role is EDUCATION - helping people understand health information so they can have informed conversations with their doctors.

For emergency symptoms, immediately tell user to call 911 or seek emergency care."""

        # User prompt with context
        user_message = f"""Medical Context from Trusted Sources:

{context_text}

---

User's Question: {query}

Please provide an educational response that:
1. Explains the topic clearly using simple language
2. Cites which sources you're drawing from (mention organization name)
3. Includes a reminder to consult healthcare professionals
4. Flags if this topic requires immediate medical attention

Educational Response:"""

        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    
    def query(self, user_question: str, n_results: int = 5) -> dict:
        """Process user query through complete RAG pipeline"""
        
        print(f"\n{'='*60}")
        print(f"Processing query: {user_question[:80]}...")
        print(f"{'='*60}\n")
        
        # Step 1: Safety check
        print("🔒 Step 1: Safety check...")
        safety_result = self.safety.check_query(user_question)
        print(f"   Safety level: {safety_result['level']}")
        
        if safety_result['level'] == 'EMERGENCY':
            print("   ⚠️ EMERGENCY DETECTED - Returning immediate care message")
            return {
                'answer': safety_result['message'],
                'sources': [],
                'safety_alert': safety_result,
                'is_emergency': True
            }
        
        # Step 2: Search vector database
        print(f"\n🔍 Step 2: Searching for relevant information...")
        context_docs = self.vector_db.search(user_question, n_results=n_results)
        print(f"   Found {len(context_docs)} relevant documents")
        
        if not context_docs:
            print("   ⚠️ No relevant information found")
            return {
                'answer': (
                    "I couldn't find relevant information in my database about this topic. "
                    "Please consult a healthcare professional for accurate, personalized information."
                ),
                'sources': [],
                'safety_alert': safety_result,
                'is_emergency': False
            }
        
        # Step 3: Generate response with LLM
        print(f"\n🤖 Step 3: Generating educational response...")
        messages = self.create_health_prompt(user_question, context_docs)
        answer = self.llm.generate(messages, temperature=0.2, max_tokens=1500)
        print(f"   Response generated ({len(answer)} characters)")
        
        # Step 4: Extract unique sources
        sources = []
        seen = set()
        for doc in context_docs:
            key = (doc['metadata']['source'], doc['metadata']['url'])
            if key not in seen:
                seen.add(key)
                sources.append({
                    'source': doc['metadata']['source'],
                    'url': doc['metadata']['url'],
                    'title': doc['metadata']['title'],
                    'organization': doc['metadata']['organization'],
                    'credibility': doc['metadata']['credibility']
                })
        
        print(f"\n✅ Query processed successfully!")
        print(f"{'='*60}\n")
        
        return {
            'answer': answer,
            'sources': sources,
            'safety_alert': safety_result,
            'is_emergency': False,
            'context_docs': context_docs  # For debugging
        }

# Test the RAG pipeline
if __name__ == "__main__":
    print("Testing RAG Pipeline...\n")
    
    try:
        rag = HealthCompassRAG()
        
        # Test queries
        test_queries = [
            "What is diabetes?",
            "How does aspirin work?",
            "What causes headaches?"
        ]
        
        for query in test_queries:
            print(f"\n{'='*80}")
            print(f"TEST QUERY: {query}")
            print(f"{'='*80}")
            
            result = rag.query(query, n_results=3)
            
            print(f"\nANSWER:\n{result['answer']}")
            print(f"\nSOURCES:")
            for source in result['sources']:
                print(f"  - {source['source']}: {source['title']}")
            
            print("\n" + "="*80)
            input("\nPress Enter for next query...")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Run the data collection: python run_pipeline.py")
        print("2. Set OPENROUTER_API_KEY in .env file")