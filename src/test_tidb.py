
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def test_tidb():
    print("Testing TiDB Connection...")
    config = {
        'host': os.getenv("TIDB_HOST"),
        'port': os.getenv("TIDB_PORT"),
        'user': os.getenv("TIDB_USER"),
        'password': os.getenv("TIDB_PASSWORD"),
        'database': os.getenv("TIDB_DATABASE")
    }
    
    # SSL check
    ca_path = os.getenv("TIDB_CA_PATH")
    if ca_path:
        config['ssl_ca'] = ca_path
        config['ssl_verify_cert'] = True

    try:
        print(f"Connecting to {config['host']}...")
        conn = mysql.connector.connect(**config)
        print("✅ Connection Successful!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()
        print(f"✅ Database Version: {version[0]}")
        
        conn.close()
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_tidb()
