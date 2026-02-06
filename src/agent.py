import os
import json
import re
from dotenv import load_dotenv

# LangChain Imports - Minimal Dependencies
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# 1. Setup & Config
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

print("Initializing 'The Corporate Analyst'...")

# 2. Connect to the "Brains"
llm = ChatOllama(model="llama3", temperature=0)
graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Robust Vector Index Loading
try:
    vector_index = Neo4jVector.from_existing_graph(
        embeddings,
        url=NEO4J_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
        index_name="strategy_vector_index",
        node_label="Chunk",
        text_node_properties=["text"],
        embedding_node_property="embedding",
    )
except Exception as e:
    print(f"Warning: Could not connect to Vector Index: {e}")
    vector_index = None

# 3. Skills
# Skill 1: Graph

CYPHER_GENERATION_TEMPLATE = """
Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}

CRITICAL NODE PROPERTIES:
- All nodes (Person, Organization) are identified by the property 'id', NOT 'name'.
- Example: MATCH (n:Person {{id: "Sarah Connor"}}) RETURN n

The question is:
{question}
"""

cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"], 
    template=CYPHER_GENERATION_TEMPLATE
)

graph_chain = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    verbose=True,
    cypher_prompt=cypher_prompt,
    allow_dangerous_requests=True
)

# Skill 2: Vector (Manual)
class SimpleVectorQA:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
        
    def invoke(self, inputs):
        if not self.retriever:
            return "Vector Store not available."
        query = inputs if isinstance(inputs, str) else inputs.get("query")
        print(f"Searching vectors for: {query}")
        docs = self.retriever.invoke(query)
        # Handle docs - extract content
        context = "\n\n".join([d.page_content for d in docs])
        prompt = f"Answer based on:\n{context}\nQuestion: {query}"
        return self.llm.invoke(prompt).content

if vector_index:
    vector_chain = SimpleVectorQA(llm, vector_index.as_retriever())
else:
    vector_chain = None

# 4. Manual Agent Implementation
class ManualAgent:
    def __init__(self, llm, graph_tool, vector_tool):
        self.llm = llm
        self.graph_tool = graph_tool
        self.vector_tool = vector_tool
        
    def invoke(self, query):
        # 1. Decide which tool to use
        system = """You are a Corporate Analyst Agent. You have two tools:
        1. GraphDatabase: For organizational structure, roles, relationships (CEO, works for, teams).
        2. DocumentSearch: For strategy, content, dates, summaries, risks.
        
        Given the user query, return a JSON object with:
        {{ "tool": "GraphDatabase" or "DocumentSearch" or "DirectAnswer", "query": "The specific query for the tool" }}
        
        If the user greets or asks something unrelated, use "DirectAnswer".
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            ("human", "{query}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"query": query})
        
        # Parse JSON manually (robustly)
        try:
            content = response.content
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                plan = json.loads(match.group(0))
            else:
                # Fallback
                return {"output": content}
        except Exception:
            return {"output": f"Could not parse plan: {response.content}"}
            
        tool = plan.get("tool")
        tool_query = plan.get("query", query)
        
        print(f"\n[Agent Decision]: Using {tool} with query: '{tool_query}'")
        
        if tool == "GraphDatabase":
            result = self.graph_tool.invoke(tool_query)
            return {"output": result['result']}
        elif tool == "DocumentSearch":
            if self.vector_tool:
                result = self.vector_tool.invoke(tool_query)
                return {"output": result}
            else:
                return {"output": "Vector search tool not available."}
        else:
            return {"output": tool_query}

agent = ManualAgent(llm, graph_chain, vector_chain)

# 6. Chat Loop
if __name__ == "__main__":
    print("\n✅ SYSTEM READY. Ask a question about the 'Project Titan' strategy.")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            query = input("User: ")
        except EOFError:
            break
        if query.lower() in ["exit", "quit"]:
            break
        
        try:
            response = agent.invoke(query)
            print(f"\nAgent: {response.get('output', response)}\n")
        except Exception as e:
            print(f"Error: {e}")