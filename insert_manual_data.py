import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

queries = [
    "MERGE (p:Person {id: 'Sarah Connor', type: 'Person'})",
    "MERGE (j:Person {id: 'John Smith', type: 'Person'})",
    "MERGE (m:Person {id: 'Michael Ross', type: 'Person'})",
    "MERGE (o:Organization {id: 'TechCorp Inc.', type: 'Organization'})",
    "MERGE (p)-[:REPORTS_TO]->(j)",
    "MERGE (p)-[:WORKS_FOR]->(o)",
    "MERGE (j)-[:WORKS_FOR]->(o)",
    "MERGE (m)-[:WORKS_FOR]->(o)",
    "MERGE (m)-[:APPROVES_BUDGET]->(o)"
]

with driver.session() as session:
    for q in queries:
        try:
            session.run(q)
            print(f"Ran: {q}")
        except Exception as e:
            print(f"Failed: {q} - {e}")

print("Manual Data Insertion Complete.")
driver.close()
