import os
import shutil
from tidb_store import TiDBGraph
from dotenv import load_dotenv

from config import UPLOAD_DIR

# Initialize Graph
graph = TiDBGraph()

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
    2. TiDB Vector Store (Chunks)
    3. TiDB Knowledge Graph (Document node)
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
    try:
        # Delete chunks where source matches filename (suffix match)
        sql = "DELETE FROM chunks WHERE source LIKE %s"
        # In Cypher we used ENDS WITH. In SQL: '%filename'
        graph.query(sql, (f"%{filename}",))
        results["vector"] = True
    except Exception as e:
        print(f"Error deleting vectors: {e}")

    # 3. Delete from Knowledge Graph
    try:
        # Delete Document Node. Edges will be deleted via CASCADE.
        # In ingest.py, we used doc_name as the ID.
        sql = "DELETE FROM nodes WHERE id = %s"
        graph.query(sql, (filename,))
        results["graph"] = True
    except Exception as e:
        print(f"Error deleting graph node: {e}")
        
    return results
