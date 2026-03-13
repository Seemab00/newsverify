# services/report_generator.py
from typing import Dict, Any, Optional
from datetime import datetime
import json

class ReportGenerator:
    def __init__(self):
        print("✅ Report Generator initialized")
    
    def generate_report(self, 
                        url: str,
                        security_check: Dict[str, Any],
                        content: Dict[str, Any],
                        ai_analysis: Dict[str, Any],
                        source_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete verification report generate karo
        """
        
        # Calculate overall trust score
        overall_score = self._calculate_overall_score(
            security_check.get('safety_score', 100),
            ai_analysis.get('fake_probability', 50),
            source_analysis.get('consistency_score', 0)
        )
        
        # Get final verdict
        final_verdict = self._get_final_verdict(
            overall_score,
            security_check.get('verdict'),
            ai_analysis.get('verdict')
        )
        
        # Generate summary
        summary = self._generate_summary(
            content.get('title', 'No title'),
            final_verdict,
            overall_score
        )
        
        # Create report
        report = {
            "report_id": self._generate_report_id(),
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "domain": content.get('domain', 'unknown'),
            
            "overall_assessment": {
                "trust_score": overall_score,
                "final_verdict": final_verdict,
                "summary": summary,
                "risk_level": self._get_risk_level(overall_score)
            },
            
            "details": {
                "security": {
                    "score": security_check.get('safety_score', 0),
                    "verdict": security_check.get('verdict', 'UNKNOWN'),
                    "threats": security_check.get('threats', {}),
                    "safe": security_check.get('is_safe', False)
                },
                
                "content": {
                    "title": content.get('title'),
                    "authors": content.get('authors', []),
                    "publish_date": content.get('publish_date'),
                    "word_count": content.get('word_count', 0),
                    "has_multimedia": content.get('has_multimedia', False)
                },
                
                "ai_analysis": {
                    "fake_probability": ai_analysis.get('fake_probability', 0),
                    "bias_score": ai_analysis.get('bias_score', 0),
                    "sensationalism": ai_analysis.get('sensationalism_score', 0),
                    "red_flags": ai_analysis.get('red_flags', [])
                },
                
                "source_verification": {
                    "consistency_score": source_analysis.get('consistency_score', 0),
                    "trusted_sources": source_analysis.get('trusted_sources_count', 0),
                    "total_sources": source_analysis.get('total_results', 0),
                    "consensus": source_analysis.get('verdict', 'UNKNOWN')
                }
            },
            
            "recommendations": self._generate_recommendations(overall_score, final_verdict),
            "shareable": self._create_shareable_text(summary, final_verdict, overall_score)
        }
        
        # Add deep check info if available
        if 'fact_check' in source_analysis:
            report['details']['source_verification']['fact_checks'] = source_analysis['fact_check']
        
        if 'source_reputation' in source_analysis:
            report['details']['source_verification']['reputation'] = source_analysis['source_reputation']
        
        return report
    
    def _calculate_overall_score(self, safety_score: int, fake_score: int, consistency_score: int) -> int:
        """Calculate overall trust score (0-100)"""
        # Safety: 30% weight
        # Fake probability: 40% weight (inverted)
        # Consistency: 30% weight
        
        inverted_fake = 100 - fake_score  # Lower fake score is better
        
        overall = (safety_score * 0.3) + (inverted_fake * 0.4) + (consistency_score * 0.3)
        return int(overall)
    
    def _get_final_verdict(self, score: int, security_verdict: str, ai_verdict: str) -> str:
        """Determine final verdict"""
        if security_verdict == "UNSAFE":
            return "UNSAFE"
        
        if score >= 80:
            return "VERIFIED_TRUE"
        elif score >= 60:
            return "LIKELY_TRUE"
        elif score >= 40:
            return "UNCERTAIN"
        elif score >= 20:
            return "LIKELY_FAKE"
        else:
            return "VERIFIED_FAKE"
    
    def _get_risk_level(self, score: int) -> str:
        """Get risk level"""
        if score >= 80:
            return "LOW"
        elif score >= 60:
            return "MEDIUM"
        elif score >= 40:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        import hashlib
        import time
        unique = f"{time.time()}{id(self)}"
        return hashlib.md5(unique.encode()).hexdigest()[:12]
    
    def _generate_summary(self, title: str, verdict: str, score: int) -> str:
        """Generate human-readable summary"""
        verdict_text = {
            "VERIFIED_TRUE": "appears to be authentic",
            "LIKELY_TRUE": "seems trustworthy",
            "UNCERTAIN": "requires more verification",
            "LIKELY_FAKE": "shows signs of misinformation",
            "VERIFIED_FAKE": "is likely fake",
            "UNSAFE": "is unsafe/malicious"
        }
        
        return f"The news '{title[:100]}...' {verdict_text.get(verdict, 'needs verification')} with a trust score of {score}%."
    
    def _generate_recommendations(self, score: int, verdict: str) -> list:
        """Generate recommendations based on verdict"""
        if verdict == "VERIFIED_TRUE":
            return [
                "✅ This news appears trustworthy",
                "📢 You can share with confidence",
                "🔍 Always check original sources"
            ]
        elif verdict == "LIKELY_TRUE":
            return [
                "📊 News seems reliable",
                "📋 Cross-check with official sources",
                "📌 Share with context"
            ]
        elif verdict == "UNCERTAIN":
            return [
                "⚠️ Verify with multiple sources",
                "🔎 Check publication date",
                "📝 Look for official statements"
            ]
        elif verdict in ["LIKELY_FAKE", "VERIFIED_FAKE"]:
            return [
                "❌ Do NOT share this news",
                "🚨 Report to platform if harmful",
                "🔍 Check fact-checking websites"
            ]
        elif verdict == "UNSAFE":
            return [
                "⚠️ Do NOT open this link",
                "🔒 Report as malicious",
                "🗑️ Delete immediately"
            ]
        else:
            return ["📋 Proceed with caution"]
    
    def _create_shareable_text(self, summary: str, verdict: str, score: int) -> str:
        """Create shareable summary text"""
        emoji = {
            "VERIFIED_TRUE": "✅",
            "LIKELY_TRUE": "📊",
            "UNCERTAIN": "⚠️",
            "LIKELY_FAKE": "❌",
            "VERIFIED_FAKE": "🚫",
            "UNSAFE": "🔴"
        }
        
        shareable = f"""
{emoji.get(verdict, '📰')} NewsVerify Report
━━━━━━━━━━━━━━━━━━━
{summary}

📊 Trust Score: {score}%
🏷️ Verdict: {verdict}

➡️ Verify any news at: http://localhost:8000
"""
        return shareable.strip()
    
    def get_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML version for web display"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>NewsVerify Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .container {{ max-width: 800px; margin: auto; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 10px; }}
        .score {{ font-size: 48px; font-weight: bold; text-align: center; }}
        .verdict {{ font-size: 24px; text-align: center; margin: 20px; }}
        .details {{ margin: 20px 0; }}
        .metric {{ background: #f9f9f9; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .recommendations {{ background: #e3f2fd; padding: 20px; border-radius: 10px; }}
        .footer {{ margin-top: 40px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>NewsVerify Report</h1>
            <p>Generated: {report['timestamp']}</p>
            <p>URL: {report['url']}</p>
        </div>
        
        <div class="score">{report['overall_assessment']['trust_score']}%</div>
        <div class="verdict">{report['overall_assessment']['final_verdict']}</div>
        <p class="summary">{report['overall_assessment']['summary']}</p>
        
        <div class="details">
            <h3>Security Check</h3>
            <div class="metric">Safety Score: {report['details']['security']['score']}%</div>
            <div class="metric">Verdict: {report['details']['security']['verdict']}</div>
            
            <h3>AI Analysis</h3>
            <div class="metric">Fake Probability: {report['details']['ai_analysis']['fake_probability']}%</div>
            <div class="metric">Bias Score: {report['details']['ai_analysis']['bias_score']}%</div>
            
            <h3>Source Verification</h3>
            <div class="metric">Consistency: {report['details']['source_verification']['consistency_score']}%</div>
            <div class="metric">Trusted Sources: {report['details']['source_verification']['trusted_sources']}</div>
        </div>
        
        <div class="recommendations">
            <h3>Recommendations</h3>
            <ul>
        """
        
        for rec in report.get('recommendations', []):
            html += f"<li>{rec}</li>"
        
        html += f"""
            </ul>
        </div>
        
        <div class="footer">
            <p>Report ID: {report['report_id']}</p>
        </div>
    </div>
</body>
</html>
"""
        return html

# Test function
async def test():
    print("🔧 Testing Report Generator...")
    generator = ReportGenerator()
    
    # Sample data
    sample_report = generator.generate_report(
        url="https://www.dawn.com/latest-news",
        security_check={
            "safety_score": 100,
            "verdict": "SAFE",
            "is_safe": True,
            "threats": {"malicious": 0, "phishing": 0}
        },
        content={
            "title": "Test News",
            "authors": ["Author 1"],
            "publish_date": "2024-01-01",
            "word_count": 500,
            "domain": "dawn.com",
            "has_multimedia": True
        },
        ai_analysis={
            "fake_probability": 30,
            "bias_score": 40,
            "sensationalism_score": 20,
            "red_flags": []
        },
        source_analysis={
            "consistency_score": 80,
            "trusted_sources_count": 3,
            "total_results": 10,
            "verdict": "STRONG_CONSENSUS"
        }
    )
    
    print("\n" + "="*60)
    print("📊 Report Generated:")
    print(f"Report ID: {sample_report['report_id']}")
    print(f"Trust Score: {sample_report['overall_assessment']['trust_score']}%")
    print(f"Final Verdict: {sample_report['overall_assessment']['final_verdict']}")
    print(f"Risk Level: {sample_report['overall_assessment']['risk_level']}")
    print(f"\nSummary: {sample_report['overall_assessment']['summary']}")
    
    print("\n📋 Recommendations:")
    for rec in sample_report['recommendations']:
        print(f"  {rec}")
    
    print("\n📱 Shareable Text:")
    print(sample_report['shareable'])

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())