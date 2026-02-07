import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def reset_database():
    """
    Clears all nodes, relationships, and indexes from the Neo4j database.
    """
    print("WARNING: This will delete ALL data in the Neo4j database.")
    confirm = input("Are you sure? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return

    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        with driver.session() as session:
            # Delete all nodes and relationships
            print("Deleting all nodes and relationships...")
            session.run("MATCH (n) DETACH DELETE n")
            
            # Drop vector index if exists
            print("Dropping vector index...")
            try:
                session.run("DROP INDEX strategy_vector_index")
            except Exception as e:
                print(f"Index might not exist or verify name: {e}")

        print("Database Reset Complete.")
        driver.close()
    except Exception as e:
        print(f"Error resetting database: {e}")

if __name__ == "__main__":
    reset_database()
