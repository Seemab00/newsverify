# services/database.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

class DatabaseService:
    def __init__(self):
        # MongoDB connection URL from .env
        self.mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.db_name = os.getenv("DATABASE_NAME", "newsverify")
        
        # Initialize as None
        self.client = None
        self.db = None
        self.verifications = None
        self.users = None
        self.reports = None
        
        try:
            # Connect to MongoDB
            self.client = MongoClient(self.mongodb_url, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            
            self.db = self.client[self.db_name]
            
            # Create collections
            self.verifications = self.db['verifications']
            self.users = self.db['users']
            self.reports = self.db['reports']
            
            # Create indexes
            self.verifications.create_index('url')
            self.verifications.create_index('timestamp')
            self.verifications.create_index('report_id')
            
            print(f"✅ MongoDB Connected: {self.db_name}")
            print(f"   Collections: verifications, users, reports")
            
        except ConnectionFailure as e:
            print(f"❌ MongoDB Connection Failed: {e}")
            print("   Continuing without database...")
            self.client = None
            self.db = None
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.client is not None and self.db is not None
    
    def save_verification(self, report: Dict[str, Any]) -> Optional[str]:
        """Save verification report to database"""
        try:
            if not self.is_connected():
                print("⚠️ Database not connected - skipping save")
                return None
            
            # Add metadata
            report['_id'] = report.get('report_id')
            report['saved_at'] = datetime.now().isoformat()
            
            # Insert into database
            result = self.verifications.insert_one(report)
            print(f"✅ Verification saved: {report['report_id']}")
            return report['report_id']
            
        except DuplicateKeyError:
            print(f"⚠️ Report already exists: {report.get('report_id')}")
            return report.get('report_id')
        except Exception as e:
            print(f"❌ Error saving verification: {e}")
            return None
    
    def get_verification(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get verification by report ID"""
        try:
            if not self.is_connected():
                return None
            
            result = self.verifications.find_one({"_id": report_id})
            if result:
                # Remove MongoDB _id from response
                result.pop('_id', None)
            return result
        except Exception as e:
            print(f"❌ Error getting verification: {e}")
            return None
    
    def get_verifications_by_url(self, url: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all verifications for a URL"""
        try:
            if not self.is_connected():
                return []
            
            results = self.verifications.find(
                {"url": url}
            ).sort("timestamp", -1).limit(limit)
            
            verifications = []
            for result in results:
                result.pop('_id', None)
                verifications.append(result)
            
            return verifications
        except Exception as e:
            print(f"❌ Error getting verifications: {e}")
            return []
    
    def get_recent_verifications(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get most recent verifications"""
        try:
            if not self.is_connected():
                return []
            
            results = self.verifications.find().sort("timestamp", -1).limit(limit)
            
            verifications = []
            for result in results:
                result.pop('_id', None)
                # Return only summary info
                verifications.append({
                    "report_id": result.get('report_id'),
                    "url": result.get('url'),
                    "domain": result.get('domain'),
                    "timestamp": result.get('timestamp'),
                    "trust_score": result.get('overall_assessment', {}).get('trust_score'),
                    "final_verdict": result.get('overall_assessment', {}).get('final_verdict'),
                    "title": result.get('details', {}).get('content', {}).get('title', 'N/A')[:50]
                })
            
            return verifications
        except Exception as e:
            print(f"❌ Error getting recent verifications: {e}")
            return []
    
    def delete_verification(self, report_id: str) -> bool:
        """Delete a verification by report ID"""
        try:
            if not self.is_connected():
                return False
            
            result = self.verifications.delete_one({"_id": report_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"❌ Error deleting verification: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            if not self.is_connected():
                return {"error": "Database not connected"}
            
            total = self.verifications.count_documents({})
            today = datetime.now().strftime("%Y-%m-%d")
            today_count = self.verifications.count_documents({
                "timestamp": {"$regex": f"^{today}"}
            })
            
            # Get verdict distribution
            pipeline = [
                {"$group": {
                    "_id": "$overall_assessment.final_verdict",
                    "count": {"$sum": 1}
                }}
            ]
            verdict_stats = list(self.verifications.aggregate(pipeline))
            
            verdicts = {}
            for stat in verdict_stats:
                verdicts[stat['_id']] = stat['count']
            
            return {
                "total_verifications": total,
                "today_verifications": today_count,
                "verdict_distribution": verdicts,
                "collections": ["verifications", "users", "reports"],
                "database": self.db_name,
                "connected": True
            }
        except Exception as e:
            return {"error": str(e), "connected": False}
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("🔒 MongoDB connection closed")

# Test function
def test():
    print("🔧 Testing Database Service...")
    db = DatabaseService()
    
    if not db.is_connected():
        print("❌ Database not connected - check MongoDB is running")
        return
    
    # Test save
    test_report = {
        "report_id": "test123",
        "url": "https://test.com",
        "timestamp": datetime.now().isoformat(),
        "domain": "test.com",
        "overall_assessment": {
            "trust_score": 85,
            "final_verdict": "VERIFIED_TRUE"
        },
        "details": {
            "content": {
                "title": "Test News Article"
            }
        }
    }
    
    # Save
    report_id = db.save_verification(test_report)
    print(f"✅ Saved: {report_id}")
    
    # Get
    retrieved = db.get_verification("test123")
    print(f"✅ Retrieved: {retrieved['url'] if retrieved else 'None'}")
    
    # Get recent
    recent = db.get_recent_verifications(5)
    print(f"✅ Recent: {len(recent)} verifications")
    
    # Stats
    stats = db.get_stats()
    print(f"✅ Stats: {stats}")
    
    # Clean up
    db.delete_verification("test123")
    print("✅ Test cleanup complete")
    
    db.close()

if __name__ == "__main__":
    test()