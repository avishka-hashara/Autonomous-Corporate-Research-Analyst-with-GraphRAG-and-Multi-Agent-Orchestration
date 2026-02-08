import os
from dotenv import load_dotenv

# Load environment variables once
load_dotenv()

# TiDB Configuration
# TiDB Configuration
TIDB_HOST = os.getenv("TIDB_HOST", "127.0.0.1").strip()
TIDB_PORT = int(os.getenv("TIDB_PORT", "4000"))
TIDB_USER = os.getenv("TIDB_USER", "root").strip()
TIDB_PASSWORD = os.getenv("TIDB_PASSWORD", "").strip()
TIDB_DATABASE = os.getenv("TIDB_DATABASE", "test").strip()
TIDB_CA_PATH = os.getenv("TIDB_CA_PATH", "").strip()

print(f"DEBUG CONFIG: Host={TIDB_HOST}, Port={TIDB_PORT}, User={TIDB_USER}")

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
# OLLAMA_BASE_URL removed as we are using Cloud LLM (Groq) and Local Embeddings (FastEmbed)

# Data Configuration
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "uploaded")
