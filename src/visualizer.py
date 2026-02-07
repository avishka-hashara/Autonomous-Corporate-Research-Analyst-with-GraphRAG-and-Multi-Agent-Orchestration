import os
from neo4j import GraphDatabase
from streamlit_agraph import agraph, Node, Edge, Config
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def get_graph_data(limit=50):
    """
    Fetches nodes and relationships from Neo4j and returns them as agraph objects.
    """
    nodes = []
    edges = []
    visited_nodes = set()
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    query = f"""
    MATCH (n)-[r]->(m)
    RETURN n, r, m
    LIMIT {limit}
    """
    
    try:
        with driver.session() as session:
            result = session.run(query)
            
            for record in result:
                n = record["n"]
                r = record["r"]
                m = record["m"]
                
                # --- Source Node ---
                n_id = n.element_id if hasattr(n, 'element_id') else str(n.id)
                n_label = list(n.labels)[0] if n.labels else "Unknown"
                n_title = n.get("id", n_label) # Use 'id' property or label as title
                
                if n_title not in visited_nodes:
                    nodes.append(Node(
                        id=n_title, # Use readable ID for linking
                        label=n_title,
                        size=25,
                        shape="circularImage" if n_label == "Person" else "dot",
                        image="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" if n_label == "Person" else None,
                        color="#FF6B6B" if n_label == "Person" else "#4ECDC4"
                    ))
                    visited_nodes.add(n_title)
                
                # --- Target Node ---
                m_id = m.element_id if hasattr(m, 'element_id') else str(m.id)
                m_label = list(m.labels)[0] if m.labels else "Unknown"
                m_title = m.get("id", m_label)

                if m_title not in visited_nodes:
                    nodes.append(Node(
                        id=m_title,
                        label=m_title,
                        size=20,
                        color="#FF6B6B" if m_label == "Person" else "#4ECDC4"
                    ))
                    visited_nodes.add(m_title)

                # --- Edge ---
                edges.append(Edge(
                    source=n_title,
                    target=m_title,
                    label=r.type,
                    color="#ccc"
                ))

    except Exception as e:
        print(f"Error fetching graph: {e}")
    finally:
        driver.close()
        
    return nodes, edges

def get_node_details(node_id):
    """
    Fetches all properties of a specific node.
    """
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    query = f"MATCH (n {{id: '{node_id}'}}) RETURN properties(n) as props"
    
    props = {}
    try:
        with driver.session() as session:
            result = session.run(query)
            record = result.single()
            if record:
                props = record["props"]
    except Exception as e:
        props = {"Error": str(e)}
    finally:
        driver.close()
        
    return props
