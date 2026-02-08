import os
import sys

# Add src to path if running from root
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import UPLOAD_DIR
from src.tidb_store import TiDBGraph
import shutil
from dotenv import load_dotenv

load_dotenv()

def reset_db():
    print("WARNING: This will delete ALL data in the TiDB Graph and Vector store.")
    print(f"WARNING: This will also delete ALL local files in {UPLOAD_DIR}")
    confirm = input("Are you sure? (y/n): ")
    
    if confirm.lower() == 'y':
        try:
            # 1. Clear Database
            graph = TiDBGraph()
            graph.clear_data()
            print("Database cleared successfully.")
            
            # 2. Clear Local Files
            if os.path.exists(UPLOAD_DIR):
                for filename in os.listdir(UPLOAD_DIR):
                    if filename.endswith(".pdf"):
                        file_path = os.path.join(UPLOAD_DIR, filename)
                        try:
                            os.remove(file_path)
                            print(f"Deleted {filename}")
                        except Exception as e:
                            print(f"Error deleting {filename}: {e}")
            print("Local files cleared.")
            
        except Exception as e:
            print(f"Error clearing database: {e}")
    else:
        print("Reset cancelled.")

if __name__ == "__main__":
    reset_db()
