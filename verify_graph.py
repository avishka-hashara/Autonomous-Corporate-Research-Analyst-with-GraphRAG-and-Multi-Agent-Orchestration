import os
import sys

# Add src to path if running from root
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.tidb_store import TiDBGraph
from dotenv import load_dotenv

load_dotenv()

def verify_tidb():
    print("Connecting to TiDB...")
    try:
        graph = TiDBGraph()
        print("Connected.")
        
        # Check Node Count
        nodes = graph.query("SELECT COUNT(*) as count FROM nodes")
        print(f"Nodes: {nodes[0]['count']}")
        
        # Check Edge Count
        edges = graph.query("SELECT COUNT(*) as count FROM edges")
        print(f"Edges: {edges[0]['count']}")
        
        # Check Chunk Count
        chunks = graph.query("SELECT COUNT(*) as count FROM chunks")
        print(f"Chunks: {chunks[0]['count']}")
        
        # Sample Data
        print("\nSample Nodes:")
        sample_nodes = graph.query("SELECT * FROM nodes LIMIT 5")
        for node in sample_nodes:
            print(node)
            
    except Exception as e:
        print(f"Error verification failed: {e}")

if __name__ == "__main__":
    verify_tidb()
