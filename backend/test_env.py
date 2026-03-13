# test_env.py
import os
from dotenv import load_dotenv

# .env file load karo
load_dotenv()

print("🔍 Checking Environment Variables...")
print("=" * 40)

# Sabhi keys check karo
keys = [
    "GROQ_API_KEY",
    "GOOGLE_AI_STUDIO_KEY", 
    "VIRUSTOTAL_API_KEY",
    "NEWSAPI_KEY",
    "MONGODB_URL",
    "DATABASE_NAME",
    "REDIS_URL",
    "DEBUG"
]

for key in keys:
    value = os.getenv(key)
    if value:
        # Key mil gayi
        if "KEY" in key:
            # API keys ko partially hide karo
            visible_part = value[:10] + "..." + value[-5:] if len(value) > 15 else "***"
            print(f"✅ {key}: {visible_part}")
        else:
            print(f"✅ {key}: {value}")
    else:
        print(f"❌ {key}: NOT FOUND")

print("=" * 40)

# Special check for Groq API
groq_key = os.getenv("GROQ_API_KEY")
if groq_key and groq_key.startswith("gsk_"):
    print("\n✅ Groq API key format is correct!")

# Google AI Studio key check
google_key = os.getenv("GOOGLE_AI_STUDIO_KEY") 
if google_key and google_key.startswith("AIza"):
    print("✅ Google AI Studio key format is correct!")

print("\n🎯 Environment check complete!")