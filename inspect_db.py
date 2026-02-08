
import sys
import os
import json
import datetime

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tidb_store import TiDBGraph

def default_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def inspect_database():
    try:
        store = TiDBGraph()
        
        with open("inspection_result.txt", "w", encoding="utf-8") as f:
            f.write("--- DATABASE INSPECTION ---\n")
            
            f.write("\n--- NODES (First 5) ---\n")
            nodes = store.query("SELECT * FROM nodes LIMIT 5")
            if nodes:
                for node in nodes:
                    # Parse properties JSON if it's a string
                    if isinstance(node.get('properties'), str):
                        try:
                            node['properties'] = json.loads(node['properties'])
                        except:
                            pass
                    f.write(json.dumps(node, indent=2, default=default_converter))
                    f.write("\n" + "-"*40 + "\n")
            else:
                f.write("No nodes found.\n")

            f.write("\n--- EDGES (First 5) ---\n")
            edges = store.query("SELECT * FROM edges LIMIT 5")
            if edges:
                for edge in edges:
                     # Parse properties JSON if it's a string
                    if isinstance(edge.get('properties'), str):
                        try:
                            edge['properties'] = json.loads(edge['properties'])
                        except:
                            pass
                    f.write(json.dumps(edge, indent=2, default=default_converter))
                    f.write("\n" + "-"*40 + "\n")
            else:
                f.write("No edges found.\n")

            f.write("\n--- CHUNKS (First 5) ---\n")
            # Exclude embedding vector for readability
            chunks = store.query("SELECT id, content, source, page, created_at FROM chunks LIMIT 5")
            if chunks:
                for chunk in chunks:
                    f.write(f"ID: {chunk['id']}\n")
                    f.write(f"Source: {chunk['source']}\n")
                    f.write(f"Page: {chunk['page']}\n")
                    f.write(f"Date: {chunk['created_at']}\n")
                    content_preview = chunk['content'][:200].replace("\n", " ")
                    f.write(f"Content (preview): {content_preview}...\n")
                    f.write("-" * 40 + "\n")
            else:
                f.write("No chunks found.\n")
                
        print("Inspection complete. Results written to inspection_result.txt")

    except Exception as e:
        print(f"Error inspecting database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_database()
