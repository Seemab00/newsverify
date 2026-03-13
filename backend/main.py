# main.py - Complete NewsVerify API with all 7 steps
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

# Import all services
from services.security_checker import SecurityChecker
from services.content_extractor import ContentExtractor
from services.ai_verifier import NewsVerifier
from services.source_verifier import SourceVerifier
from services.report_generator import ReportGenerator

# FastAPI app initialize
app = FastAPI(
    title="NewsVerify API",
    description="AI-Powered News Verification System",
    version="1.0.0"
)

# Initialize all services
security_checker = SecurityChecker()
content_extractor = ContentExtractor()
ai_verifier = NewsVerifier()
source_verifier = SourceVerifier()
report_generator = ReportGenerator()

# Request/Response Models
class NewsRequest(BaseModel):
    url: str
    check_deep: Optional[bool] = False

class NewsResponse(BaseModel):
    url: str
    status: str
    message: str
    security_check: Optional[Dict[str, Any]] = None
    content: Optional[Dict[str, Any]] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    source_analysis: Optional[Dict[str, Any]] = None
    report: Optional[Dict[str, Any]] = None
    fake_score: Optional[int] = None
    verdict: Optional[str] = None

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "NewsVerify API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "health": "/health",
            "verify": "/api/verify",
            "docs": "/docs",
            "report": "/api/report/{report_id}"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "services": {
            "security_checker": "ready",
            "content_extractor": "ready",
            "ai_verifier": "ready",
            "source_verifier": "ready",
            "report_generator": "ready"
        }
    }

# Verify news endpoint - Complete with all steps
@app.post("/api/verify", response_model=NewsResponse)
async def verify_news(request: NewsRequest):
    """
    Complete news verification in 5 steps:
    1. Security Check (VirusTotal)
    2. Content Extraction (Newspaper3k)
    3. AI Analysis (Groq)
    4. Source Verification (NewsAPI)
    5. Report Generation
    """
    try:
        print(f"\n🔍 Processing URL: {request.url}")
        print("="*50)
        
        # STEP 1: Security Check
        print("📌 Step 1/5: Security Check...")
        security_result = await security_checker.check_url_safety(request.url)
        
        if security_result.get("verdict") == "UNSAFE":
            print("⚠️ URL is UNSAFE - Stopping verification")
            return NewsResponse(
                url=request.url,
                status="blocked",
                message="⚠️ This URL appears to be unsafe!",
                security_check=security_result
            )
        print(f"✅ Security Check Complete - Verdict: {security_result.get('verdict')}")
        
        # STEP 2: Content Extraction
        print("📌 Step 2/5: Extracting Content...")
        content_result = await content_extractor.extract_news_content(request.url)
        print(f"✅ Content Extracted - Title: {content_result.get('title', 'N/A')[:50]}...")
        
        # STEP 3: AI Analysis
        print("📌 Step 3/5: AI Analysis with Groq...")
        ai_result = await ai_verifier.verify_news(
            title=content_result.get('title', ''),
            content=content_result.get('main_text', '')
        )
        print(f"✅ AI Analysis Complete - Verdict: {ai_result.get('verdict')}")
        
        # STEP 4: Source Verification
        print("📌 Step 4/5: Source Verification...")
        source_result = await source_verifier.search_similar_news(
            title=content_result.get('title', ''),
            keywords=content_result.get('keywords', [])
        )
        print(f"✅ Source Verification Complete - Consensus: {source_result.get('verdict')}")
        
        # Deep check mein extra info
        if request.check_deep:
            print("📌 Deep Check Enabled - Adding extra analysis...")
            domain = content_result.get('domain', '')
            reputation = await source_verifier.verify_source_reputation(domain)
            source_result['source_reputation'] = reputation
        
        # STEP 5: Generate Report
        print("📌 Step 5/5: Generating Final Report...")
        final_report = report_generator.generate_report(
            url=request.url,
            security_check=security_result,
            content=content_result,
            ai_analysis=ai_result,
            source_analysis=source_result
        )
        print("✅ Report Generated Successfully!")
        print("="*50)
        print(f"🎯 Final Verdict: {final_report['overall_assessment']['final_verdict']}")
        print(f"📊 Trust Score: {final_report['overall_assessment']['trust_score']}%")
        print("="*50)
        
        return NewsResponse(
            url=request.url,
            status="completed",
            message="Verification complete",
            security_check=security_result,
            content=content_result,
            ai_analysis=ai_result,
            source_analysis=source_result,
            report=final_report,
            fake_score=ai_result.get('fake_probability'),
            verdict=final_report['overall_assessment']['final_verdict']
        )
    
    except Exception as e:
        print(f"❌ Error in verification: {str(e)}")
        return NewsResponse(
            url=request.url,
            status="error",
            message=f"Error: {str(e)}"
        )

# Get HTML report endpoint
@app.get("/api/report/{report_id}")
async def get_html_report(report_id: str):
    """
    Get HTML version of a report
    (In production, fetch from database)
    """
    return {
        "message": "HTML report endpoint",
        "report_id": report_id,
        "note": "Database integration coming in Step 8"
    }

# Get shareable text endpoint
@app.post("/api/share")
async def get_shareable_text(report: Dict[str, Any]):
    """
    Get shareable text version of report
    """
    try:
        shareable = report_generator._create_shareable_text(
            report.get('overall_assessment', {}).get('summary', ''),
            report.get('overall_assessment', {}).get('final_verdict', ''),
            report.get('overall_assessment', {}).get('trust_score', 0)
        )
        return {"shareable": shareable}
    except Exception as e:
        return {"error": str(e)}

# Shutdown event - clean up resources
@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Shutting down services...")
    security_checker.close()
    print("✅ All services closed")

# Agar file directly run ho to server start karo
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)