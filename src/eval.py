import os
import json
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
from datasets import Dataset
from langchain_ollama import ChatOllama, OllamaEmbeddings
from graph_agent import app # Import the agent

# 1. Setup
langchain_llm = ChatOllama(model="llama3", temperature=0)
langchain_embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Ragas expects specific column names: question, answer, contexts, ground_truth
# We will create a small Golden Dataset here or load it.

golden_dataset = [
    {
        "question": "What is the strategic focus regarding AI?",
        "ground_truth": " The company is focusing on autonomous agents and knowledge graphs to improve corporate research."
    },
    {
        "question": "Who is the CEO?",
        "ground_truth": "Sarah Connor is the CEO."
    }
]

def run_evaluation():
    print("Starting Evaluation Run...")
    
    questions = []
    answers = []
    contexts = []
    ground_truths = []
    
    for item in golden_dataset:
        q = item["question"]
        print(f"Evaluating: {q}")
        
        # Run Agent
        inputs = {"question": q}
        output = app.invoke(inputs)
        
        ans = output.get("answer", "No answer")
        docs = output.get("documents", [])
        
        questions.append(q)
        answers.append(ans)
        contexts.append(docs)
        ground_truths.append(item["ground_truth"])
        
    # Create Dataset
    data = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }
    dataset = Dataset.from_dict(data)
    
    # Run Ragas
    print("Calculating Metrics...")
    results = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ],
        llm=langchain_llm,
        embeddings=langchain_embeddings
    )
    
    print("\n=== Evaluation Results ===")
    print(results)
    
    # Save results
    df = results.to_pandas()
    df.to_csv("evaluation_results.csv", index=False)
    print("Results saved to evaluation_results.csv")

if __name__ == "__main__":
    run_evaluation()
