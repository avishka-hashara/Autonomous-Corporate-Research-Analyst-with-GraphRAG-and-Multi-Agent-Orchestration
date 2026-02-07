import os
import traceback
from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

print(f"Connecting to: {NEO4J_URI} as {NEO4J_USERNAME}")

try:
    graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)
    print("Connected to Neo4j.")

    print("Running query: MATCH (n) OPTIONAL MATCH (n)-[r]->(m) RETURN n, r, m")
    result = graph.query("MATCH (n) OPTIONAL MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100")
    
    if not result:
        print("Graph is empty.")
    else:
        print(f"Found {len(result)} records:")
        for record in result:
            print(record)

except Exception:
    traceback.print_exc()
