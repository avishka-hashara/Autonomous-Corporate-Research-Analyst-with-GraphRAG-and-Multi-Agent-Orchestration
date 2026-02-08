
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
    print("Starting inspection v2...")
    try:
        store = TiDBGraph()
        
        output_buffer = []

        output_buffer.append("--- DATABASE INSPECTION V2 ---\n")
        
        print("Querying nodes...")
        try:
            nodes = store.query("SELECT * FROM nodes LIMIT 5")
            output_buffer.append(f"\n--- NODES (Count: {len(nodes) if nodes else 0}) ---\n")
            if nodes:
                for node in nodes:
                    if isinstance(node.get('properties'), str):
                        try:
                            node['properties'] = json.loads(node['properties'])
                        except:
                            pass
                    output_buffer.append(json.dumps(node, indent=2, default=default_converter))
                    output_buffer.append("\n" + "-"*40 + "\n")
            else:
                output_buffer.append("No nodes found.\n")
        except Exception as e:
            output_buffer.append(f"Error querying nodes: {e}\n")

        print("Querying edges...")
        try:
            edges = store.query("SELECT * FROM edges LIMIT 5")
            output_buffer.append(f"\n--- EDGES (Count: {len(edges) if edges else 0}) ---\n")
            if edges:
                for edge in edges:
                    if isinstance(edge.get('properties'), str):
                        try:
                            edge['properties'] = json.loads(edge['properties'])
                        except:
                            pass
                    output_buffer.append(json.dumps(edge, indent=2, default=default_converter))
                    output_buffer.append("\n" + "-"*40 + "\n")
            else:
                output_buffer.append("No edges found.\n")
        except Exception as e:
            output_buffer.append(f"Error querying edges: {e}\n")

        print("Querying chunks...")
        try:
            # Exclude embedding vector matching original logic
            chunks = store.query("SELECT id, content, source, page, created_at FROM chunks LIMIT 5")
            output_buffer.append(f"\n--- CHUNKS (Count: {len(chunks) if chunks else 0}) ---\n")
            if chunks:
                for chunk in chunks:
                    output_buffer.append(f"ID: {chunk['id']}\n")
                    output_buffer.append(f"Source: {chunk['source']}\n")
                    output_buffer.append(f"Page: {chunk['page']}\n")
                    output_buffer.append(f"Date: {chunk['created_at']}\n")
                    content_preview = chunk['content'][:200].replace("\n", " ") if chunk['content'] else "None"
                    output_buffer.append(f"Content (preview): {content_preview}...\n")
                    output_buffer.append("-" * 40 + "\n")
            else:
                output_buffer.append("No chunks found.\n")
        except Exception as e:
            output_buffer.append(f"Error querying chunks: {e}\n")

        final_output = "".join(output_buffer)
        
        # Write to file
        with open("inspection_result_v2.txt", "w", encoding="utf-8") as f:
            f.write(final_output)
            
        print("Inspection complete. Results written.")
        # Also print to stdout as backup
        print(final_output)

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_database()
