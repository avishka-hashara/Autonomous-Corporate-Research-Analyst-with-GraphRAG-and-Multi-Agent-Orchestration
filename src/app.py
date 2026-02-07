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

# --- File Upload Section ---
with st.sidebar:
    st.header("📂 Document Upload")
    uploaded_file = st.file_uploader("Upload a PDF report", type="pdf")
    
    if uploaded_file is not None:
        if st.button("Process Document"):
            with st.spinner("Processing document... This may take a while."):
                # 1. Save file locally
                os.makedirs("data/uploaded", exist_ok=True)
                file_path = os.path.join("data/uploaded", uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"File saved to {file_path}")

                # 2. Trigger Ingestion
                try:
                    # Import here to avoid circular dependencies if any, or just for cleanliness
                    from ingest import process_document
                    from vector_store import ingest_vectors

                    st.info("Starting Vector Ingestion (Fast)...")
                    ingest_vectors(file_path)
                    st.success("Vector Index Updated!")

                    st.info("Starting Graph Extraction (Slow - Llama3)...")
                    process_document(file_path) # This prints to stdout, we won't see it in UI easily without redirecting
                    st.success("Knowledge Graph Updated!")
                    
                except Exception as e:
                    st.error(f"Error during processing: {e}")


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
