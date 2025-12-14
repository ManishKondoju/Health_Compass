import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from tqdm import tqdm

class MedlinePlusScraper:
    """Scrape MedlinePlus - FREE government health resource"""
    
    def __init__(self, output_dir="data/raw/medlineplus"):
        self.base_url = "https://medlineplus.gov"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Educational Health Project)'
        }
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_health_topics(self, limit=None):
        """Get list of health topics from multiple sources"""
        print("📋 Fetching health topics list...")
        
        topics = []
        seen_urls = set()
        
        # Method 1: Try encyclopedia A-Z pages (most reliable)
        print("   Trying encyclopedia A-Z pages...")
        for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
            try:
                # Try different URL patterns
                urls_to_try = [
                    f"{self.base_url}/ency/encyclopedia_{letter}.htm",
                    f"{self.base_url}/encyclopedia_{letter}.htm",
                ]
                
                for url in urls_to_try:
                    try:
                        response = requests.get(url, headers=self.headers, timeout=10)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.content, 'html.parser')
                            
                            # Find all article links
                            for link in soup.find_all('a', href=True):
                                href = link['href']
                                text = link.text.strip()
                                
                                # Look for encyclopedia article links
                                if '/ency/article/' in href or '/ency/patientinstructions/' in href:
                                    full_url = self.base_url + href if not href.startswith('http') else href
                                    
                                    if full_url not in seen_urls and text and len(text) > 3:
                                        seen_urls.add(full_url)
                                        topics.append({
                                            'title': text,
                                            'url': full_url
                                        })
                            
                            break  # Success, move to next letter
                            
                    except:
                        continue
                
                time.sleep(1)  # Be polite
                
                # Stop if we have enough
                if limit and len(topics) >= limit:
                    break
                    
            except Exception as e:
                continue
        
        # Method 2: Try health topics index
        print("   Trying health topics index...")
        try:
            index_urls = [
                f"{self.base_url}/healthtopics.html",
                f"{self.base_url}/health-topics.html",
            ]
            
            for url in index_urls:
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            text = link.text.strip()
                            
                            # Look for various topic link patterns
                            if any(pattern in href for pattern in ['/english/', '/healthtopics/', '/ency/']):
                                full_url = self.base_url + href if not href.startswith('http') else href
                                
                                if full_url not in seen_urls and text and len(text) > 3:
                                    seen_urls.add(full_url)
                                    topics.append({
                                        'title': text,
                                        'url': full_url
                                    })
                        
                        break
                        
                except:
                    continue
            
            time.sleep(1)
            
        except Exception as e:
            print(f"   ⚠️ Health topics index: {e}")
        
        # Method 3: Direct article URLs (fallback with common topics)
        if len(topics) < 20:
            print("   Adding common health topics...")
            common_topics = [
                ('Diabetes', '/ency/article/001214.htm'),
                ('Heart Disease', '/ency/article/007115.htm'),
                ('High Blood Pressure', '/ency/article/000468.htm'),
                ('Asthma', '/ency/article/000141.htm'),
                ('Cancer Overview', '/ency/article/001289.htm'),
                ('Depression', '/ency/article/003213.htm'),
                ('Obesity', '/ency/article/003101.htm'),
                ('Pneumonia', '/ency/article/000145.htm'),
                ('Stroke', '/ency/article/000726.htm'),
                ('Arthritis', '/ency/article/001243.htm'),
                ('Alzheimer Disease', '/ency/article/000760.htm'),
                ('COVID-19', '/ency/article/007768.htm'),
                ('Influenza', '/ency/article/000080.htm'),
                ('Kidney Disease', '/ency/article/000468.htm'),
                ('Liver Disease', '/ency/article/000205.htm'),
                ('Migraine', '/ency/article/000709.htm'),
                ('Osteoporosis', '/ency/article/000360.htm'),
                ('Pneumonia', '/ency/article/000145.htm'),
                ('Tuberculosis', '/ency/article/000077.htm'),
                ('HIV/AIDS', '/ency/article/000594.htm'),
                ('Anemia', '/ency/article/000560.htm'),
                ('Anxiety', '/ency/article/003211.htm'),
                ('Back Pain', '/ency/article/007425.htm'),
                ('Bronchitis', '/ency/article/001087.htm'),
                ('Cholesterol', '/ency/article/003491.htm'),
                ('COPD', '/ency/article/000091.htm'),
                ('Dehydration', '/ency/article/000982.htm'),
                ('Eczema', '/ency/article/000853.htm'),
                ('Epilepsy', '/ency/article/000694.htm'),
                ('Fever', '/ency/article/003090.htm'),
                ('Gout', '/ency/article/000422.htm'),
                ('Headache', '/ency/article/003024.htm'),
                ('Hepatitis', '/ency/article/001154.htm'),
                ('Insomnia', '/ency/article/000805.htm'),
                ('Lupus', '/ency/article/000435.htm'),
                ('Menopause', '/ency/article/000894.htm'),
                ('Multiple Sclerosis', '/ency/article/000737.htm'),
                ('Nausea', '/ency/article/003117.htm'),
                ('Osteoarthritis', '/ency/article/000423.htm'),
                ('Parkinson Disease', '/ency/article/000755.htm'),
                ('Psoriasis', '/ency/article/000434.htm'),
                ('Rheumatoid Arthritis', '/ency/article/000431.htm'),
                ('Sciatica', '/ency/article/000686.htm'),
                ('Thyroid Disease', '/ency/article/001159.htm'),
                ('Ulcer', '/ency/article/000206.htm'),
                ('Urinary Tract Infection', '/ency/article/000521.htm'),
                ('Vertigo', '/ency/article/001432.htm'),
                ('Vision Problems', '/ency/article/003029.htm'),
                ('Weight Loss', '/ency/article/003107.htm'),
            ]
            
            for title, path in common_topics:
                full_url = self.base_url + path
                if full_url not in seen_urls:
                    seen_urls.add(full_url)
                    topics.append({
                        'title': title,
                        'url': full_url
                    })
                
                if limit and len(topics) >= limit:
                    break
        
        # Apply limit
        if limit:
            topics = topics[:limit]
        
        print(f"✅ Found {len(topics)} health topics")
        return topics
    
    def scrape_topic(self, topic_url):
        """Scrape individual topic page"""
        try:
            response = requests.get(topic_url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content
            content = {
                'url': topic_url,
                'title': '',
                'summary': '',
                'sections': []
            }
            
            # Get title (try multiple selectors)
            title_selectors = ['h1', 'h1.page-title', 'div.page-title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    content['title'] = title_elem.text.strip()
                    break
            
            # If no title found, try meta title
            if not content['title']:
                meta_title = soup.find('meta', {'property': 'og:title'})
                if meta_title:
                    content['title'] = meta_title.get('content', '')
            
            # Get summary/introduction
            summary_selectors = [
                'div#topic-summary',
                'div.section-body',
                'div.mp-content',
                'div#mplus-content',
                'article'
            ]
            
            for selector in summary_selectors:
                summary_div = soup.select_one(selector)
                if summary_div:
                    paragraphs = summary_div.find_all('p', limit=3)
                    if paragraphs:
                        content['summary'] = ' '.join([p.get_text(strip=True) for p in paragraphs])
                        break
            
            # Get all sections
            section_selectors = [
                'div.section',
                'div.mp-content',
                'section',
                'article section'
            ]
            
            for selector in section_selectors:
                sections = soup.select(selector)
                if sections:
                    for section in sections:
                        # Get heading
                        heading_elem = section.find(['h2', 'h3', 'h4'])
                        
                        # Get content
                        section_text = section.get_text(separator=' ', strip=True)
                        
                        # Only add if has meaningful content
                        if section_text and len(section_text) > 100:
                            content['sections'].append({
                                'heading': heading_elem.text.strip() if heading_elem else 'Content',
                                'content': section_text
                            })
                    
                    if content['sections']:
                        break
            
            # If no sections found, try to get main content
            if not content['sections'] and not content['summary']:
                main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
                if main_content:
                    paragraphs = main_content.find_all('p')
                    if paragraphs:
                        all_text = ' '.join([p.get_text(strip=True) for p in paragraphs])
                        content['summary'] = all_text[:2000]  # First 2000 chars
            
            # Only return if we got some content
            if content['title'] and (content['summary'] or content['sections']):
                return content
            else:
                return None
            
        except Exception as e:
            return None
    
    def scrape_all(self, limit=50):
        """Scrape multiple topics"""
        print("🚀 Starting MedlinePlus scraping...")
        
        topics = self.get_health_topics(limit=limit)
        
        if not topics:
            print("⚠️ No topics found to scrape")
            return 0
        
        successful = 0
        for i, topic in enumerate(tqdm(topics, desc="Scraping topics")):
            try:
                data = self.scrape_topic(topic['url'])
                
                if data and (data['summary'] or data['sections']):
                    # Save to file
                    filename = f"topic_{i:04d}.json"
                    with open(self.output_dir / filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    successful += 1
                
                time.sleep(1.5)  # Be extra respectful to the server
                
            except Exception as e:
                continue
        
        print(f"\n✅ Successfully scraped {successful}/{len(topics)} topics")
        return successful

# Test if run directly
if __name__ == "__main__":
    print("Testing MedlinePlus Scraper...\n")
    
    scraper = MedlinePlusScraper()
    
    # Test with small number first
    print("Testing with 5 topics...\n")
    count = scraper.scrape_all(limit=5)
    
    print(f"\n{'='*60}")
    print(f"✅ Test complete: {count} topics scraped")
    print(f"{'='*60}")
    
    if count > 0:
        print("\n✅ Scraper is working! You can now run:")
        print("   python run_pipeline.py")
    else:
        print("\n⚠️ Scraper needs adjustment. Check your internet connection.")