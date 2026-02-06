import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def run_query(session, query, desc):
    print(f"\nTesting {desc}...")
    try:
        session.run(query)
        print("SUCCESS")
    except Exception as e:
        print(f"FAILED: {e}")

with driver.session() as session:
    # Test 1: Old style CALL { WITH ... } for subquery
    q1 = """
    UNWIND [1, 2] AS x 
    CALL { 
        WITH x 
        RETURN x*2 AS y 
    } 
    RETURN x, y
    """
    run_query(session, q1, "Old Style Subquery (WITH x)")

    # Test 2: Call in Transactions (Old Style)
    q2 = """
    UNWIND range(1, 5) AS id 
    CALL { 
        WITH id 
        MERGE (:TestNode {id: id}) 
    } IN TRANSACTIONS OF 2 ROWS
    """
    run_query(session, q2, "Transaction Batching (WITH id)")

driver.close()
