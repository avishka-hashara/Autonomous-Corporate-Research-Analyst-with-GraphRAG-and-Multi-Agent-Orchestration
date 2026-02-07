import streamlit as st
import sys
import os

# Ensure src is in python path
sys.path.append(os.path.dirname(__file__))

# Import the compiled graph
try:
    from graph_agent import app as agent_app
except ImportError:
    # Fallback for running from project root
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from src.graph_agent import app as agent_app

st.set_page_config(page_title="Corporate Analyst Agent", layout="wide")

st.title("🤖 Corporate Analyst Agent")
st.markdown("Ask questions about company strategy, risks, and structure. I can search documents and the knowledge graph.")

# --- System Check ---
def check_system_health():
    """Checks if Neo4j and Ollama are reachable."""
    health_status = []
    
    # Check Neo4j
    try:
        from neo4j import GraphDatabase
        from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        driver.verify_connectivity()
        health_status.append("✅ Neo4j Connected")
    except Exception:
        health_status.append("❌ Neo4j Disconnected (Check Docker)")

    # Check Ollama
    try:
        import requests
        from config import OLLAMA_BASE_URL
        res = requests.get(f"{OLLAMA_BASE_URL}")
        if res.status_code == 200:
            health_status.append("✅ Ollama Connected")
        else:
             health_status.append("⚠️ Ollama Reachable but returned error")
    except Exception:
         health_status.append("❌ Ollama Disconnected (Check Local Server)")
         
    return health_status

with st.expander("System Health Checks"):
    for status in check_system_health():
        st.write(status)

# --- File Upload Section ---
with st.sidebar:
    st.header("📂 Document Upload")
    uploaded_file = st.file_uploader("Upload a PDF report", type="pdf")
    
    if uploaded_file is not None:
        if st.button("Process Document"):
            status_container = st.empty()
            
            def update_status(msg):
                status_container.info(msg)

            with st.spinner("Processing document... This may take a while."):
                # 1. Save file locally
                os.makedirs("data/uploaded", exist_ok=True)
                file_path = os.path.join("data/uploaded", uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"File saved to {file_path}")

                # 2. Trigger Ingestion
                try:
                    # Import here
                    from ingest import process_document
                    from vector_store import ingest_vectors

                    update_status("Starting Vector Ingestion (Fast)...")
                    ingest_vectors(file_path, status_callback=update_status)
                    st.success("Vector Index Updated!")

                    update_status("Starting Graph Extraction (Slow - Llama3)...")
                    process_document(file_path, status_callback=update_status) 
                    st.success("Knowledge Graph Updated!")
                    
                except Exception as e:
                    st.error(f"Error during processing: {e}")


# --- Main Layout with Tabs ---
tab1, tab2 = st.tabs(["💬 Chat", "🗂️ Manage Resources"])

with tab1:
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            status_placeholder = st.empty()
            full_response = ""
            
            with status_placeholder.status("Thinking...", expanded=True) as status:
                try:
                    inputs = {"question": prompt}
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
            st.info("No documents uploaded yet.")
        else:
            st.markdown(f"Found **{len(docs)}** documents.")
            
            for doc in docs:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📄 **{doc}**")
                with col2:
                    if st.button("Delete", key=f"del_{doc}", type="primary"):
                        with st.spinner(f"Deleting {doc}..."):
                            res = delete_document(doc)
                            if res['disk']:
                                st.success(f"Deleted {doc} from disk.")
                            else:
                                st.warning(f"Could not delete {doc} from disk (maybe already gone).")
                                
                            if res['vector']:
                                st.success(f"Removed vectors for {doc}.")
                            
                            if res['graph']:
                                st.success(f"Removed graph nodes for {doc}.")
                                
                        st.rerun()
                        
    except ImportError:
        st.error("Could not import manage_data module. Please check installation.")

