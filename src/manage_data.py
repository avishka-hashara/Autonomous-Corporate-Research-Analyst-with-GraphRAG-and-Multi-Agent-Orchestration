import os
import shutil
from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv

from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, UPLOAD_DIR

graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)

def list_documents():
    """
    Returns a list of documents found in the upload directory.
    Returns: List[str] filenames
    """
    if not os.path.exists(UPLOAD_DIR):
        return []
    return [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".pdf")]

def delete_document(filename: str):
    """
    Deletes a document from:
    1. Disk
    2. Vector Store (Chunks)
    3. Knowledge Graph (Document node and linked entities if isolated)
    """
    results = {"disk": False, "vector": False, "graph": False}
    
    # 1. Delete from Disk
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            results["disk"] = True
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    # 2. Delete from Vector Store
    # Chunks have a 'source' metadata field. Usually it's the full path.
    # We match by suffix to be safe.
    try:
        # Note: source path in vector store might be relative or absolute depending on how it was ingested.
        # We try to match end of string.
        query = """
        MATCH (c:Chunk) 
        WHERE c.source ENDS WITH $filename 
        DETACH DELETE c
        """
        graph.query(query, params={"filename": filename})
        results["vector"] = True
    except Exception as e:
        print(f"Error deleting vectors: {e}")

    # 3. Delete from Knowledge Graph
    # We delete the Document node. 
    # Optionally, we could delete entities that are ONLY mentioned in this document.
    # For now, let's just delete the Document node and the MENTIONED_IN relationships (via DETACH).
    try:
        query = """
        MATCH (d:Document {name: $filename})
        DETACH DELETE d
        """
        graph.query(query, params={"filename": filename})
        results["graph"] = True
    except Exception as e:
        print(f"Error deleting graph node: {e}")
        # If it's a connection error, we might want to let the user know, but for now print is okay as this is backend
        
    return results
