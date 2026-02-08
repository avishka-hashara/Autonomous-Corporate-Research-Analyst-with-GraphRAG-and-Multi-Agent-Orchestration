
import sys
import os
import json

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from tidb_store import TiDBGraph
from config import LLM_MODEL
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def debug_system():
    print("--- DIAGNOSTIC START ---")
    graph = TiDBGraph()
    
    # 1. Check Vector Data for Doc_A roughly
    print("\n1. Checking Vector Data...")
    try:
        # Check if any chunks exist
        count = graph.query("SELECT COUNT(*) as c FROM chunks")[0]['c']
        print(f"Total Chunks in DB: {count}")
        
        # Check sources
        sources = graph.query("SELECT DISTINCT source FROM chunks")
        print("Sources in DB:", [s['source'] for s in sources])
        
        # Check specific keyword match
        res = graph.query("SELECT content FROM chunks WHERE content LIKE '%Facebook%' LIMIT 1")
        if res:
             print("Found 'Facebook' in vector chunks: YES")
        else:
             print("Found 'Facebook' in vector chunks: NO")

    except Exception as e:
        print(f"Error checking vectors: {e}")

    # 2. Simulate Graph Search
    print("\n2. Simulating Graph Search...")
    query = "what are Facebook's core products?"
    
    sql_prompt = """
    Task: Generate SQL for: {query}
    Schema: {schema}
    
    The database contains a graph structure in 'nodes' and 'edges' tables.
    - 'nodes' table: id, type, properties (JSON)
    - 'edges' table: source, target, type, properties (JSON)
    
    IMPORTANT: Use MySQL compatible JSON syntax. Do NOT use PostgreSQL operators like ->> or @>.
    
    To find relationships, JOIN edges with nodes.
    Example: 
    SELECT s.id AS source, t.id AS target, e.type 
    FROM edges e 
    JOIN nodes s ON e.source = s.id 
    JOIN nodes t ON e.target = t.id 
    WHERE s.id LIKE '%Keywords%';
    
    Return ONLY JSON: {{"sql": "SELECT ...", "reasoning": "..."}}
    """
    
    try:
        llm = ChatGroq(model=LLM_MODEL, temperature=0).bind(response_format={"type": "json_object"})
        
        prompt = ChatPromptTemplate.from_messages([
             ("system", "You are a TiDB SQL expert."),
             ("human", sql_prompt)
        ])
        chain = prompt | llm
        print("Generating SQL...")
        response = chain.invoke({"query": query, "schema": graph.get_schema()})
        content = response.content
        print(f"LLM Response: {content}")
        
        sql_json = json.loads(content)
        sql = sql_json.get("sql")
        
        print(f"Executing SQL: {sql}")
        result = graph.query(sql)
        print(f"SQL Result: {result}")
        
    except Exception as e:
        print(f"GRAPH SEARCH FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_system()
