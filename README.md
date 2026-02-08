# Corporate Analyst Agent

An autonomous research assistant capable of knowledge graph extraction and vector-based strategy analysis. Powered by **Llama 3 (via Groq)** and **TiDB Serverless**.

![Corporate Analyst Agent](https://img.icons8.com/clouds/200/company.png)

## Features
*   **Knowledge Graph Extraction**: Converts PDF documents into structured graph data (Nodes/Edges).
*   **Vector Search**: Hybrid search using `sentence-transformers` for semantic similarity.
*   **Context-Aware**: Answers questions strictly from the provided context (no hallucination).
*   **Cloud Native**: Zero local dependencies (no Ollama, no Neo4j required).

## 🚀 Deployment Guide

This app is designed to be deployed on **Streamlit Cloud** (Recommended), Render, or Railway.

### Option 1: Streamlit Cloud (Fastest & Free)

1.  **Fork/Push** this repository to your GitHub.
2.  Go to [share.streamlit.io](https://share.streamlit.io/).
3.  Click **New App** and select your repository.
4.  **Main file path**: `src/app.py`
5.  **Advanced Settings** -> **Secrets**:
    Copy the contents of your `.env` file into the Secrets text area TOML format:
    ```toml
    GROQ_API_KEY = "gsk_..."
    TIDB_HOST = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
    TIDB_PORT = 4000
    TIDB_USER = "..."
    TIDB_PASSWORD = "..."
    TIDB_DATABASE = "test"
    TIDB_CA_PATH = "" # Leave empty for cloud
    LLM_MODEL = "llama-3.1-8b-instant"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    ```
6.  Click **Deploy**! 🎈

### Option 2: Docker (Render/Railway)

1.  This repo includes a `Dockerfile`.
2.  Deploy to Render/Railway and set the **Environment Variables** (same as above) in their dashboard.
3.  **Command**: `streamlit run src/app.py`

## 🛠️ Local Development

1.  Clone repo.
2.  `pip install -r requirements.txt`
3.  Set up `.env` file.
4.  `streamlit run src/app.py`

## System Architecture
*   **Frontend**: Streamlit
*   **Orchestration**: LangGraph
*   **LLM**: Groq (Llama 3.1)
*   **Database**: TiDB Serverless (Vector + Graph)