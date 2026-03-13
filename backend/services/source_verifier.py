# services/source_verifier.py
import os
import aiohttp
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json

load_dotenv()

class SourceVerifier:
    def __init__(self):
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        if not self.newsapi_key:
            raise ValueError("NEWSAPI_KEY not found in .env file")
        
        print(f"✅ NewsAPI key loaded")
        
        # Trusted news sources
        self.trusted_sources = [
            "bbc.com", "bbc.co.uk",
            "cnn.com",
            "reuters.com",
            "apnews.com",
            "nytimes.com",
            "wsj.com",
            "theguardian.com",
            "dawn.com",  # Pakistan
            "geo.tv",    # Pakistan
            "arynews.tv", # Pakistan
            "timesofindia.indiatimes.com", # India
            "aljazeera.com",
            "dw.com"
        ]
    
    async def search_similar_news(self, title: str, keywords: List[str]) -> Dict[str, Any]:
        """
        Search for similar news from other sources
        """
        try:
            print(f"🔍 Searching similar news for: {title[:50]}...")
            
            # Extract main keywords for search
            search_terms = keywords[:3] if keywords else title.split()[:5]
            search_query = " ".join(search_terms)
            
            # NewsAPI call
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": search_query,
                "apiKey": self.newsapi_key,
                "pageSize": 10,
                "sortBy": "relevancy",
                "language": "en",
                "from": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")  # Last 7 days
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Process results
                        articles = data.get("articles", [])
                        
                        # Separate trusted and other sources
                        trusted_articles = []
                        other_articles = []
                        
                        for article in articles:
                            source_domain = self._extract_domain(article.get("url", ""))
                            article_info = {
                                "title": article.get("title"),
                                "source": article.get("source", {}).get("name"),
                                "domain": source_domain,
                                "url": article.get("url"),
                                "published_at": article.get("publishedAt"),
                                "description": article.get("description")
                            }
                            
                            if any(source in source_domain for source in self.trusted_sources):
                                trusted_articles.append(article_info)
                            else:
                                other_articles.append(article_info)
                        
                        # Calculate consistency score
                        total_articles = len(trusted_articles) + len(other_articles)
                        consistency_score = min(len(trusted_articles) * 20, 100) if total_articles > 0 else 0
                        
                        result = {
                            "query": search_query,
                            "total_results": data.get("totalResults", 0),
                            "trusted_sources_count": len(trusted_articles),
                            "other_sources_count": len(other_articles),
                            "consistency_score": consistency_score,
                            "trusted_articles": trusted_articles[:5],  # Top 5 trusted
                            "other_articles": other_articles[:5],  # Top 5 others
                            "verdict": self._get_consensus_verdict(consistency_score, len(trusted_articles))
                        }
                        
                        print(f"✅ Found {len(trusted_articles)} trusted sources")
                        return result
                    else:
                        return {
                            "error": f"NewsAPI error: {response.status}",
                            "consistency_score": 0,
                            "verdict": "UNKNOWN"
                        }
                        
        except Exception as e:
            print(f"❌ Error searching news: {e}")
            return {
                "error": str(e),
                "consistency_score": 0,
                "verdict": "UNKNOWN"
            }
    
    async def verify_with_fact_check_apis(self, title: str, content: str) -> Dict[str, Any]:
        """
        Check with fact-checking APIs (Google Fact Check Tools)
        """
        try:
            # Google Fact Check API (free tier)
            url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            params = {
                "query": title,
                "key": os.getenv("GOOGLE_AI_STUDIO_KEY"),  # Same key use kar sakte ho
                "languageCode": "en",
                "maxAgeDays": 30
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        claims = data.get("claims", [])
                        
                        fact_checks = []
                        for claim in claims[:5]:
                            fact_checks.append({
                                "text": claim.get("text"),
                                "claimant": claim.get("claimant"),
                                "claim_date": claim.get("claimDate"),
                                "rating": claim.get("claimReview", [{}])[0].get("textualRating"),
                                "publisher": claim.get("claimReview", [{}])[0].get("publisher", {}).get("name")
                            })
                        
                        return {
                            "has_fact_checks": len(fact_checks) > 0,
                            "fact_checks": fact_checks,
                            "total_found": len(claims)
                        }
                    else:
                        return {"has_fact_checks": False, "error": f"API error: {response.status}"}
                        
        except Exception as e:
            return {"has_fact_checks": False, "error": str(e)}
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        try:
            domain = urlparse(url).netloc
            return domain.replace('www.', '')
        except:
            return "unknown"
    
    def _get_consensus_verdict(self, score: int, trusted_count: int) -> str:
        """Get verdict based on consensus score"""
        if trusted_count >= 3 and score >= 80:
            return "STRONG_CONSENSUS"
        elif trusted_count >= 2 and score >= 60:
            return "MODERATE_CONSENSUS"
        elif trusted_count >= 1 and score >= 40:
            return "WEAK_CONSENSUS"
        elif trusted_count == 0 and score == 0:
            return "NO_OTHER_SOURCES"
        else:
            return "CONFLICTING_REPORTS"
    
    async def verify_source_reputation(self, domain: str) -> Dict[str, Any]:
        """Check source reputation"""
        # Simple reputation check based on trusted sources list
        is_trusted = any(source in domain for source in self.trusted_sources)
        
        # Domain age and reputation (simplified)
        return {
            "domain": domain,
            "is_trusted": is_trusted,
            "reputation_score": 90 if is_trusted else 50,
            "category": "Trusted News" if is_trusted else "Unknown Source"
        }

# Test function
async def test():
    print("🔧 Testing Source Verifier...")
    verifier = SourceVerifier()
    
    # Test news
    test_cases = [
        {
            "title": "US Election Results 2024",
            "keywords": ["US", "Election", "2024", "results"]
        },
        {
            "title": "Pakistan vs India Cricket Match",
            "keywords": ["Pakistan", "India", "cricket", "match"]
        }
    ]
    
    for case in test_cases:
        print("\n" + "="*60)
        print(f"📌 Title: {case['title']}")
        
        # Search similar news
        result = await verifier.search_similar_news(case['title'], case['keywords'])
        
        print(f"\n🎯 Consensus: {result.get('verdict')}")
        print(f"📊 Consistency Score: {result.get('consistency_score')}%")
        print(f"📰 Trusted Sources: {result.get('trusted_sources_count')}")
        print(f"📰 Other Sources: {result.get('other_sources_count')}")
        
        if result.get('trusted_articles'):
            print("\n📰 Trusted Sources Found:")
            for article in result['trusted_articles'][:3]:
                print(f"  - {article['source']}")

if __name__ == "__main__":
    asyncio.run(test())