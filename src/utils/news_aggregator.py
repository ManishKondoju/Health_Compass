import feedparser
from datetime import datetime

class HealthNewsAggregator:
    """Fetch health news from trusted sources"""
    
    def __init__(self):
        self.sources = {
            "CDC": "https://tools.cdc.gov/api/v2/resources/media/132608.rss",
            "WHO": "https://www.who.int/rss-feeds/news-english.xml",
            "NIH": "https://www.nih.gov/news-events/news-releases/rss.xml"
        }
    
    def get_news(self, source="CDC", limit=5):
        """Fetch news from specified source"""
        try:
            feed_url = self.sources.get(source, self.sources["CDC"])
            feed = feedparser.parse(feed_url)
            
            news = []
            for entry in feed.entries[:limit]:
                news.append({
                    "title": entry.get('title', 'No title'),
                    "summary": entry.get('summary', entry.get('description', 'No summary'))[:300] + "...",
                    "link": entry.get('link', '#'),
                    "date": entry.get('published', 'Date unknown')
                })
            
            return news
        except Exception as e:
            return []
    
    def get_all_news(self, limit=3):
        """Get news from all sources"""
        all_news = {}
        for source in self.sources.keys():
            all_news[source] = self.get_news(source, limit)
        return all_news