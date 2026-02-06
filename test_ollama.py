import ollama
import sys

print("Testing Ollama with llama3...")
try:
    response = ollama.chat(model='llama3', messages=[
      {'role': 'user', 'content': 'Hello! Are you working?'}
    ])
    print("Response received:")
    print(response['message']['content'])
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
