import os
import sys

# Add src to path if running from root
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from graph_agent import app

def test_agent():
    print("Testing Agent with Question: 'What is the strategy?'")
    inputs = {"question": "What is the strategy?", "attempts": 0}
    
    try:
        for output in app.stream(inputs):
            for key, value in output.items():
                print(f"Finished running: {key}")
                if key == 'generator':
                     print(f"Answer: {value.get('answer')}")
                if key == 'reviewer':
                     print(f"Critique: {value.get('critique')}")
    except Exception as e:
        print(f"Agent Error: {e}")

if __name__ == "__main__":
    test_agent()
