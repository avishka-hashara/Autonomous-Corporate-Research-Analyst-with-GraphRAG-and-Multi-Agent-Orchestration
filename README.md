# Autonomous Corporate Research Analyst (Cognitive Enterprise Architect)

This is an advanced AI agent designed to analyze corporate strategy documents using a **GraphRAG** approach and **Agentic State Machine** orchestration.

![Corporate Analyst Agent Interface](assets/interface_preview.png)

## 🧠 System Architecture

The system follows a **Supervisor-Worker-Reviewer** pattern using **LangGraph**:

1.  **Supervisor Node**:
    - Routes tasks to `VectorSearch` (unstructured text) or `GraphSearch` (relationships).
2.  **Worker Nodes**:
    - **VectorSearch**: Semantically searches text chunks.
    - **GraphSearch**: Generates Cypher queries for the Neo4j Knowledge Graph.
3.  **Generator Node**:
    - Synthesizes answers from all sources.
4.  **Reviewer Node**:
    - Self-corrects answers for faithfulness and relevance.

## 🚀 Key Features

*   **📂 Dynamic File Upload**: Upload PDF reports directly via the UI.
*   **️ Resource Management**: View and delete ingested documents and their associated graph data.
*   **Hybrid RAG**: Combines Vector embeddings with Graph connections.

## 🛠️ Prerequisites

1.  **Python 3.10+**
2.  **Neo4j Database**:
    - Local or Docker (`bolt://localhost:7687`).
    - APOC plugin enabled.
3.  **Ollama**:
    - `llama3` (Logic/Generation)
    - `nomic-embed-text` (Embeddings)

## 📦 Installation

1.  **Clone & Setup venv**:
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure `.env`**:
    Create a `.env` file with your credentials:
    ```env
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USERNAME=neo4j
    NEO4J_PASSWORD=your_password
    ```
    *Note: Advanced configuration can be modified in `src/config.py`.*

## ⚡ Quick Start

1.  **Run the App**:
    ```bash
    streamlit run src/app.py
    ```
    *The app will automatically check connections to Neo4j and Ollama on startup.*


2.  **Upload Data**:
    - Go to the **"📂 Document Upload"** sidebar.
    - Upload a PDF (e.g., a strategy report).
    - Click **"Process Document"**.

3.  **Explore**:
    - **💬 Chat**: Ask questions like "What are the key risks?".
    - **️ Manage Resources**: View or delete your files.

## 📂 Key Files

*   `src/app.py`: Main Streamlit application.
*   `src/graph_agent.py`: Agentic workflow definition.
*   `src/ingest.py`: PDF ETL pipeline (LLM extraction).
*   `src/config.py`: Centralized configuration.


2-WLQr6FcEU1GThqiXJ97Der-PKOnOa6Gsf3AXyvghE