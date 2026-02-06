import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

with driver.session() as session:
    result = session.run("CALL dbms.components() YIELD name, versions, edition")
    for record in result:
        print(f"Name: {record['name']}")
        print(f"Versions: {record['versions']}")
        print(f"Edition: {record['edition']}")

    print("\nAttempting simplified CALL syntax check:")
    try:
        # Try old syntax
        session.run("CALL { RETURN 1 }")
        print("Support for CALL { ... } verified.")
    except Exception as e:
        print(f"Old Syntax Failed: {e}")

driver.close()
