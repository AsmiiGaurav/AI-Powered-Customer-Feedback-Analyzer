#!/usr/bin/env python3
"""
Setup script for multilingual support in Restaurant Review Analysis app
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages for multilingual support"""
    print("🔧 Installing multilingual dependencies...")
    
    try:
        # Install from requirements file
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_multilingual.txt"
        ])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_existing_files():
    """Check if required files exist"""
    required_files = [
        'venv/main.py',
        'venv/vector.py',
        'venv/sentiment.py',
        'realistic_restaurant_reviews.csv'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("⚠️  Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found!")
    return True

def create_backup():
    """Create backup of original app.py"""
    if os.path.exists('app.py'):
        try:
            import shutil
            shutil.copy2('app.py', 'app_original_backup.py')
            print("✅ Created backup of original app.py as app_original_backup.py")
        except Exception as e:
            print(f"⚠️  Could not create backup: {e}")

def main():
    """Main setup function"""
    print("🌍 Setting up Multilingual Support for Restaurant Review Analysis")
    print("=" * 70)
    
    # Check existing files
    if not check_existing_files():
        print("\n❌ Setup cannot continue due to missing files.")
        print("Please ensure you have the original project files in place.")
        return
    
    # Create backup
    create_backup()
    
    # Install dependencies
    if not install_requirements():
        print("\n❌ Setup failed during dependency installation.")
        return
    
    print("\n🎉 Multilingual setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Run the multilingual app: streamlit run app_multilingual.py")
    print("2. Select your preferred language from the sidebar")
    print("3. Ask questions in any supported language!")
    
    print("\n🌍 Supported Languages:")
    languages = [
        "🇺🇸 English", "🇪🇸 Español", "🇫🇷 Français", "🇩🇪 Deutsch",
        "🇮🇹 Italiano", "🇵🇹 Português", "🇷🇺 Русский", "🇯🇵 日本語",
        "🇰🇷 한국어", "🇨🇳 中文", "🇸🇦 العربية", "🇮🇳 हिन्दी",
        "🇳🇱 Nederlands", "🇸🇪 Svenska", "🇩🇰 Dansk", "🇳🇴 Norsk",
        "🇫🇮 Suomi", "🇵🇱 Polski", "🇹🇷 Türkçe", "🇹🇭 ไทย"
    ]
    
    for i, lang in enumerate(languages, 1):
        print(f"   {lang}", end="")
        if i % 4 == 0:
            print()
        else:
            print("  ", end="")
    
    print("\n\n💡 Features:")
    print("   • Automatic language detection for user input")
    print("   • Real-time translation of questions and responses")
    print("   • Multilingual sentiment analysis")
    print("   • Localized UI elements")
    print("   • Right-to-left (RTL) support for Arabic")
    
    print("\n🚀 Ready to go! Run: streamlit run app_multilingual.py")

if __name__ == "__main__":
    main()
