# services/ai_verifier.py
import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class NewsVerifier:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        
        # Direct initialization - no proxies parameter
        from groq import Groq
        self.client = Groq(api_key=self.api_key)
        print(f"✅ Groq API client initialized")
    
    async def verify_news(self, title: str, content: str) -> Dict[str, Any]:
        try:
            print(f"🤖 Analyzing news with Groq AI...")
            
            prompt = f"""
            You are a professional fact-checker and news analyst. Analyze this news article:

            TITLE: {title}
            
            CONTENT: {content[:2000]}
            
            Provide a JSON response with:
            1. fake_probability: 0-100 score
            2. bias_score: 0-100 score
            3. sensationalism_score: 0-100 score
            4. emotional_language: list of emotional phrases found
            5. facts_analysis: brief analysis of facts presented
            6. red_flags: list of suspicious elements
            7. verdict: "TRUE", "MISLEADING", "FAKE", or "UNVERIFIABLE"
            8. confidence: 0-100 score in your analysis
            
            Return ONLY valid JSON, no other text.
            """
            
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",  # Using Llama 3 instead of Mixtral
                messages=[
                    {"role": "system", "content": "You are a fact-checking expert. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1024,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result["model_used"] = "llama3-70b-8192"
            
            print(f"✅ Analysis complete. Verdict: {result.get('verdict', 'Unknown')}")
            return result
            
        except Exception as e:
            print(f"❌ Error in AI analysis: {e}")
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
                model="llama3-8b-8192",
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