import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Neo4jVector
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

from neo4j import GraphDatabase

def ingest_vectors():
    print("Loading PDF for Vectorization...")
    loader = PyPDFLoader("data/strategy_report.pdf")
    docs = loader.load()

    # Split documents
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    print(f"Created {len(chunks)} text chunks.")

    # 2. Initialize Embedding Model (Nomic)
    print("Initializing Ollama Embeddings...")
    embeddings_model = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url="http://127.0.0.1:11434"
    )

    # 3. Generate Embeddings Manually
    print("Generating embeddings... (This may take a while)")
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
    print("Connecting to Neo4j...")
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

            print("Creating Vector Index...")
            session.run(index_query)
            
            print("Inserting Data...")
            session.run(insert_query, data=data_to_insert)
            
        print("Vector Indexing Complete!")
    except Exception as e:
        print(f"Error during ingestion: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    ingest_vectors()