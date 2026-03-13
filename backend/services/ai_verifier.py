# services/ai_verifier.py
import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from groq import Groq

# .env file load karo
load_dotenv()

class NewsVerifier:
    def __init__(self):
        # Groq API key load karo
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        
        # Groq client initialize karo
        self.client = Groq(api_key=self.api_key)
        print(f"✅ Groq API client initialized")
    
    async def verify_news(self, title: str, content: str) -> Dict[str, Any]:
        """
        News article ko analyze karo using Groq API
        """
        try:
            print(f"🤖 Analyzing news with Groq AI...")
            
            # Prompt design for news analysis
            prompt = f"""
            You are a professional fact-checker and news analyst. Analyze this news article:

            TITLE: {title}
            
            CONTENT: {content[:2000]}  # Limit content to 2000 chars
            
            Provide a JSON response with:
            1. fake_probability: 0-100 score (0=completely true, 100=completely fake)
            2. bias_score: 0-100 score (0=neutral, 100=highly biased)
            3. sensationalism_score: 0-100 score
            4. emotional_language: list of emotional phrases found
            5. facts_analysis: brief analysis of facts presented
            6. red_flags: list of suspicious elements
            7. verdict: "TRUE", "MISLEADING", "FAKE", or "UNVERIFIABLE"
            8. confidence: 0-100 score in your analysis
            
            Return ONLY valid JSON, no other text.
            """
            
            # Groq API call
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",  # Using Mixtral for complex analysis
                messages=[
                    {"role": "system", "content": "You are a fact-checking expert. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=1024,
                response_format={"type": "json_object"}  # Ensure JSON response
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            # Add metadata
            result["model_used"] = "mixtral-8x7b-32768"
            result["analysis_time"] = str(response.usage.total_time) if hasattr(response, 'usage') else "unknown"
            
            print(f"✅ Analysis complete. Verdict: {result.get('verdict', 'Unknown')}")
            return result
            
        except Exception as e:
            print(f"❌ Error in AI analysis: {e}")
            
            # Fallback response
            return {
                "fake_probability": 50,
                "bias_score": 50,
                "sensationalism_score": 50,
                "emotional_language": [],
                "facts_analysis": "Analysis failed due to technical error",
                "red_flags": ["Analysis incomplete"],
                "verdict": "UNVERIFIABLE",
                "confidence": 0,
                "error": str(e)
            }
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of the news text
        """
        try:
            prompt = f"""
            Analyze the sentiment of this news text:
            
            {text[:1000]}
            
            Return JSON with:
            - sentiment: "positive", "negative", or "neutral"
            - emotion: "anger", "fear", "joy", "sadness", "surprise", or "neutral"
            - intensity: 0-100
            - manipulative: true/false
            """
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",  # Using Llama for faster sentiment analysis
                messages=[
                    {"role": "system", "content": "Analyze sentiment and return JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"❌ Sentiment analysis error: {e}")
            return {
                "sentiment": "neutral",
                "emotion": "neutral",
                "intensity": 0,
                "manipulative": False
            }

# Test function
async def test():
    print("🔧 Testing AI News Verifier...")
    verifier = NewsVerifier()
    
    # Test news
    test_cases = [
        {
            "title": "Scientists Discover Cure for All Cancers",
            "content": "A team of researchers has found a miracle drug that cures all types of cancer. Clinical trials show 100% success rate. Big Pharma is trying to suppress this breakthrough."
        },
        {
            "title": "Local School Wins Science Competition",
            "content": "Students from City High School won first prize in the regional science fair with their project on renewable energy. The team will now compete at the national level."
        }
    ]
    
    for case in test_cases:
        print("\n" + "="*60)
        print(f"📌 Title: {case['title']}")
        
        result = await verifier.verify_news(case['title'], case['content'])
        
        print(f"\n🎯 Verdict: {result.get('verdict')}")
        print(f"📊 Fake Probability: {result.get('fake_probability')}%")
        print(f"📊 Bias Score: {result.get('bias_score')}%")
        print(f"⚠️ Red Flags: {result.get('red_flags', [])}")
        print(f"📝 Analysis: {result.get('facts_analysis', '')[:100]}...")
        
        # Sentiment analysis
        sentiment = await verifier.analyze_sentiment(case['content'])
        print(f"\n😊 Sentiment: {sentiment.get('sentiment')} ({sentiment.get('emotion')})")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())