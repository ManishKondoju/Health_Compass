import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from tqdm import tqdm

class CDCScraper:
    """Scrape CDC.gov - FREE government health resource"""
    
    def __init__(self, output_dir="data/raw/cdc"):
        self.base_url = "https://www.cdc.gov"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Educational Project)'
        }
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_disease_pages(self, limit=None):
        """Get list of disease pages"""
        print("📋 Fetching CDC disease pages...")
        
        # CDC diseases A-Z
        pages = []
        
        # Common health topics URLs
        topic_urls = [
            f"{self.base_url}/az/index.html",
            f"{self.base_url}/diseasesconditions/index.html",
        ]
        
        for url in topic_urls:
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all disease links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    text = link.text.strip()
                    
                    if text and len(text) > 3:  # Valid topic
                        full_url = href if href.startswith('http') else self.base_url + href
                        
                        if full_url not in [p['url'] for p in pages]:
                            pages.append({
                                'title': text,
                                'url': full_url
                            })
                
                time.sleep(1)
                
            except Exception as e:
                print(f"⚠️ Error: {e}")
                continue
        
        if limit:
            pages = pages[:limit]
        
        print(f"✅ Found {len(pages)} pages")
        return pages
    
    def scrape_page(self, url):
        """Scrape individual CDC page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            content = {
                'url': url,
                'title': '',
                'content': []
            }
            
            # Get title
            h1 = soup.find('h1')
            if h1:
                content['title'] = h1.text.strip()
            
            # Get main content
            main = soup.find('main') or soup.find('div', class_='content')
            if main:
                for elem in main.find_all(['p', 'h2', 'h3', 'li']):
                    text = elem.get_text(strip=True)
                    if len(text) > 20:  # Meaningful content
                        content['content'].append({
                            'type': elem.name,
                            'text': text
                        })
            
            return content
            
        except Exception as e:
            return None
    
    def scrape_all(self, limit=50):
        """Scrape multiple pages"""
        print("🚀 Starting CDC scraping...")
        
        pages = self.get_disease_pages(limit=limit)
        
        successful = 0
        for i, page in enumerate(tqdm(pages, desc="Scraping CDC")):
            try:
                data = self.scrape_page(page['url'])
                
                if data and data['content']:
                    filename = f"page_{i:04d}.json"
                    with open(self.output_dir / filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    successful += 1
                
                time.sleep(1)
                
            except Exception as e:
                continue
        
        print(f"\n✅ Successfully scraped {successful}/{len(pages)} pages")
        return successful

if __name__ == "__main__":
    scraper = CDCScraper()
    scraper.scrape_all(limit=50)