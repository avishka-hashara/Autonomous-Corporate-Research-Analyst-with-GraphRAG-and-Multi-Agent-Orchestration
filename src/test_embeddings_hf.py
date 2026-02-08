
import os
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import time

load_dotenv()

def test_embeddings():
    print("Testing HuggingFace Embeddings...")
    model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    print(f"Model: {model_name}")

    try:
        start = time.time()
        print("Loading model (this may take a while to download first time)...")
        embeddings = HuggingFaceEmbeddings(model_name=model_name)
        print(f"✅ HuggingFace initialized in {time.time() - start:.2f}s")
        
        text = "This is a test sentence for embeddings."
        vec = embeddings.embed_query(text)
        print(f"✅ Embedding generated. Vector length: {len(vec)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_embeddings()
