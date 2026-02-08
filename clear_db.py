
import sys
import os

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tidb_store import TiDBGraph
import logging

def clear_database():
    print("WARNING: This will delete all data from the TiDB database.")
    print("Clearing database...")
    
    try:
        graph = TiDBGraph()
        graph.clear_data() # Drops tables
        # Re-initialize schema immediately so the app doesn't crash on next run
        graph._init_schema() 
        print("Database cleared and schema re-initialized successfully.")
        
        # Also clear local files
        upload_dir = os.path.join(os.path.dirname(__file__), "data", "uploaded")
        if os.path.exists(upload_dir):
            for f in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, f)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        print(f"Deleted local file: {f}")
                except Exception as e:
                    print(f"Error deleting {f}: {e}")
            print("Local upload directory cleared.")
            
    except Exception as e:
        print(f"Error clearing database: {e}")

if __name__ == "__main__":
    clear_database()
