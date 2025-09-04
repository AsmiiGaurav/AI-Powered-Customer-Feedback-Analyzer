from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd
import shutil

# Global variables to store components
vector_store = None
embeddings = None
df = None

def reset_database():
    """Reset the vector database by deleting the existing one"""
    db_location = os.path.join(os.path.dirname(__file__), '..', 'chrome_langchain_db')
    if os.path.exists(db_location):
        print(f"🗑️ Deleting existing database at {db_location}")
        shutil.rmtree(db_location)
        print("✅ Database deleted successfully")
    return db_location

def load_and_validate_csv():
    """Load and validate the CSV file - prioritizes reviews.csv"""
    try:
        # Priority order: reviews.csv > combined > expanded > original
        csv_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'reviews.csv'),
            os.path.join(os.path.dirname(__file__), '..', 'combined_restaurant_reviews.csv'),
            os.path.join(os.path.dirname(__file__), '..', 'expanded_restaurant_reviews.csv'),
            os.path.join(os.path.dirname(__file__), '..', 'realistic_restaurant_reviews.csv')
        ]
        
        df = None
        csv_path = None
        
        for path in csv_paths:
            if os.path.exists(path):
                df = pd.read_csv(path)
                csv_path = path
                break
        
        if df is None:
            print("❌ No CSV file found!")
            print("Looking for: reviews.csv, combined_restaurant_reviews.csv, expanded_restaurant_reviews.csv, or realistic_restaurant_reviews.csv")
            return None
            
        filename = os.path.basename(csv_path)
        print(f"📊 Loaded CSV from {filename} with {len(df)} rows")
        print(f"📊 Columns: {list(df.columns)}")
        
        # Show sample data
        print("\n📝 Sample rows:")
        print(df.head(3).to_string())
        
        # Check for required columns
        required_columns = ['Title', 'Review', 'Rating', 'Date']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            print(f"Available columns: {list(df.columns)}")
            return None
        
        # Check if this is multi-restaurant format
        if 'restaurant_name' in df.columns:
            print("🏢 Multi-restaurant format detected!")
            restaurant_counts = df['restaurant_name'].value_counts()
            print(f"📊 Restaurant distribution:")
            for restaurant, count in restaurant_counts.items():
                avg_rating = df[df['restaurant_name'] == restaurant]['Rating'].mean()
                print(f"   🍽️ {restaurant}: {count} reviews (avg: {avg_rating:.1f}⭐)")
                
            # Show dataset composition based on filename
            if filename == 'reviews.csv':
                print(f"\n📈 Reviews dataset statistics:")
                print(f"   Total restaurants: {df['restaurant_name'].nunique()}")
                print(f"   Average reviews per restaurant: {len(df) / df['restaurant_name'].nunique():.1f}")
                print(f"   Overall average rating: {df['Rating'].mean():.1f}⭐")
            elif filename == 'combined_restaurant_reviews.csv':
                print(f"\n📈 Combined dataset statistics:")
                print(f"   Total restaurants: {df['restaurant_name'].nunique()}")
                print(f"   Average reviews per restaurant: {len(df) / df['restaurant_name'].nunique():.1f}")
                print(f"   Overall average rating: {df['Rating'].mean():.1f}⭐")
        else:
            print("📝 Single restaurant format detected")
        
        # Data quality checks
        if df.empty:
            print("❌ CSV file is empty")
            return None
        
        null_reviews = df['Review'].isnull().sum()
        if null_reviews > 0:
            print(f"⚠️ Found {null_reviews} null reviews, will skip these")
        
        print(f"✅ CSV validation completed - dataset ready for processing")
        return df
        
    except FileNotFoundError:
        print("❌ CSV file not found!")
        print("Please make sure one of these files exists:")
        print("  - reviews.csv (recommended)")
        print("  - combined_restaurant_reviews.csv")
        print("  - expanded_restaurant_reviews.csv") 
        print("  - realistic_restaurant_reviews.csv")
        return None
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return None

