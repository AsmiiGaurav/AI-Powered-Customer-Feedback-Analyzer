"""
Setup script for sentiment analysis model
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies for sentiment analysis"""
    print("🔧 Setting up Sentiment Analysis Model")
    print("=" * 40)
    
    # List of required packages
    packages = [
        'vaderSentiment',
        'textblob',
        'transformers',
        'torch',
        'numpy',
        'scikit-learn',
        'langdetect'
    ]
    
    print("Installing required packages...")
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
    
    print("\n🎯 Testing sentiment analysis...")
    
    # Test the installation
    try:
        # Add venv folder to Python path
        venv_path = os.path.join(os.path.dirname(__file__), 'venv')
        if venv_path not in sys.path:
            sys.path.append(venv_path)
        
        from multilingual_sentiment import analyze_sentiment
        
        # Test basic functionality
        test_result = analyze_sentiment("This is a great restaurant!")
        print(f"✅ Test successful: {test_result['label']} sentiment detected")
        
        print("\n🚀 Sentiment analysis model is ready to use!")
        print("\nYou can now:")
        print("1. Run your Streamlit app: streamlit run app_multilingual2.py")
        print("2. Test the model: python sentiment_demo.py")
        print("3. Run full tests: python test_sentiment.py")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("The model will use fallback methods.")

if __name__ == "__main__":
    install_dependencies()
