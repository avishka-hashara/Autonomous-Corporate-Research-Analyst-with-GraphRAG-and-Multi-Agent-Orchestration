
import os
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from dotenv import load_dotenv
import time

load_dotenv()

def test_embeddings():
    print("Testing FastEmbed Embeddings...")
    model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    print(f"Model: {model_name}")

    try:
        start = time.time()
        embeddings = FastEmbedEmbeddings(model_name=model_name)
        print(f"✅ FastEmbed initialized in {time.time() - start:.2f}s")
        
        text = "This is a test sentence for embeddings."
        vec = embeddings.embed_query(text)
        print(f"✅ Embedding generated. Vector length: {len(vec)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_embeddings()
