#!/usr/bin/env python3

import sys
import traceback

def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print("✅ Ollama is running")
            print("Available models:")
            for model in models:
                print(f"  - {model['name']}")
            
            # Check if embedding model exists
            embedding_models = [m for m in models if 'mxbai-embed-large' in m['name']]
            if embedding_models:
                print("✅ mxbai-embed-large model found")
                return True
            else:
                print("❌ mxbai-embed-large model not found")
                print("Run: ollama pull mxbai-embed-large")
                return False
        else:
            print(f"❌ Ollama responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("Make sure Ollama is running with: ollama serve")
        return False

def test_langchain_ollama():
    """Test LangChain Ollama integration"""
    try:
        from langchain_ollama import OllamaEmbeddings
        print("\n🔧 Testing LangChain Ollama embeddings...")
        
        embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        
        # Test embedding a simple text
        test_text = "This is a test review about pizza"
        print(f"Testing text: '{test_text}'")
        
        embedding = embeddings.embed_query(test_text)
        print(f"✅ Embedding successful! Dimension: {len(embedding)}")
        print(f"Sample values: {embedding[:5]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ LangChain Ollama test failed: {e}")
        traceback.print_exc()
        return False

def test_chroma_basic():
    """Test basic Chroma functionality"""
    try:
        from langchain_chroma import Chroma
        from langchain_core.documents import Document
        from langchain_ollama import OllamaEmbeddings
        import tempfile
        import shutil
        
        print("\n🔧 Testing Chroma database creation...")
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        print(f"Using temporary directory: {temp_dir}")
        
        try:
            # Initialize embeddings
            embeddings = OllamaEmbeddings(model="mxbai-embed-large")
            
            # Create test documents
            test_docs = [
                Document(page_content="Great pizza with excellent service", metadata={"rating": 5}),
                Document(page_content="Bad food and terrible atmosphere", metadata={"rating": 1}),
                Document(page_content="Average restaurant with okay food", metadata={"rating": 3})
            ]
            
            # Create vector store
            vector_store = Chroma(
                collection_name="test_reviews",
                persist_directory=temp_dir,
                embedding_function=embeddings
            )
            
            # Add documents
            vector_store.add_documents(test_docs)
            
            # Check count
            count = vector_store._collection.count()
            print(f"✅ Added {count} documents to test database")
            
            # Test search
            results = vector_store.similarity_search("good pizza", k=2)
            print(f"✅ Search successful! Found {len(results)} results")
            
            if results:
                print(f"Sample result: {results[0].page_content}")
            
            return True
            
        finally:
            # Clean up
            shutil.rmtree(temp_dir)
            print("🧹 Cleaned up temporary directory")
            
    except Exception as e:
        print(f"❌ Chroma test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Ollama + LangChain + Chroma Setup")
    print("=" * 60)
    
    # Test 1: Ollama connection
    if not test_ollama_connection():
        print("\n❌ Ollama test failed. Fix Ollama setup first.")
        return
    
    # Test 2: LangChain integration
    if not test_langchain_ollama():
        print("\n❌ LangChain integration failed. Check your installation.")
        return
    
    # Test 3: Chroma integration
    if not test_chroma_basic():
        print("\n❌ Chroma integration failed. Check your installation.")
        return
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed! Your setup should work.")
    print("Now run the fixed vector.py to create your database.")

if __name__ == "__main__":
    main()