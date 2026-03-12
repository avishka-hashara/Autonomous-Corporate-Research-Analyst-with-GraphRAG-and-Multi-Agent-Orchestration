# 🤖 Corporate Analyst Agent

> **An Autonomous AI Research Assistant specifically designed for Corporate Strategy & Analysis.**  
> Powered by **Llama 3**, **LangGraph**, and **TiDB Serverless**.

![Corporate Analyst Agent](assets/home.png)

## 📖 Overview

The **Corporate Analyst Agent** is a next-generation AI tool capable of performing deep research on complex corporate documents. Unlike traditional chatbots that simply predict the next word, this agent uses a **Cognitive Architecture** to plan, research, and verify information.

It combines **Knowledge Graphs** (to understand entities like *CEO*, *Competitor*, *Acquisition*) with **Vector Search** (to understand semantic meaning), ensuring that every answer is grounded strictly in the provided data.

## 🎯 The Problem Solved

Standard RAG (Retrieval-Augmented Generation) systems often fail on complex queries like *"How does the new regulation affect the subsidiary's risk profile?"* because they only look for matching keywords.

**This Agent solves that by:**
1.  **Extracting Structure**: It builds a graph of relationships from the document.
2.  **Multi-Step Reasoning**: It breaks down complex questions into sub-tasks (e.g., "Find subsidiary", "Check regulations", "Analyze risk").
3.  **No Hallucinations**: It explicitly refuses to answer if the information is not in the source text.

## ✨ Key Capabilities

*   **🕵️‍♂️ Autonomous Research**: The agent assumes the role of a "Supervisor" and assigns tasks to specialized workers ("Vector Searcher" and "Graph Searcher").
*   **🕸️ Knowledge Graph Extraction**: Automatically identifies and maps relationships between people, organizations, and concepts.
*   **🧠 Hybrid Intelligence**: Merges structured graph data with unstructured textual analysis for superior accuracy.
*   **⚡ Real-Time Processing**: optimized for speed and accuracy using Groq's LPU inference engine.
*   **🌐 Seamless Interface: Offers a "Professional Adaptive Mode" crafted for analysts, ensuring an elegant, responsive experience across all devices.


## 🏗️ How It Works

The system operates as a multi-agent workflow:

```mermaid
graph TD
    User[User Uploads PDF] --> Ingest[Ingestion Engine]
    Ingest -->|Structure| KnowledgeGraph[(Knowledge Graph)]
    Ingest -->|Semantics| VectorDB[(Vector Database)]
    
    User[User Asks Question] --> Supervisor[Supervisor Agent]
    Supervisor -->|Why?| Planner{Research Plan}
    
    Planner -->|Need Specifics| VectorWorker[Vector Search Agent]
    Planner -->|Need Relationships| GraphWorker[Graph Search Agent]
    
    VectorWorker -->|Retrieve| VectorDB
    GraphWorker -->|Query| KnowledgeGraph
    
    VectorWorker & GraphWorker --> Generator[Analyst Agent]
    Generator -->|Draft| Reviewer[Compliance Reviewer]
    Reviewer -->|Verified Answer| User
```

## 🛠️ Technology Stack

This project leverages the latest in AI and Cloud infrastructure:

*   **Large Language Model**: Meta Llama 3.1 (via Groq API)
*   **Orchestration**: LangChain & LangGraph
*   **Database**: TiDB Serverless (Unified Vector & Graph Store)
*   **Embeddings**: HuggingFace (`sentence-transformers`)
*   **Interface**: Streamlit (Python)

Link : https://autonomous-corporate-research-analyst.streamlit.app/

---
*Built for the future of Corporate Intelligence.*
