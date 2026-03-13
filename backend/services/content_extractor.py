# services/content_extractor.py
from newspaper import Article
from bs4 import BeautifulSoup
import requests
import os
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import json

class ContentExtractor:
    def __init__(self):
        print("✅ Content Extractor initialized")
    
    async def extract_news_content(self, url: str) -> Dict[str, Any]:
        """
        News article se content extract karo
        """
        try:
            print(f"📰 Extracting content from: {url}")
            
            # Newspaper3k article object banao
            article = Article(url)
            
            # Article download karo
            article.download()
            
            # Article parse karo
            article.parse()
            
            # NLP perform karo (summary ke liye)
            article.nlp()
            
            # Extracted data
            content = {
                "url": url,
                "title": article.title or "No title found",
                "authors": article.authors or ["Unknown"],
                "publish_date": article.publish_date.isoformat() if article.publish_date else None,
                "main_text": article.text[:5000] + "..." if len(article.text) > 5000 else article.text,  # Limit text
                "summary": article.summary,
                "keywords": article.keywords[:10],  # Top 10 keywords
                "top_image": article.top_image,
                "images": list(article.images)[:5],  # First 5 images
                "videos": article.movies,
                "word_count": len(article.text.split()),
                "meta_description": article.meta_description,
                "meta_keywords": article.meta_keywords,
                "meta_lang": article.meta_lang,
                
                # Additional metadata
                "domain": self._extract_domain(url),
                "has_multimedia": len(article.images) > 0 or len(article.movies) > 0,
                "extraction_time": datetime.now().isoformat()
            }
            
            # Text length check
            if len(article.text) < 100:
                content["warning"] = "⚠️ Very short article - might not be a news article"
            
            print(f"✅ Content extracted: {content['title'][:50]}...")
            print(f"📊 Word count: {content['word_count']}")
            
            return content
            
        except Exception as e:
            print(f"❌ Error extracting content: {e}")
            
            # Fallback: Try with BeautifulSoup
            return await self._fallback_extraction(url, str(e))
    
    async def _fallback_extraction(self, url: str, error: str) -> Dict[str, Any]:
        """
        Agar newspaper3k fail ho jaye to simple HTML parsing try karo
        """
        try:
            print("🔄 Trying fallback extraction with BeautifulSoup...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Simple title extraction
            title = soup.find('title')
            title_text = title.text if title else "No title found"
            
            # Simple text extraction
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text() for p in paragraphs[:20]])
            
            return {
                "url": url,
                "title": title_text,
                "authors": ["Unknown"],
                "publish_date": None,
                "main_text": text[:2000] + "..." if len(text) > 2000 else text,
                "summary": "Summary not available",
                "keywords": [],
                "word_count": len(text.split()),
                "domain": self._extract_domain(url),
                "error": f"Newspaper3k error: {error}",
                "fallback": True,
                "extraction_time": datetime.now().isoformat()
            }
            
        except Exception as e2:
            return {
                "url": url,
                "title": "Extraction failed",
                "error": f"Primary: {error}, Fallback: {str(e2)}",
                "extraction_time": datetime.now().isoformat()
            }
    
    def _extract_domain(self, url: str) -> str:
        """URL se domain name extract karo"""
        from urllib.parse import urlparse
        try:
            domain = urlparse(url).netloc
            return domain.replace('www.', '')
        except:
            return "unknown"
    
    async def extract_multiple(self, urls: list) -> list:
        """Ek saath multiple URLs se content extract karo"""
        tasks = [self.extract_news_content(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

# Test function mein yeh working URLs use karo
async def test():
    print("🔧 Testing Content Extractor...")
    extractor = ContentExtractor()
    
    # Working news URLs
    test_urls = [
        "https://timesofindia.indiatimes.com/world/us/us-news/live-updates",
        "https://www.dawn.com/latest-news",
        "https://www.bbc.com/news"
    ]
    
    for url in test_urls:
        print("\n" + "="*60)
        result = await extractor.extract_news_content(url)
        
        print(f"\n📌 TITLE: {result.get('title', 'N/A')}")
        print(f"✍️ AUTHORS: {result.get('authors', [])}")
        print(f"📅 DATE: {result.get('publish_date', 'Unknown')}")
        print(f"📊 WORD COUNT: {result.get('word_count', 0)}")
        print(f"🏷️ KEYWORDS: {result.get('keywords', [])[:5]}")
        if 'summary' in result:
            print(f"\n📝 SUMMARY: {result.get('summary', 'N/A')[:200]}...")

if __name__ == "__main__":
    asyncio.run(test())