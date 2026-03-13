# services/security_checker.py
import vt
import os
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv

# .env file load karo
load_dotenv()

class SecurityChecker:
    def __init__(self):
        # VirusTotal API key load karo
        self.vt_api_key = os.getenv("VIRUSTOTAL_API_KEY")
        if not self.vt_api_key:
            raise ValueError("VIRUSTOTAL_API_KEY not found in .env file")
        
        print(f"✅ VirusTotal API key loaded: {self.vt_api_key[:10]}...")
        
        # VirusTotal client initialize karo
        self.vt_client = vt.Client(self.vt_api_key)
    
    async def check_url_safety(self, url: str) -> Dict[str, Any]:
        """
        URL ko scan karo aur safety report do
        """
        try:
            print(f"🔍 Scanning URL: {url}")
            
            # URL ko VirusTotal ke format mein convert karo
            url_id = vt.url_id(url)
            
            # URL report lo
            url_report = await self.vt_client.get_object_async(f"/urls/{url_id}")
            
            # Analysis results
            stats = url_report.last_analysis_stats
            
            # Safety score calculate karo (0-100)
            total_scans = sum(stats.values())
            safe_scans = stats.get('harmless', 0) + stats.get('undetected', 0)
            safety_score = int((safe_scans / total_scans) * 100) if total_scans > 0 else 50
            
            # Detailed results
            result = {
                "url": url,
                "is_safe": stats.get('malicious', 0) == 0 and stats.get('phishing', 0) == 0,
                "safety_score": safety_score,
                "threats": {
                    "malicious": stats.get('malicious', 0),
                    "phishing": stats.get('phishing', 0),
                    "suspicious": stats.get('suspicious', 0),
                    "harmless": stats.get('harmless', 0),
                    "undetected": stats.get('undetected', 0)
                },
                "total_scans": total_scans,
                "verdict": "SAFE" if (stats.get('malicious', 0) == 0 and stats.get('phishing', 0) == 0) else "UNSAFE"
            }
            
            print(f"✅ Scan complete. Verdict: {result['verdict']}")
            return result
            
        except Exception as e:
            print(f"❌ Error scanning URL: {e}")
            return {
                "url": url,
                "is_safe": None,
                "safety_score": 0,
                "error": str(e),
                "verdict": "UNKNOWN",
                "threats": {}
            }
    
    def close(self):
        """VirusTotal client close karo"""
        if self.vt_client:
            self.vt_client.close()
            print("🔒 VirusTotal client closed")

# Test function
async def test():
    print("🔧 Testing Security Checker...")
    checker = SecurityChecker()
    
    # Test URLs
    test_urls = [
        "https://www.google.com",
        "https://www.youtube.com",
    ]
    
    for url in test_urls:
        result = await checker.check_url_safety(url)
        print("\n" + "="*50)
        print(f"URL: {result['url']}")
        print(f"Verdict: {result['verdict']}")
        print(f"Safety Score: {result['safety_score']}%")
        if 'threats' in result:
            print(f"Malicious: {result['threats']['malicious']}")
            print(f"Phishing: {result['threats']['phishing']}")
    
    checker.close()

if __name__ == "__main__":
    asyncio.run(test())