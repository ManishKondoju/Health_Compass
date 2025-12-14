"""
Quick test to verify Health Compass setup
Run this to check if everything is configured correctly
"""

import sys
from pathlib import Path

def test_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (need 3.8+)")
        return False

def test_imports():
    """Check if required packages are installed"""
    print("\n📦 Checking required packages...")
    
    required = {
        'streamlit': 'Streamlit',
        'chromadb': 'ChromaDB',
        'sentence_transformers': 'SentenceTransformers',
        'beautifulsoup4': 'BeautifulSoup4',
        'requests': 'Requests',
        'openai': 'OpenAI SDK',
        'dotenv': 'python-dotenv'
    }
    
    missing = []
    for package, name in required.items():
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

def test_env_file():
    """Check if .env file exists and has API key"""
    print("\n🔑 Checking .env configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("   ❌ .env file not found")
        print("   Create .env file with:")
        print("   OPENROUTER_API_KEY=sk-or-v1-your-key-here")
        return False
    
    print("   ✅ .env file exists")
    
    # Check if API key is set
    with open(env_file) as f:
        content = f.read()
        if 'OPENROUTER_API_KEY' in content and 'your-key-here' not in content:
            print("   ✅ API key configured")
            return True
        else:
            print("   ⚠️ API key not configured or using placeholder")
            print("   Get your free key from: https://openrouter.ai/")
            return False

def test_folders():
    """Check if required folders exist"""
    print("\n📁 Checking folder structure...")
    
    required_folders = [
        'data',
        'data/raw',
        'data/raw/medlineplus',
        'data/raw/cdc',
        'data/processed',
        'data/chroma_db',
        'src',
        'src/scrapers',
        'src/processors',
        'src/rag',
        'src/utils'
    ]
    
    missing = []
    for folder in required_folders:
        path = Path(folder)
        if path.exists():
            print(f"   ✅ {folder}/")
        else:
            print(f"   ❌ {folder}/ - MISSING")
            missing.append(folder)
    
    if missing:
        print(f"\n⚠️ Missing folders will be created automatically")
    
    return True

def test_openrouter_connection():
    """Test OpenRouter API connection"""
    print("\n🔌 Testing OpenRouter connection...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from src.rag.openrouter_client import OpenRouterClient
        
        client = OpenRouterClient()
        if client.test_connection():
            print("   ✅ OpenRouter API connection successful")
            return True
        else:
            print("   ❌ OpenRouter API connection failed")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_database():
    """Check if vector database has data"""
    print("\n🗄️ Checking vector database...")
    
    db_path = Path("data/chroma_db")
    if not db_path.exists() or not list(db_path.glob("*")):
        print("   ⚠️ Database is empty")
        print("   Run: python run_pipeline.py")
        return False
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from src.rag.vector_db import FreeVectorDB
        
        db = FreeVectorDB()
        stats = db.get_stats()
        
        if stats['total_documents'] > 0:
            print(f"   ✅ Database has {stats['total_documents']} documents")
            return True
        else:
            print("   ⚠️ Database is empty")
            print("   Run: python run_pipeline.py")
            return False
    except Exception as e:
        print(f"   ⚠️ Cannot check database: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🏥 HEALTH COMPASS - SETUP VERIFICATION")
    print("="*70 + "\n")
    
    results = {
        'Python Version': test_python_version(),
        'Required Packages': test_imports(),
        'Environment File': test_env_file(),
        'Folder Structure': test_folders(),
        'OpenRouter API': test_openrouter_connection(),
        'Vector Database': test_database()
    }
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70 + "\n")
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test:.<50} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED - System ready!")
        print("\nYou can now run:")
        print("   streamlit run src/app.py")
    else:
        print("⚠️ SOME TESTS FAILED - Please fix issues above")
        
        if not results['Vector Database']:
            print("\nTo set up the database:")
            print("   python run_pipeline.py")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()