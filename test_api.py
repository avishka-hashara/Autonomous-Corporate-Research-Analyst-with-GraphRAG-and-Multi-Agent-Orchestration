from langchain_community.chat_models import ChatOllama

# Connect to the local Llama 3 model
llm = ChatOllama(model="llama3", base_url="http://127.0.0.1:11434", temperature=0)

print("Testing Local Llama 3...")

try:
    # Ask a test question
    response = llm.invoke("Explain the concept of a 'Knowledge Graph' in one sentence.")
    print("\nSUCCESS! Model response:")
    print(response.content)
except Exception as e:
    print("\nERROR:")
    print(e)