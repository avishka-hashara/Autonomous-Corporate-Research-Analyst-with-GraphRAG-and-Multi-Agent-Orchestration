import streamlit as st
import os
import json
import re
from dotenv import load_dotenv

# LangChain Imports - Robust Paths
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

# Page Config
st.set_page_config(page_title="Corporate Analyst AI", layout="wide")
st.title("🤖 Autonomous Corporate Research Analyst")
st.markdown("### Powered by Llama 3, Neo4j & GraphRAG")

# Load Env
load_dotenv()

# --- DEFINE MANUAL AGENT (Since langchain.agents is broken) ---

class SimpleVectorQA:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
        
    def invoke(self, inputs):
        if not self.retriever:
            return "Vector Store not available."
        query = inputs if isinstance(inputs, str) else inputs.get("query")
        # st.write(f"DEBUG: Searching vectors for: {query}")
        docs = self.retriever.invoke(query)
        context = "\n\n".join([d.page_content for d in docs])
        prompt = f"Answer based on:\n{context}\nQuestion: {query}"
        return self.llm.invoke(prompt).content

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
        
        # Parse JSON manually
        try:
            content = response.content
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                plan = json.loads(match.group(0))
            else:
                return {"output": content}
        except Exception:
            return {"output": f"Could not parse plan: {response.content}"}
            
        tool = plan.get("tool")
        tool_query = plan.get("query", query)
        
        # st.toast(f"Agent decided: {tool}")
        
        if tool == "GraphDatabase":
            try:
                result = self.graph_tool.invoke(tool_query)
                return {"output": result['result']}
            except Exception as e:
                return {"output": f"Graph Error: {e}"}
        elif tool == "DocumentSearch":
            if self.vector_tool:
                result = self.vector_tool.invoke(tool_query)
                return {"output": result}
            else:
                return {"output": "Vector search tool not available."}
        else:
            return {"output": tool_query}

# --- CACHED RESOURCE INITIALIZATION ---
@st.cache_resource
def get_agent():
    print("INITIALIZING AGENT...")
    
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

    # 1. LLM
    llm = ChatOllama(model="llama3", temperature=0)

    # 2. Graph
    graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)

    # 3. Vector Store
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
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
        st.error(f"Vector Index Error: {e}")
        vector_index = None

    # 4. Tools Setup
    
    # Strict Cypher Prompt
    CYPHER_GENERATION_TEMPLATE = """
    Task: Generate Cypher statement to query a graph database.
    Instructions:
    Use only the provided relationship types and properties in the schema.
    Do not use any other relationship types or properties that are not provided.
    Schema:
    {schema}
    
    CRITICAL NODE PROPERTIES:
    - All nodes are identified by the property 'id', NOT 'name'.
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
        cypher_prompt=cypher_prompt,
        verbose=True,
        allow_dangerous_requests=True
    )

    if vector_index:
        vector_chain = SimpleVectorQA(llm, vector_index.as_retriever())
    else:
        vector_chain = None

    # 5. Initialize Manual Agent
    agent = ManualAgent(llm, graph_chain, vector_chain)
    
    return agent

# Initialize the agent
try:
    agent = get_agent()
    st.success("System Ready: Llama 3 Connected to Neo4j Graph")
except Exception as e:
    st.error(f"Failed to initialize: {e}")

# --- CHAT INTERFACE ---

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about Project Titan..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = agent.invoke(prompt)
                result = response['output']
                st.markdown(result)
                st.session_state.messages.append({"role": "assistant", "content": result})
            except Exception as e:
                st.error(f"An error occurred: {e}")