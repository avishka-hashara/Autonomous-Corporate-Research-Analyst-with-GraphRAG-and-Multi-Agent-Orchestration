# Autonomous Corporate Research Analyst (Cognitive Enterprise Architect)

This is an advanced AI agent designed to analyze corporate strategy documents using a **GraphRAG** approach and **Agentic State Machine** orchestration.

![Architecture](https://via.placeholder.com/800x400?text=Supervisor+->+Workers+->+Generator+->+Reviewer)

## 🧠 System Architecture

The system has been upgraded from a simple "Manual Agent" to a **Cognitive Enterprise Architect** using **LangGraph**. It follows a **Supervisor-Worker-Reviewer** pattern:

1.  **Supervisor Node**:
    - Analyzes the visual complexity of the user's query.
    - Routes the task to the appropriate worker (`VectorSearch` for unstructured text or `GraphSearch` for structured relationships).
    - Can decompose complex queries into multiple steps (via the Reviewer loop).

2.  **Worker Nodes**:
    - **VectorSearch Worker**: Queries the Neo4j Vector Index for semantic understanding (e.g., "What are the risks?").
    - **GraphSearch Worker**: Generates Cypher queries to find precise relationships in Neo4j (e.g., "Who reports to Sarah Connor?").

3.  **Generator Node**:
    - Synthesizes information from all workers to draft an answer.

4.  **Reviewer Node (Self-Correction)**:
    - Acts as a "Senior Editor".
    - Grades the answer for faithfulness and relevance.
    - **Loop**: If the answer is rejected, it sends critique back to the Supervisor to refine the search.

## 🚀 Features

*   **Hybrid Knowledge Store**: Uses Neo4j for both **Knowledge Graph** (Entities/Relationships) and **Vector Store** (Embeddings).
*   **Self-Correcting**: The agent can try up to 3 times to improve its answer based on critique.
*   **Structured Ingestion**: Uses a custom pipeline to extract entities (People, Orgs) and relationships from PDFs.
*   **Evaluation Pipeline**: Integrated **Ragas** framework to measure `faithfulness` and `answer_relevancy`.

## 🛠️ Prerequisites

1.  **Python 3.10+** (Recommend 3.10-3.12, works on 3.14 with verified fallbacks)
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
    *(Note: Uses `pypdf` for compatibility as `unstructured` has strict build requirements on Windows).*

3.  **Configure `.env`**:
    ```env
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USERNAME=neo4j
    NEO4J_PASSWORD=your_password
    ```

## ⚡ Quick Start

### 1. Ingest Data (ETL)
Populate the Knowledge Graph and Vector Index.

```bash
# 1. Extract Entities & Relationships to Neo4j
python src/ingest.py

# 2. Index Text Chunks for Vector Search
python src/vector_store.py
```

### 2. Run the Agent (UI)
Start the Streamlit interface.

```bash
streamlit run src/app.py
```

### 3. Run Evaluation (Optional)
Run the Ragas evaluation suite.

```bash
python src/eval.py
```

## 📂 Key Files

*   `src/graph_agent.py`: **Core Logic**. Defines the LangGraph state machine, nodes, and edges.
*   `src/ingest.py`: PDF ETL pipeline with Entity Extraction prompt.
*   `src/vector_store.py`: Vector embedding and indexing.
*   `src/app.py`: Streamlit UI.
*   `src/eval.py`: Evaluation script using Ragas.
