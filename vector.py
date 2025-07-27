from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd
import shutil

def reset_database():
    """Reset the vector database by deleting the existing one"""
    db_location = "./chrome_langchain_db"
    if os.path.exists(db_location):
        print(f"🗑️ Deleting existing database at {db_location}")
        shutil.rmtree(db_location)
        print("✅ Database deleted successfully")
    return db_location

def load_and_validate_csv():
    """Load and validate the CSV file"""
    try:
        df = pd.read_csv("realistic_restaurant_reviews.csv")
        print(f"📊 Loaded CSV with {len(df)} rows")
        print(f"📊 Columns: {list(df.columns)}")
        
        # Show sample data
        print("\n📝 Sample rows:")
        print(df.head(3).to_string())
        
        # Check for required columns (order doesn't matter)
        required_columns = ['Title', 'Review', 'Rating', 'Date']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            print(f"Available columns: {list(df.columns)}")
            return None
        
        # Check for empty data
        if df.empty:
            print("❌ CSV file is empty")
            return None
        
        # Check for null values in critical columns
        null_reviews = df['Review'].isnull().sum()
        if null_reviews > 0:
            print(f"⚠️ Found {null_reviews} null reviews, will skip these")
        
        return df
        
    except FileNotFoundError:
        print("❌ CSV file 'realistic_restaurant_reviews.csv' not found!")
        print("Please make sure the file exists in the current directory")
        return None
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return None

def create_documents_from_df(df):
    """Create documents from DataFrame with validation"""
    documents = []
    ids = []
    skipped = 0
    
    for i, row in df.iterrows():
        try:
            # Skip rows with missing review text
            if pd.isnull(row['Review']) or str(row['Review']).strip() == '':
                skipped += 1
                continue
            
            # Create content by combining title and review
            title = str(row['Title']).strip() if not pd.isnull(row['Title']) else ""
            review = str(row['Review']).strip()
            
            # Combine title and review
            if title:
                content = f"{title} {review}"
            else:
                content = review
            
            # Create document
            document = Document(
                page_content=content,
                metadata={
                    "rating": row["Rating"] if not pd.isnull(row["Rating"]) else 0,
                    "date": str(row["Date"]) if not pd.isnull(row["Date"]) else "",
                    "row_id": i,
                    "title": title,
                    "review": review
                },
                id=str(i)
            )
            
            documents.append(document)
            ids.append(str(i))
            
        except Exception as e:
            print(f"⚠️ Error processing row {i}: {e}")
            skipped += 1
            continue
    
    print(f"✅ Created {len(documents)} documents")
    if skipped > 0:
        print(f"⚠️ Skipped {skipped} rows due to missing/invalid data")
    
    return documents, ids

def initialize_embeddings():
    """Initialize embeddings with error handling"""
    try:
        print("🔧 Initializing embeddings...")
        embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        
        # Test the embeddings
        test_text = "This is a test"
        test_embedding = embeddings.embed_query(test_text)
        print(f"✅ Embeddings working! Dimension: {len(test_embedding)}")
        
        return embeddings
    except Exception as e:
        print(f"❌ Error initializing embeddings: {e}")
        print("Make sure Ollama is running and 'mxbai-embed-large' model is available")
        print("Run: ollama pull mxbai-embed-large")
        return None

def create_vector_store(embeddings, documents, ids, db_location):
    """Create vector store with error handling"""
    try:
        print("🔧 Creating vector store...")
        vector_store = Chroma(
            collection_name="restaurant_reviews",
            persist_directory=db_location,
            embedding_function=embeddings
        )
        
        if documents:
            print(f"📚 Adding {len(documents)} documents to vector store...")
            
            # Add documents in batches to avoid memory issues
            batch_size = 50
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]
                
                print(f"  Adding batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
                vector_store.add_documents(documents=batch_docs, ids=batch_ids)
            
            # Verify documents were added
            collection_count = vector_store._collection.count()
            print(f"✅ Vector store created! Collection count: {collection_count}")
            
            if collection_count == 0:
                print("❌ No documents were actually added to the vector store!")
                return None
            
        return vector_store
        
    except Exception as e:
        print(f"❌ Error creating vector store: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main initialization function"""
    print("🚀 Initializing Restaurant Review Vector Database")
    print("=" * 60)
    
    # Step 1: Reset database (force recreation)
    db_location = reset_database()
    
    # Step 2: Load and validate CSV
    df = load_and_validate_csv()
    if df is None:
        print("❌ Failed to load CSV data")
        return None, None, None
    
    # Step 3: Create documents
    documents, ids = create_documents_from_df(df)
    if not documents:
        print("❌ No valid documents created")
        return None, None, None
    
    # Step 4: Initialize embeddings
    embeddings = initialize_embeddings()
    if embeddings is None:
        return None, None, None
    
    # Step 5: Create vector store
    vector_store = create_vector_store(embeddings, documents, ids, db_location)
    if vector_store is None:
        return None, None, None
    
    # Step 6: Create retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    
    # Step 7: Test retriever
    print("\n🧪 Testing retriever...")
    try:
        test_results = retriever.invoke("food")
        print(f"✅ Retriever test successful: Found {len(test_results)} results")
        
        if test_results:
            print("📄 Sample result:")
            print(f"  Content: {test_results[0].page_content[:100]}...")
            print(f"  Metadata: {test_results[0].metadata}")
        
    except Exception as e:
        print(f"❌ Retriever test failed: {e}")
        return None, None, None
    
    print("\n" + "=" * 60)
    print("🎉 Vector database initialization complete!")
    
    return retriever, vector_store, df

# Initialize everything
retriever, vector_store, df = main()

# Export components (only if initialization was successful)
if retriever is not None:
    __all__ = ['retriever', 'vector_store', 'df']
    print("✅ All components exported successfully")
else:
    print("❌ Initialization failed - components not available")
    retriever = None
    vector_store = None
    df = None
