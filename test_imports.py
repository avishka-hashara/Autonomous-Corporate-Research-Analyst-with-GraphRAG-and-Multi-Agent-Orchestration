import sys
try:
    import langchain
    print(f"LangChain Version: {langchain.__version__}")
    print(f"LangChain Path: {langchain.__file__}")
except ImportError:
    print("LangChain not installed")

try:
    from langchain.chains import GraphCypherQAChain
    print("GraphCypherQAChain found in langchain.chains")
except ImportError as e:
    print(f"GraphCypherQAChain NOT found in langchain.chains: {e}")

try:
    from langchain_community.chains import GraphCypherQAChain
    print("GraphCypherQAChain found in langchain_community.chains")
except ImportError as e:
    print(f"GraphCypherQAChain NOT found in langchain_community.chains: {e}")

try:
    from langchain.chains import RetrievalQA
    print("RetrievalQA found in langchain.chains")
except ImportError as e:
    print(f"RetrievalQA NOT found in langchain.chains: {e}")
