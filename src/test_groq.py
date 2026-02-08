
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def test_groq():
    print("Testing Groq Integration...")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment.")
        return

    try:
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
        print("✅ ChatGroq initialized.")
        
        print("Sending test message...")
        response = llm.invoke("Hello, are you working?")
        print(f"✅ Response received: {response.content}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_groq()
