import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# 1. Setup
from config import EMBEDDING_MODEL
from tidb_store import TiDBGraph
import sys

def ingest_vectors(file_path: str = None, status_callback=None):
    msg = "Loading PDF for Vectorization..."
    print(msg)
    if status_callback: status_callback(msg)

    # Check for CLI argument or use default if not provided
    if not file_path:
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
        else:
            file_path = "data/strategy_report.pdf"
        
    msg = f"Processing: {file_path}"
    print(msg)
    if status_callback: status_callback(msg)

    if not os.path.exists(file_path):
        msg = f"Error: File {file_path} not found."
        print(msg)
        if status_callback: status_callback(msg)
        return
    
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    # Split documents
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    
    msg = f"Created {len(chunks)} text chunks."
    print(msg)
    if status_callback: status_callback(msg)

    # 2. Initialize Embedding Model (HuggingFace)
    msg = "Initializing HuggingFace Embeddings..."
    print(msg)
    if status_callback: status_callback(msg)
    
    # Downloads model locally (cache)
    embeddings_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # 3. Generate Embeddings Manually
    msg = "Generating embeddings and inserting into TiDB..."
    print(msg)
    if status_callback: status_callback(msg)
    
    graph = TiDBGraph()
    
    texts = [c.page_content for c in chunks]
    embeddings_list = embeddings_model.embed_documents(texts)
    
    for i, chunk in enumerate(chunks):
        try:
            graph.insert_chunk(
                content=chunk.page_content,
                source=chunk.metadata.get("source", "unknown"),
                page=chunk.metadata.get("page", 0),
                embedding=embeddings_list[i]
            )
        except Exception as e:
            print(f"Error inserting chunk {i}: {e}")

    msg = "Vector Indexing Complete!"
    print(msg)
    if status_callback: status_callback(msg)

def search_vectors(query: str):
    """Simple wrapper for vector search using TiDB."""
    try:
        embeddings_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        query_embedding = embeddings_model.embed_query(query)
        
        graph = TiDBGraph()
        results = graph.search_vectors(query_embedding, top_k=5)
        
        return [f"Source: {row['source']} (Page {row['page']})\nContent: {row['content']}" for row in results]
    except Exception as e:
        return [f"Error searching vectors: {e}"]

if __name__ == "__main__":
    ingest_vectors()
