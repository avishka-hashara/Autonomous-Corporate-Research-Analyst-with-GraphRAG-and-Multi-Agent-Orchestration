import streamlit as st
import sys
import os
import time

# Ensure src is in python path
sys.path.append(os.path.dirname(__file__))

# Import the compiled graph
try:
    from graph_agent import app as agent_app
except ImportError:
    # Fallback for running from project root
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from src.graph_agent import app as agent_app

# Import custom styles
try:
    from ui_styles import apply_custom_css, render_header
except ImportError:
    # Fallback if ui_styles is not found (shouldn't happen if structure is correct)
    def apply_custom_css(): pass
    def render_header(): st.title("🤖 Corporate Analyst Agent")

# --- Page Config ---
st.set_page_config(page_title="Corporate Analyst Agent", page_icon="🤖", layout="wide")

# Apply Custom CSS
apply_custom_css()

# Render Custom Header
render_header()

# --- System Check ---
def check_system_health():
    """Checks if Neo4j and Ollama are reachable."""
    health_status = []
    
    # Check TiDB
    try:
        from tidb_store import TiDBGraph
        graph = TiDBGraph()
        conn = graph.get_connection()
        if conn.is_connected():
            health_status.append(("TiDB", "Connected", "✅"))
            conn.close()
        else:
            health_status.append(("TiDB", "Disconnected", "❌"))
    except Exception as e:
        health_status.append(("TiDB", f"Error: {e}", "❌"))

    # Check Embeddings Model (HuggingFace)
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        from config import EMBEDDING_MODEL
        if EMBEDDING_MODEL:
            health_status.append(("Embeddings (HF)", "Ready", "✅"))
        else:
             health_status.append(("Embeddings", "Config Missing", "⚠️"))
    except Exception as e:
         health_status.append(("Embeddings", f"Error: {e}", "❌"))

    # Check Groq (for LLM)
    try:
        from config import LLM_MODEL
        import os
        if os.getenv("GROQ_API_KEY"):
            health_status.append(("Groq (LLM)", "Ready", "✅"))
        else:
             health_status.append(("Groq", "Missing API Key", "❌"))
    except Exception:
        health_status.append(("Groq", "Error", "❌"))

    return health_status

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/company.png", width=150) # Placeholder or local asset
    st.markdown("### 📊 Analyst Dashboard")
    
    # System Health in Sidebar (Mini)
    with st.expander("System Status", expanded=False):
        for service, status_text, icon in check_system_health():
            st.markdown(f"**{service}**: {status_text} {icon}")

    st.markdown("---")
    st.header("📂 Data Ingestion")
    uploaded_file = st.file_uploader("Upload Company Report (PDF)", type="pdf")
    
    if uploaded_file is not None:
        if st.button("🚀 Process Document", type="primary"):
            status_container = st.empty()
            
            def update_status(msg):
                status_container.info(msg)

            with st.status("Processing Document...", expanded=True) as status:
                try:
                    # 1. Save file locally
                    os.makedirs("data/uploaded", exist_ok=True)
                    file_path = os.path.join("data/uploaded", uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.write(f"✅ File saved: `{uploaded_file.name}`")

                    # 2. Trigger Ingestion
                    # Import here to avoid early errors
                    from ingest import process_document
                    from vector_store import ingest_vectors

                    st.write("⚙️ Ingesting Vectors...")
                    ingest_vectors(file_path, status_callback=lambda m: st.write(f"vectors: {m}"))
                    st.write("✅ Vectors Index Updated")

                    st.write("🕸️ Extracting Knowledge Graph (Llama3)...")
                    process_document(file_path, status_callback=lambda m: st.write(f"graph: {m}")) 
                    st.write("✅ Knowledge Graph Updated")
                    
                    status.update(label="Processing Complete!", state="complete", expanded=False)
                    st.balloons()
                    
                except Exception as e:
                    status.update(label="Processing Failed", state="error")
                    st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("###### Powered by LangGraph & TiDB")

    # Document Selector
    try:
        from manage_data import list_documents
        available_docs = list_documents()
        if available_docs:
            st.markdown("### 📂 Filter Context")
            selected_docs = st.multiselect(
                "Select documents to search:",
                options=available_docs,
                default=[],
                help="If empty, searches all documents.",
                key="selected_docs" 
            )
    except Exception as e:
        st.error(f"Error loading docs: {e}")


# --- Main Layout with Tabs ---
tab1, tab2 = st.tabs(["💬 Analyst Chat", "🗂️ Knowledge Base"])

with tab1:
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        role = message["role"]
        avatar = "🤖" if role == "assistant" else "👤"
        with st.chat_message(role, avatar=avatar):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask about company strategy, risks, or market position..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat message container
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            status_placeholder = st.empty()
            full_response = ""
            
            with status_placeholder.status("Thinking...", expanded=True) as status:
                try:
                    # Get selected documents from sidebar if any
                    # We need to move the list_documents logical call here or use session state if the sidebar one isn't accessible
                    # Ideally, we should capture the selection from the sidebar.
                    
                    # BUT: The sidebar code runs before this. We need to store the selection in a variable.
                    # Since st.multiselect returns the list, let's grab it from session state or a variable if we refactor.
                    # EASIER: Just place the multiselect inside the sidebar block and store in session_state, OR re-read the widget here?
                    # Streamlit widgets return values. We need to capture the sidebar return value.
                    pass 
                    
                    inputs = {
                        "question": prompt,
                        "selected_sources": st.session_state.get("selected_docs", [])
                    }
                    # Placeholder for graph visualization (future)
                    
                    for output in agent_app.stream(inputs):
                        for key, value in output.items():
                            if key == "supervisor":
                                status.write(f"📋 **Supervisor**: Planning step {value.get('attempts', 1)}")
                            elif key == "vector_search":
                                status.write(f"🔍 **Vector Search**: Found relevant documents")
                            elif key == "graph_search":
                                status.write(f"🕸️ **Graph Search**: Querying knowledge graph")
                            elif key == "generator":
                                status.write("✍️ **Generator**: Drafting response...")
                                if "answer" in value:
                                    full_response = value["answer"]
                            elif key == "reviewer":
                                status.write("⚖️ **Reviewer**: Validating answer...")
                    
                    status.update(label="Complete", state="complete", expanded=False)
                    
                    if full_response:
                        message_placeholder.markdown(full_response)
                    else:
                        message_placeholder.error("Failed to generate a response.")
                        full_response = "I'm sorry, I couldn't generate a response."
                        
                except Exception as e:
                    status.update(label="Error", state="error")
                    st.error(f"An error occurred: {str(e)}")
                    full_response = f"An error occurred: {str(e)}"

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

with tab2:
    st.header("🗂️ Managed Resources")
    
    try:
        from manage_data import list_documents, delete_document
        
        docs = list_documents()
        
        if not docs:
            st.info("No documents uploaded yet.", icon="ℹ️")
        else:
            # Using a container for better spacing
            with st.container():
                st.write(f"**{len(docs)}** Documents in the Knowledge Base")
                
                # Header row
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.markdown("**Filename**")
                c2.markdown("**Format**")
                c3.markdown("**Action**")
                st.divider()

                for doc in docs:
                    c1, c2, c3 = st.columns([3, 1, 1])
                    c1.write(f"📄 {doc}")
                    c2.write("PDF") # Assuming PDF for now
                    
                    if c3.button("🗑️ Delete", key=f"del_{doc}"):
                        with st.spinner(f"Deleting {doc}..."):
                            res = delete_document(doc)
                            if res['disk'] or res['vector'] or res['graph']:
                                st.toast(f"Deleted {doc}", icon="✅")
                            else:
                                st.toast(f"Could not delete {doc}", icon="⚠️")
                        time.sleep(1) # Give time for toast
                        st.rerun()
                    
                    st.divider()
                        
    except ImportError:
        st.error("Could not import manage_data module. Please check installation.")