def create_documents_from_df(df):
    """Create documents from DataFrame with multi-restaurant support"""
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
            
            # Create metadata - include restaurant info if available
            metadata = {
                "rating": row["Rating"] if not pd.isnull(row["Rating"]) else 0,
                "date": str(row["Date"]) if not pd.isnull(row["Date"]) else "",
                "row_id": i,
                "title": title,
                "review": review
            }
            
            # Add restaurant-specific metadata if available
            if 'restaurant_name' in row:
                metadata["restaurant_name"] = str(row["restaurant_name"]).strip()
            if 'cuisine_type' in row:
                metadata["cuisine_type"] = str(row["cuisine_type"]).strip()
            if 'location' in row:
                metadata["location"] = str(row["location"]).strip()
            
            # Add any other columns as metadata
            for col in df.columns:
                if col not in ['Title', 'Review', 'Rating', 'Date', 'restaurant_name', 'cuisine_type', 'location']:
                    metadata[col.lower()] = str(row[col]) if not pd.isnull(row[col]) else ""
            
            # Create document
            document = Document(
                page_content=content,
                metadata=metadata,
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
    global embeddings
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
    global vector_store
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

def get_restaurant_retriever(restaurant_name, k=5):
    """Get a retriever filtered for a specific restaurant"""
    global vector_store
    if vector_store is None:
        print("❌ Vector store not initialized")
        return None
    
    try:
        # Create filtered retriever
        retriever = vector_store.as_retriever(
            search_kwargs={
                "k": k,
                "filter": {"restaurant_name": restaurant_name}
            }
        )
        print(f"✅ Created restaurant-specific retriever for: {restaurant_name}")
        return retriever
    except Exception as e:
        print(f"❌ Error creating restaurant retriever: {e}")
        return None

def get_available_restaurants():
    """Get list of all restaurants in the database"""
    global vector_store
    if vector_store is None:
        print("❌ Vector store not initialized")
        return []
    
    try:
        # Get all documents and extract unique restaurant names
        all_docs = vector_store.get()
        restaurants = set()
        
        for metadata in all_docs['metadatas']:
            restaurant_name = metadata.get('restaurant_name')
            if restaurant_name and restaurant_name.strip() != '' and restaurant_name != 'Unknown':
                restaurants.add(restaurant_name)
        
        restaurant_list = sorted(list(restaurants))
        if restaurant_list:
            print(f"✅ Found {len(restaurant_list)} restaurants: {restaurant_list}")
        return restaurant_list
        
    except Exception as e:
        print(f"❌ Error getting restaurant list: {e}")
        return []

def search_by_restaurant(restaurant_name, query, k=5):
    """Search reviews for a specific restaurant"""
    restaurant_retriever = get_restaurant_retriever(restaurant_name, k)
    if restaurant_retriever is None:
        return []
    
    try:
        results = restaurant_retriever.invoke(query)
        print(f"🔍 Found {len(results)} results for '{restaurant_name}' with query: '{query}'")
        return results
    except Exception as e:
        print(f"❌ Error searching for restaurant: {e}")
        return []

def get_restaurant_info(restaurant_name):
    """Get detailed info about a specific restaurant"""
    global vector_store
    if vector_store is None:
        return None
        
    try:
        # Get all documents for this restaurant
        all_docs = vector_store.get(where={"restaurant_name": restaurant_name})
        
        if not all_docs['metadatas']:
            return None
            
        # Extract info from first document
        first_metadata = all_docs['metadatas'][0]
        
        # Calculate statistics
        ratings = [m.get('rating', 0) for m in all_docs['metadatas'] if m.get('rating', 0) > 0]
        
        info = {
            'name': restaurant_name,
            'cuisine_type': first_metadata.get('cuisine_type', 'Unknown'),
            'location': first_metadata.get('location', 'Unknown'),
            'total_reviews': len(all_docs['metadatas']),
            'average_rating': sum(ratings) / len(ratings) if ratings else 0,
            'rating_distribution': {}
        }
        
        # Calculate rating distribution
        for rating in ratings:
            info['rating_distribution'][rating] = info['rating_distribution'].get(rating, 0) + 1
            
        return info
        
    except Exception as e:
        print(f"❌ Error getting restaurant info: {e}")
        return None

def main():
    """Main initialization function"""
    global vector_store, df
    
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
    
    # Step 6: Create retriever (general - searches all restaurants)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    
    # Step 7: Test retriever
    print("\n🧪 Testing retriever...")
    try:
        test_results = retriever.invoke("food quality")
        print(f"✅ Retriever test successful: Found {len(test_results)} results")
        
        if test_results:
            print("📄 Sample result:")
            result = test_results[0]
            print(f"  Content: {result.page_content[:100]}...")
            print(f"  Metadata: {result.metadata}")
            
            # Show restaurant name if available
            restaurant_name = result.metadata.get('restaurant_name', 'N/A')
            print(f"  Restaurant: {restaurant_name}")
        
    except Exception as e:
        print(f"❌ Retriever test failed: {e}")
        return None, None, None
    
    # Step 8: Test restaurant-specific functionality (if multi-restaurant format)
    if 'restaurant_name' in df.columns:
        print("\n🧪 Testing restaurant-specific search...")
        restaurants = get_available_restaurants()
        if restaurants:
            test_restaurant = restaurants[0]
            test_results = search_by_restaurant(test_restaurant, "food", k=3)
            if test_results:
                print(f"✅ Restaurant-specific search working for: {test_restaurant}")
                
                # Show restaurant info
                restaurant_info = get_restaurant_info(test_restaurant)
                if restaurant_info:
                    print(f"   📊 {restaurant_info['name']}: {restaurant_info['total_reviews']} reviews, avg {restaurant_info['average_rating']:.1f}⭐")
            else:
                print(f"⚠️ No results found for restaurant-specific search")
    
    print("\n" + "=" * 60)
    print("🎉 Vector database initialization complete!")
    print("✅ Available functions:")
    print("   - retriever: General search across all reviews")
    print("   - get_restaurant_retriever(name): Restaurant-specific search")
    print("   - get_available_restaurants(): List all restaurants")
    print("   - search_by_restaurant(name, query): Direct restaurant search")
    print("   - get_restaurant_info(name): Get restaurant statistics")
    
    return retriever, vector_store, df

# Initialize everything
if __name__ == "__main__":
    retriever, vector_store, df = main()

# For import usage - only initialize if not already done
if vector_store is None:
    retriever, vector_store, df = main()

# Export components (only if initialization was successful)
if retriever is not None:
    __all__ = ['retriever', 'vector_store', 'df', 'get_restaurant_retriever', 'get_available_restaurants', 
               'search_by_restaurant', 'get_restaurant_info']
    print("✅ All components exported successfully")
else:
    print("❌ Initialization failed - components not available")
    retriever = None
    vector_store = None
    df = None