import os
import json
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.graphs import Neo4jGraph
# 1. Setup
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, LLM_MODEL

# Initialize Graph
graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)

# 2. The Llama 3 Model (Structured Output Mode)
llm = ChatOllama(model=LLM_MODEL, temperature=0, format="json")

# 3. The Extraction Prompt
system_prompt = """
You are a Data Engineer extracting information for a Knowledge Graph.
Extract entities (People, Organizations, Projects, Locations, Concepts) and relationships.

Return a strictly valid JSON object with this format:
{{
  "nodes": [
    {{"id": "Sarah Connor", "type": "Person"}},
    {{"id": "TechCorp", "type": "Organization"}}
  ],
  "relationships": [
    {{"source": "Sarah Connor", "target": "TechCorp", "type": "WORKS_FOR"}}
  ]
}}

Ensure "id" is the specific name. "type" should be generic (Person, Organization, etc.).
RELATIONSHIPS should be UPPERCASE (e.g., LOCATED_IN, MANAGED_BY).
"""

import sys

def process_document(file_path: str = None, status_callback=None):
    msg = "Loading PDF using PyPDFLoader (Fallback)..."
    print(msg)
    if status_callback: status_callback(msg)
    
    # Check for CLI argument or use default if not provided
    if not file_path:
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
        else:
            file_path = "data/strategy_report.pdf"
    
    msg = f"Processing: {file_path}"
    print(msg)
    if status_callback: status_callback(msg)

    if not os.path.exists(file_path):
        msg = f"Error: File {file_path} not found."
        print(msg)
        if status_callback: status_callback(msg)
        return

    loader = PyPDFLoader(file_path)
    docs = loader.load()
    
    # Split text into chunks (LLMs can't read whole books at once)
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    
    msg = f"Processing {len(chunks)} chunks..."
    print(msg)
    if status_callback: status_callback(msg)
    
    for i, chunk in enumerate(chunks):
        msg = f"Extracting graph from chunk {i+1}/{len(chunks)}..."
        print(msg)
        if status_callback: status_callback(msg)
        
        # Invoke Llama 3
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Extract info from this text:\n\n{text}")
        ])
        chain = prompt | llm
        try:
            response = chain.invoke({"text": chunk.page_content})
            print(f"DEBUG RESPONSE: {response.content[:100]}...") # Truncate log
            
            # Since we requested JSON format, the content should be JSON
            try:
                data = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback regex if Llama3 decides to chat
                match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                else:
                    raise ValueError("No JSON found in response")
            
            # Write to Neo4j
            # We use Cypher queries to merge nodes and relationships
            
            # 1. Create the Document Node first
            doc_name = os.path.basename(file_path)
            try:
                graph.query("MERGE (d:Document {name: $name})", params={"name": doc_name})
            except Exception as e:
                print(f"Error creating Document node: {e}")

            for node in data.get("nodes", []):
                # Sanitize inputs
                node_type = node.get('type', 'Unknown').replace(" ", "_")
                node_id = node.get('id', 'Unknown')
                
                # Note: node labels cannot be parameterized in Cypher (e.g. :Person), but properties can.
                # We trust node_type enough (simple string replace) but id should be param.
                cypher = f"MERGE (n:{node_type} {{id: $id}})"
                try:
                    graph.query(cypher, params={"id": node_id})
                    
                    # Link to Document
                    link_cypher = f"""
                    MATCH (n:{node_type} {{id: $id}}), (d:Document {{name: $doc_name}})
                    MERGE (n)-[:MENTIONED_IN]->(d)
                    """
                    graph.query(link_cypher, params={"id": node_id, "doc_name": doc_name})
                    
                except Exception as e:
                    print(f"Error merging node {node_id}: {e}")

            for rel in data.get("relationships", []):
                source = rel.get('source', '')
                target = rel.get('target', '')
                rel_type = rel.get('type', 'RELATED_TO').upper().replace(" ", "_")
                
                if source and target:
                    cypher = f"""
                    MATCH (a {{id: $source}}), (b {{id: $target}})
                    MERGE (a)-[:{rel_type}]->(b)
                    """
                    try:
                        graph.query(cypher, params={"source": source, "target": target})
                        # Ideally link relationship to doc too, but node link is usually sufficient for cascading delete
                    except Exception as e:
                        print(f"Error merging relationship {source}->{target}: {e}")
                
            msg = f"Chunk {i+1} saved to Graph linked to {doc_name}!"
            print(msg)
            
        except Exception as e:
            print(f"Error processing chunk {i+1}: {e}")

if __name__ == "__main__":
    # Clear DB first (Optional, good for testing)
    # console input to confirm clear
    print("Do you want to clear the database? (y/n)")
    # choice = input().lower()
    # if choice == 'y':
    #     graph.query("MATCH (n) DETACH DELETE n")
    #     print("Database cleared.")
    
    process_document()
