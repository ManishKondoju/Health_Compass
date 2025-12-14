import json
from pathlib import Path
import re
from tqdm import tqdm

class TextProcessor:
    """Process and clean scraped health data"""
    
    def __init__(self):
        self.raw_dir = Path("data/raw")
        self.processed_dir = Path("data/processed")
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def clean_text(self, text):
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep medical terms
        text = re.sub(r'[^\w\s\-,.()\[\]:/]', '', text)
        return text.strip()
    
    def chunk_text(self, text, chunk_size=400, overlap=50):
        """Split text into overlapping chunks"""
        if not text or len(text) < 100:
            return []
        
        words = text.split()
        if len(words) < 50:
            return [text]
        
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk) > 100:  # Only meaningful chunks
                chunks.append(chunk)
        
        return chunks
    
    def process_medlineplus(self):
        """Process MedlinePlus data"""
        print("📝 Processing MedlinePlus data...")
        
        medline_dir = self.raw_dir / "medlineplus"
        if not medline_dir.exists():
            print("⚠️ MedlinePlus data not found")
            return []
        
        processed_docs = []
        
        files = list(medline_dir.glob("*.json"))
        for file in tqdm(files, desc="Processing MedlinePlus"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Process summary
                if data.get('summary'):
                    chunks = self.chunk_text(data['summary'])
                    for i, chunk in enumerate(chunks):
                        processed_docs.append({
                            'source': 'MedlinePlus',
                            'url': data.get('url', ''),
                            'title': data.get('title', ''),
                            'section': 'Summary',
                            'chunk_id': i,
                            'text': self.clean_text(chunk),
                            'metadata': {
                                'credibility': 'high',
                                'source_type': 'government',
                                'organization': 'National Library of Medicine'
                            }
                        })
                
                # Process sections
                for section in data.get('sections', []):
                    chunks = self.chunk_text(section.get('content', ''))
                    for i, chunk in enumerate(chunks):
                        processed_docs.append({
                            'source': 'MedlinePlus',
                            'url': data.get('url', ''),
                            'title': data.get('title', ''),
                            'section': section.get('heading', 'Content'),
                            'chunk_id': i,
                            'text': self.clean_text(chunk),
                            'metadata': {
                                'credibility': 'high',
                                'source_type': 'government',
                                'organization': 'National Library of Medicine'
                            }
                        })
                
            except Exception as e:
                print(f"⚠️ Error processing {file}: {e}")
                continue
        
        print(f"✅ Processed {len(processed_docs)} MedlinePlus chunks")
        return processed_docs
    
    def process_cdc(self):
        """Process CDC data"""
        print("📝 Processing CDC data...")
        
        cdc_dir = self.raw_dir / "cdc"
        if not cdc_dir.exists():
            print("⚠️ CDC data not found")
            return []
        
        processed_docs = []
        
        files = list(cdc_dir.glob("*.json"))
        for file in tqdm(files, desc="Processing CDC"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Combine content items
                full_text = ' '.join([
                    item.get('text', '') 
                    for item in data.get('content', [])
                ])
                
                if full_text:
                    chunks = self.chunk_text(full_text)
                    for i, chunk in enumerate(chunks):
                        processed_docs.append({
                            'source': 'CDC',
                            'url': data.get('url', ''),
                            'title': data.get('title', ''),
                            'section': 'Main Content',
                            'chunk_id': i,
                            'text': self.clean_text(chunk),
                            'metadata': {
                                'credibility': 'high',
                                'source_type': 'government',
                                'organization': 'Centers for Disease Control'
                            }
                        })
                
            except Exception as e:
                continue
        
        print(f"✅ Processed {len(processed_docs)} CDC chunks")
        return processed_docs
    
    def process_all(self):
        """Process all scraped data"""
        print("🔄 Starting data processing...")
        
        all_docs = []
        
        # Process MedlinePlus
        all_docs.extend(self.process_medlineplus())
        
        # Process CDC
        all_docs.extend(self.process_cdc())
        
        # Save processed data
        if all_docs:
            output_file = self.processed_dir / "all_documents.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_docs, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Total: {len(all_docs)} document chunks processed")
            print(f"💾 Saved to: {output_file}")
        else:
            print("⚠️ No documents processed!")
        
        return all_docs

if __name__ == "__main__":
    processor = TextProcessor()
    processor.process_all()