"""
Test script to verify Gemini API key is working
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"🔑 API Key found: {GEMINI_API_KEY[:20]}..." if GEMINI_API_KEY else "❌ No API key found")

try:
    genai.configure(api_key=GEMINI_API_KEY)
    
    # List available models first
    print("\n📋 Available models:")
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            print(f"   - {m.name}")
    
    # Test with gemini-2.0-flash (fast and efficient)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    print("\n🧪 Testing Gemini API with a simple prompt...")
    response = model.generate_content("Say 'Hello from Gemini!' and confirm you're working.")
    
    print("\n✅ SUCCESS! Gemini API is working!")
    print(f"\n📝 Response:\n{response.text}")
    
    # Test paraphrasing capability
    print("\n\n🧪 Testing paraphrasing capability...")
    test_text = "The student submitted their homework on time and it was very well written."
    paraphrase_prompt = f"""Paraphrase the following text while maintaining its meaning. 
Make it sound more professional and academic:

Text: {test_text}

Paraphrased version:"""
    
    response = model.generate_content(paraphrase_prompt)
    print(f"\n✅ Paraphrasing works!")
    print(f"\nOriginal: {test_text}")
    print(f"Paraphrased: {response.text}")
    
    print("\n\n🎉 All tests passed! Gemini API is ready to use.")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\n💡 Possible issues:")
    print("   - Invalid API key")
    print("   - API key not activated")
    print("   - Network connectivity issues")
    print("   - API quota exceeded")
