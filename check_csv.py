import pandas as pd
import os

def check_csv_file():
    """Check if the CSV file exists and has the correct format"""
    filename = "realistic_restaurant_reviews.csv"
    
    print("🔍 Checking CSV file...")
    print("=" * 50)
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"❌ File '{filename}' not found!")
        print("Current directory contents:")
        for file in os.listdir("."):
            if file.endswith(".csv"):
                print(f"  📄 {file}")
        return False
    
    try:
        # Load the CSV
        df = pd.read_csv(filename)
        
        print(f"✅ File found: {filename}")
        print(f"📊 Shape: {df.shape} (rows, columns)")
        print(f"📊 Columns: {list(df.columns)}")
        
        # Check required columns
        required_columns = ['Title', 'Review', 'Rating', 'Date']
        missing_columns = []
        
        for col in required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            print("Expected columns: Title, Review, Rating, Date")
            return False
        
        # Check data quality
        print("\n📈 Data Quality Check:")
        print(f"  Total rows: {len(df)}")
        
        # Check for null values
        for col in required_columns:
            null_count = df[col].isnull().sum()
            print(f"  {col} - Null values: {null_count}")
        
        # Check review text length
        review_lengths = df['Review'].str.len()
        print(f"  Review lengths - Min: {review_lengths.min()}, Max: {review_lengths.max()}, Avg: {review_lengths.mean():.1f}")
        
        # Show sample data
        print("\n📝 Sample Data (first 3 rows):")
        print("-" * 50)
        for i, row in df.head(3).iterrows():
            print(f"Row {i+1}:")
            print(f"  Title: {row['Title']}")
            print(f"  Review: {str(row['Review'])[:100]}{'...' if len(str(row['Review'])) > 100 else ''}")
            print(f"  Rating: {row['Rating']}")
            print(f"  Date: {row['Date']}")
            print()
        
        # Check for empty reviews
        empty_reviews = df['Review'].isnull().sum() + (df['Review'] == '').sum()
        if empty_reviews > 0:
            print(f"⚠️ Warning: {empty_reviews} empty reviews found")
        
        print("✅ CSV file looks good!")
        return True
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False

if __name__ == "__main__":
    check_csv_file()