#!/usr/bin/env python3
"""
Campaign Dashboard - Quick Start Script
This script helps you get the dashboard running quickly
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ is required")
        return False
    
    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("⚠️  credentials.json not found!")
        print("📋 Please set up Google Sheets API credentials first:")
        print("1. Go to Google Cloud Console")
        print("2. Create a Service Account")
        print("3. Download JSON key as 'credentials.json'")
        print("4. Share your Google Sheet with the service account")
        return False
    
    print("✅ All requirements met!")
    return True

def install_dependencies():
    """Install required packages"""
    print("📚 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def start_dashboard():
    """Start the dashboard"""
    print("🚀 Starting dashboard...")
    print("📱 Dashboard will be available at: http://localhost:5000")
    print("🔄 Auto-refresh is enabled (every minute)")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:5000')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start the Flask app
        subprocess.run([sys.executable, 'app.py'])
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

def main():
    """Main function"""
    print("🎯 Campaign Dashboard - Quick Start")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Setup incomplete. Please fix the issues above.")
        return
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        return
    
    print("\n🎉 Ready to start!")
    input("Press Enter to start the dashboard...")
    
    # Start dashboard
    start_dashboard()

if __name__ == "__main__":
    main()


