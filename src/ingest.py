import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv
import json
import re

from langchain_core.output_parsers import JsonOutputParser

# 1. Setup
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)

# 2. The Llama 3 Model (Structured Output Mode)
llm = ChatOllama(model="llama3", temperature=0)

# 3. The Extraction Prompt
# We force the model to ONLY speak JSON. This is crucial for automation.
system_prompt = """
You are a Data Engineer extracting information for a Knowledge Graph.
Extract entities (People, Organizations, Projects, Locations) and relationships.

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
"""

def process_document():
    print("Loading PDF...")
    loader = PyPDFLoader("data/strategy_report.pdf")
    docs = loader.load()
    
    # Split text into chunks (LLMs can't read whole books at once)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    
    print(f"Processing {len(chunks)} chunks...")
    
    parser = JsonOutputParser()

    for i, chunk in enumerate(chunks):
        print(f"Extracting graph from chunk {i+1}...")
        
        # Invoke Llama 3
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Extract info from this text:\n\n{text}")
        ])
        chain = prompt | llm
        try:
            response = chain.invoke({"text": chunk.page_content})
            print(f"DEBUG RESPONSE: {response.content}")
            
            # Manual Regex Extraction
            match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if match:
                json_str = match.group(0)
                data = json.loads(json_str)
                print(f"DEBUG DATA: {data}")
            else:
                raise ValueError("No JSON found in response")
            
            # Write to Neo4j
            # We use Cypher queries to merge nodes and relationships
            for node in data.get("nodes", []):
                cypher = f"MERGE (n:{node['type']} {{id: '{node['id']}'}})"
                graph.query(cypher)
                
            for rel in data.get("relationships", []):
                cypher = f"""
                MATCH (a {{id: '{rel['source']}'}}), (b {{id: '{rel['target']}'}})
                MERGE (a)-[:{rel['type'].upper().replace(" ", "_")}]->(b)
                """
                graph.query(cypher)
                
            print(f"Chunk {i+1} saved to Graph!")
            
        except Exception as e:
            print(f"Error parsing chunk {i+1}: {e}")

if __name__ == "__main__":
    # Clear DB first (Optional, good for testing)
    graph.query("MATCH (n) DETACH DELETE n")
    process_document()