"""
Health Compass Data Pipeline
Run this once to collect and process health data
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.scrapers.medlineplus_scraper import MedlinePlusScraper
from src.scrapers.cdc_scraper import CDCScraper
from src.processors.text_processor import TextProcessor
from src.rag.vector_db import FreeVectorDB
from src.utils.config import Config

def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print("🏥 HEALTH COMPASS - DATA PIPELINE")
    print("="*70)
    print("This will collect and process health information from trusted sources.")
    print("Estimated time: 10-15 minutes")
    print("="*70 + "\n")

def validate_setup():
    """Check if everything is set up correctly"""
    print("🔧 Validating setup...")
    
    is_valid, errors = Config.validate()
    
    if not is_valid:
        print("\n❌ Setup validation failed:")
        for error in errors:
            print(f"   - {error}")
        print("\nPlease fix these issues and try again.")
        return False
    
    print("✅ Setup validated successfully!\n")
    return True

def run_scraping(limit=50):
    """Step 1: Scrape data from medical websites"""
    print("\n" + "="*70)
    print("STEP 1: DATA COLLECTION")
    print("="*70 + "\n")
    
    # Scrape MedlinePlus
    print("📥 Scraping MedlinePlus (U.S. National Library of Medicine)...")
    medline_scraper = MedlinePlusScraper()
    medline_count = medline_scraper.scrape_all(limit=limit)
    print(f"✅ MedlinePlus: {medline_count} topics collected\n")
    
    # Scrape CDC
    print("📥 Scraping CDC (Centers for Disease Control and Prevention)...")
    cdc_scraper = CDCScraper()
    cdc_count = cdc_scraper.scrape_all(limit=limit)
    print(f"✅ CDC: {cdc_count} pages collected\n")
    
    total = medline_count + cdc_count
    print(f"✅ Total sources scraped: {total}\n")
    
    return total > 0

def run_processing():
    """Step 2: Process and clean scraped data"""
    print("\n" + "="*70)
    print("STEP 2: DATA PROCESSING")
    print("="*70 + "\n")
    
    processor = TextProcessor()
    documents = processor.process_all()
    
    if documents:
        print(f"✅ Successfully processed {len(documents)} document chunks\n")
        return documents
    else:
        print("❌ No documents were processed\n")
        return []

def build_database(documents):
    """Step 3: Build vector database"""
    print("\n" + "="*70)
    print("STEP 3: BUILDING VECTOR DATABASE")
    print("="*70 + "\n")
    
    if not documents:
        print("❌ No documents to add to database")
        return False
    
    print("🗄️ Initializing vector database...")
    vector_db = FreeVectorDB()
    
    print("📊 Adding documents to database...")
    vector_db.add_documents(documents)
    
    stats = vector_db.get_stats()
    print(f"\n✅ Database built successfully!")
    print(f"   📚 Total documents: {stats['total_documents']}")
    print(f"   🔢 Embedding dimensions: {stats['embedding_dimension']}\n")
    
    return True

def test_system():
    """Step 4: Test the RAG system"""
    print("\n" + "="*70)
    print("STEP 4: SYSTEM TEST")
    print("="*70 + "\n")
    
    try:
        from src.rag.rag_pipeline import HealthCompassRAG
        
        print("🧪 Initializing RAG system...")
        rag = HealthCompassRAG()
        
        print("🔍 Running test query: 'What is diabetes?'\n")
        result = rag.query("What is diabetes?", n_results=3)
        
        print("✅ Test query successful!")
        print(f"\nAnswer preview:")
        print(f"{result['answer'][:200]}...\n")
        
        print(f"Sources found: {len(result['sources'])}")
        for source in result['sources']:
            print(f"   - {source['source']}: {source['title']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main pipeline execution"""
    print_banner()
    
    # Step 0: Validate
    if not validate_setup():
        return
    
    # Ask user for limit
    print("How many sources to scrape from each website?")
    print("  - 50 (recommended for testing, ~5-10 minutes)")
    print("  - 100 (good coverage, ~15-20 minutes)")
    print("  - 200 (comprehensive, ~30-40 minutes)")
    
    try:
        limit_input = input("\nEnter number (default 50): ").strip()
        limit = int(limit_input) if limit_input else 50
    except:
        limit = 50
    
    print(f"\n✅ Will scrape {limit} sources from each website\n")
    
    # Step 1: Scrape data
    if not run_scraping(limit=limit):
        print("❌ Data collection failed. Exiting.")
        return
    
    # Step 2: Process data
    documents = run_processing()
    if not documents:
        print("❌ Data processing failed. Exiting.")
        return
    
    # Step 3: Build database
    if not build_database(documents):
        print("❌ Database creation failed. Exiting.")
        return
    
    # Step 4: Test system
    test_system()
    
    # Success!
    print("\n" + "="*70)
    print("✅ SETUP COMPLETE!")
    print("="*70)
    print("\nYou can now run the Health Compass app:")
    print("   streamlit run src/app.py")
    print("\nOr test the RAG system:")
    print("   python -m src.rag.rag_pipeline")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Pipeline interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print("\nPlease check the error and try again.")