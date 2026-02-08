import os
import json
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.graphs import Neo4jGraph # Keeping for reference if needed, but we use TiDBGraph now
from tidb_store import TiDBGraph

# 1. Setup
from config import LLM_MODEL

# Initialize Graph
graph = TiDBGraph()

# 2. The Llama 3 Model (Structured Output Mode)
llm = ChatGroq(model=LLM_MODEL, temperature=0).bind(response_format={"type": "json_object"})

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
            
            # Write to TiDB (Graph)
            # We collect all nodes and edges for this chunk and insert in one batch
            
            batch_nodes = []
            batch_edges = []
            
            # 1. Document Node
            doc_name = os.path.basename(file_path)
            batch_nodes.append({
                "id": doc_name,
                "type": "Document",
                "properties": {"name": doc_name}
            })

            # 2. Extracted Nodes
            for node in data.get("nodes", []):
                # Sanitize inputs
                node_type = node.get('type', 'Unknown').replace(" ", "_")
                node_id = node.get('id', 'Unknown')
                
                batch_nodes.append({
                    "id": node_id,
                    "type": node_type,
                    "properties": {"id": node_id}
                })
                
                # Link to Document
                batch_edges.append({
                    "source": node_id,
                    "target": doc_name,
                    "type": "MENTIONED_IN",
                    "properties": {}
                })

            # 3. Extracted Relationships
            for rel in data.get("relationships", []):
                source = rel.get('source', '')
                target = rel.get('target', '')
                rel_type = rel.get('type', 'RELATED_TO').upper().replace(" ", "_")
                
                if source and target:
                    batch_edges.append({
                        "source": source,
                        "target": target,
                        "type": rel_type,
                        "properties": {}
                    })
            
            # Execute Batch Insert covering all nodes and edges for this chunk
            try:
                graph.batch_insert_graph_data(batch_nodes, batch_edges)
                msg = f"Chunk {i+1} saved to Graph linked to {doc_name}!"
                print(msg)
            except Exception as e:
                print(f"Error saving batch for chunk {i+1}: {e}")

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
