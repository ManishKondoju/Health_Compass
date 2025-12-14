import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import json
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm

class FreeVectorDB:
    """100% Free local vector database with ChromaDB"""
    
    def __init__(self, persist_dir="data/chroma_db"):
        print("🔧 Initializing vector database...")
        
        self.persist_dir = persist_dir
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB (local, persistent)
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Load free embedding model (runs locally)
        print("📥 Loading embedding model (this may take a minute)...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Embedding model loaded (384 dimensions)")
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="health_compass",
            metadata={"description": "Health information from trusted sources"}
        )
        
        print(f"✅ Vector database ready ({self.collection.count()} documents)")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings locally (FREE)"""
        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32
        )
        return embeddings.tolist()
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to vector database"""
        if not documents:
            print("⚠️ No documents to add")
            return
        
        print(f"\n📊 Adding {len(documents)} documents to database...")
        
        # Prepare data
        ids = [f"doc_{i:06d}" for i in range(len(documents))]
        texts = [doc['text'] for doc in documents]
        metadatas = []
        
        for doc in documents:
            metadata = {
                'source': doc.get('source', 'Unknown'),
                'url': doc.get('url', ''),
                'title': doc.get('title', 'Untitled'),
                'section': doc.get('section', 'General'),
                'credibility': doc.get('metadata', {}).get('credibility', 'medium'),
                'organization': doc.get('metadata', {}).get('organization', 'Unknown')
            }
            metadatas.append(metadata)
        
        # Generate embeddings
        print("🔢 Generating embeddings...")
        embeddings = self.embed_texts(texts)
        
        # Add to ChromaDB in batches (to avoid memory issues)
        batch_size = 100
        total_batches = (len(documents) - 1) // batch_size + 1
        
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            batch_num = i // batch_size + 1
            
            try:
                self.collection.add(
                    ids=ids[i:end_idx],
                    embeddings=embeddings[i:end_idx],
                    documents=texts[i:end_idx],
                    metadatas=metadatas[i:end_idx]
                )
                print(f"✅ Batch {batch_num}/{total_batches} added")
            except Exception as e:
                print(f"⚠️ Error adding batch {batch_num}: {e}")
                continue
        
        print(f"\n✅ Successfully added {len(documents)} documents!")
        print(f"💾 Database now contains {self.collection.count()} total documents")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for relevant documents"""
        # Generate query embedding
        query_embedding = self.embed_texts([query])[0]
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        count = self.collection.count()
        return {
            'total_documents': count,
            'collection_name': self.collection.name,
            'embedding_dimension': 384
        }
    
    def delete_all(self):
        """Delete all documents (use with caution!)"""
        print("⚠️ Deleting all documents...")
        self.client.delete_collection(name="health_compass")
        self.collection = self.client.get_or_create_collection(
            name="health_compass",
            metadata={"description": "Health information from trusted sources"}
        )
        print("✅ Database cleared")

# Test the database
if __name__ == "__main__":
    print("Testing Vector Database...\n")
    
    db = FreeVectorDB()
    
    # Check if database has data
    stats = db.get_stats()
    print(f"\nDatabase stats: {stats}")
    
    if stats['total_documents'] == 0:
        print("\n⚠️ Database is empty! Run the data pipeline first:")
        print("   python run_pipeline.py")
    else:
        # Test search
        print("\n🔍 Testing search...")
        results = db.search("What causes diabetes?", n_results=3)
        
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['metadata']['title']}")
            print(f"   Source: {result['metadata']['source']}")
            print(f"   Preview: {result['document'][:150]}...")