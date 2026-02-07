import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Neo4jVector
from dotenv import load_dotenv

# 1. Setup
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, EMBEDDING_MODEL, OLLAMA_BASE_URL

from neo4j import GraphDatabase

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

    # 2. Initialize Embedding Model (Nomic)
    msg = "Initializing Ollama Embeddings..."
    print(msg)
    if status_callback: status_callback(msg)
    
    embeddings_model = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL
    )

    # 3. Generate Embeddings Manually
    msg = "Generating embeddings... (This may take a while)"
    print(msg)
    if status_callback: status_callback(msg)
    
    texts = [c.page_content for c in chunks]
    embeddings_list = embeddings_model.embed_documents(texts)
    
    # Prepare data for insertion
    data_to_insert = []
    for i, chunk in enumerate(chunks):
        data_to_insert.append({
            "text": chunk.page_content,
            "embedding": embeddings_list[i],
            "source": chunk.metadata.get("source", "unknown"),
            "page": chunk.metadata.get("page", 0)
        })

    # 4. Insert into Neo4j using compatible Cypher
    msg = "Connecting to Neo4j..."
    print(msg)
    if status_callback: status_callback(msg)
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    insert_query = """
    UNWIND $data AS row
    CALL {
        WITH row
        CREATE (c:Chunk {
            text: row.text, 
            source: row.source, 
            page: row.page
        })
        WITH c, row
        CALL db.create.setNodeVectorProperty(c, 'embedding', row.embedding)
    } IN TRANSACTIONS OF 100 ROWS
    """
    
    # Create Vector Index (if not exists)
    index_query = """
    CREATE VECTOR INDEX strategy_vector_index IF NOT EXISTS
    FOR (c:Chunk) ON (c.embedding)
    OPTIONS {indexConfig: {
      `vector.dimensions`: 768,
      `vector.similarity_function`: 'cosine'
    }}
    """
    
    try:
        with driver.session() as session:
            # Clear existing chunks? Optional.
            # print("Clearing old Chunks...")
            # session.run("MATCH (c:Chunk) DETACH DELETE c")

            msg = "Creating Vector Index..."
            print(msg)
            if status_callback: status_callback(msg)
            session.run(index_query)
            
            msg = "Inserting Data..."
            print(msg)
            if status_callback: status_callback(msg)
            session.run(insert_query, data=data_to_insert)
            
        msg = "Vector Indexing Complete!"
        print(msg)
        if status_callback: status_callback(msg)
        
    except Exception as e:
        msg = f"Error during ingestion: {e}"
        print(msg)
        if status_callback: status_callback(msg)
    finally:
        driver.close()

def get_retriever():
    """Returns a Neo4jVector retriever."""
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    try:
        vector_index = Neo4jVector.from_existing_graph(
            embeddings,
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
            index_name="strategy_vector_index",
            node_label="Chunk",
            text_node_properties=["text", "source", "page"],
            embedding_node_property="embedding",
        )
        return vector_index.as_retriever()
    except Exception as e:
        print(f"Vector Store Error: {e}")
        return None

def search_vectors(query: str):
    """Simple wrapper for vector search."""
    retriever = get_retriever()
    if not retriever:
        return ["Vector store not available."]
    
    try:
        docs = retriever.invoke(query)
        return [f"Source: {d.metadata.get('source', 'unknown')} (Page {d.metadata.get('page', '?')})\nContent: {d.page_content}" for d in docs]
    except Exception as e:
        return [f"Error searching vectors: {e}"]

if __name__ == "__main__":
    ingest_vectors()