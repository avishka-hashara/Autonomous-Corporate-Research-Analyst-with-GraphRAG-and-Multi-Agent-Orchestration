import os
import json
from typing import TypedDict, List, Literal
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from tidb_store import TiDBGraph
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from vector_store import search_vectors

load_dotenv()

# --- 1. State Definition ---
class AgentState(TypedDict):
    question: str
    plan: str
    documents: List[str] # Content from vector/graph
    answer: str
    critique: str
    attempts: int

from config import LLM_MODEL

# --- 2. Tool Setup ---
graph = TiDBGraph()
llm = ChatGroq(model=LLM_MODEL, temperature=0)
json_llm = ChatGroq(model=LLM_MODEL, temperature=0).bind(response_format={"type": "json_object"})

# --- 3. Nodes ---

def supervisor_node(state: AgentState):
    """
    Decides the research plan based on the question and previous attempts.
    """
    question = state["question"]
    attempts = state.get("attempts", 0)
    print(f"--- [SUPERVISOR] Attempts: {attempts} | Question: {question} ---")
    
    # If we have an answer but it was rejected (critique exists), we need to adjust
    critique = state.get("critique", "")
    
    system = """You are the Supervisor of a Corporate Research Team.
    Analyze the user question and decide on a research plan.
    
    Available Workers:
    1. VectorSearch: For finding specific documents, reports, risks, strategy content.
    2. GraphSearch: For finding entity relationships, hierarchy, acquisitions, structure.
    
    Return JSON:
    {{
        "next_step": "VectorSearch" or "GraphSearch" or "GenerateAnswer",
        "query": "The specific query for the worker"
    }}
    """
    
    if critique:
        system += f"\n\nPREVIOUS CRITIQUE: {{critique}}\nAdjust your plan to address this."
    
    context_summary = f"Documents found so far: {{doc_count}}"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "Question: {question}\n\nContext: {context_summary}\n\nAttempts: {attempts}")
    ])
    
    chain = prompt | json_llm
    response = chain.invoke({
        "question": question, 
        "context_summary": f"Documents found so far: {len(state.get('documents', []))}",
        "attempts": attempts,
        "critique": critique
    })
    plan = json.loads(response.content)
    
    return {"plan": plan, "attempts": attempts + 1}

def vector_search_node(state: AgentState):
    """
    Executes a vector search.
    """
    plan = state["plan"]
    query = plan.get("query", state["question"])
    
    print(f"--- [VECTOR SEARCH] {query} ---")
    
    results = search_vectors(query)

    return {"documents": state.get("documents", []) + results}

def graph_search_node(state: AgentState):
    """
    Executes a SQL query on TiDB.
    """
    plan = state["plan"]
    query = plan.get("query", state["question"])
    
    print(f"--- [GRAPH SEARCH] {query} ---")
    
    # We use LLM to gen SQL
    sql_prompt = """
    Task: Generate SQL for: {query}
    Schema: {schema}
    
    The database contains a graph structure in 'nodes' and 'edges' tables.
    - 'nodes' table: id, type, properties (JSON)
    - 'edges' table: source, target, type, properties (JSON)
    
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
        
        prompt = ChatPromptTemplate.from_messages([
             ("system", "You are a TiDB SQL expert."),
             ("human", sql_prompt)
        ])
        chain = prompt | json_llm
        response = chain.invoke({"query": query, "schema": graph.get_schema()})
        
        sql_json = json.loads(response.content)
        sql = sql_json.get("sql")
        
        print(f"Executing: {sql}")
        result = graph.query(sql)
        doc = f"Graph Result for '{query}': {result}"
        
    except Exception as e:
        doc = f"Graph Search Error: {e}"

    return {"documents": state.get("documents", []) + [doc]}

def generator_node(state: AgentState):
    """
    Generates the final answer based on gathered documents.
    """
    question = state["question"]
    documents = state.get("documents", [])
    
    if not documents:
        print("--- [GENERATOR] No documents found. ---")
        return {"answer": "I cannot answer this question because no relevant information was found in the knowledge base. Please upload a relevant document."}

    docs = "\n\n".join(documents)
    print(f"--- [GENERATOR] Generating Answer... ---")
    
    system = """You are a Corporate Analyst. Answer the question based ONLY on the provided context.
    If the answer is not in the context, state that you don't know."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "Context:\n{docs}\n\nQuestion: {question}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"docs": docs, "question": question})
    return {"answer": response.content}

def reviewer_node(state: AgentState):
    """
    Reviews the answer for quality and hallucinations.
    """
    question = state["question"]
    answer = state.get("answer", "No answer generated.")
    docs = state.get("documents", [])
    print(f"--- [REVIEWER] Grading Answer... ---")
    
    system = """You are a Senior Editor. Grade the answer.
    1. Does it answer the question?
    2. Is it supported by context?
    
    Return JSON:
    {{
        "status": "APPROVED" or "REJECTED",
        "critique": "Explanation if rejected"
    }}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "Q: {question}\nA: {answer}")
    ])
    
    chain = prompt | json_llm
    response = json.loads(chain.invoke({"question": question, "answer": answer}).content)
    
    if response["status"] == "APPROVED":
        return {"critique": None}
    else:
        return {"critique": response["critique"]}

# --- 4. Graph Construction ---

workflow = StateGraph(AgentState)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("vector_search", vector_search_node)
workflow.add_node("graph_search", graph_search_node)
workflow.add_node("generator", generator_node)
workflow.add_node("reviewer", reviewer_node)

workflow.set_entry_point("supervisor")

def route_supervisor(state):
    attempts = state.get("attempts", 0)
    if attempts >= 3:
        return "generator"

    plan = state["plan"]
    step = plan.get("next_step")
    if step == "VectorSearch":
        return "vector_search"
    elif step == "GraphSearch":
        return "graph_search"
    elif step == "GenerateAnswer":
        return "generator"
    else:
        return "generator" # Default

workflow.add_conditional_edges("supervisor", route_supervisor)

workflow.add_edge("vector_search", "supervisor") # Loop back for more steps? Or to generator?
# Let's simplify: Workers -> Supervisor (to decide if more info needed or Generate)
# For this blueprint, Supervisor spawns sub-tasks. 
# Let's say Workers -> Supervisor is the loop.
# But Blueprint asks for "Cyclic Edge: If Reviewer rejects... loop back to Supervisor".

workflow.add_edge("vector_search", "supervisor") 
workflow.add_edge("graph_search", "supervisor")

workflow.add_edge("generator", "reviewer")

def route_reviewer(state):
    critique = state.get("critique")
    attempts = state.get("attempts", 0)
    if critique and attempts < 3: # Limit loops
        return "supervisor"
    else:
        return END

workflow.add_conditional_edges("reviewer", route_reviewer)

app = workflow.compile()
