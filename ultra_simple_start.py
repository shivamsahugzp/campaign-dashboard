#!/usr/bin/env python3
"""
Ultra Simple Campaign Dashboard - No Setup Required!
Just run this and paste your Google Sheets URL
"""

import subprocess
import sys
import os
import webbrowser
import time
import threading

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'simple_requirements.txt'])
        print("✅ Packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def start_dashboard():
    """Start the dashboard"""
    print("🚀 Starting Campaign Dashboard...")
    print("📱 Dashboard will open at: http://localhost:5000")
    print("🔄 Auto-refresh enabled (every minute)")
    print("📋 Just paste your Google Sheets URL and you're ready!")
    print("-" * 60)
    
    # Open browser after delay
    def open_browser():
        time.sleep(3)
        webbrowser.open('http://localhost:5000')
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        subprocess.run([sys.executable, 'simple_app.py'])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")

def main():
    """Main function"""
    print("🎯 Ultra Simple Campaign Dashboard")
    print("=" * 40)
    print("✨ No API keys needed!")
    print("✨ No complex setup!")
    print("✨ Just paste your Google Sheets URL!")
    print("=" * 40)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed. Please check your Python installation.")
        return
    
    print("\n🎉 Ready to start!")
    print("📋 Make sure your Google Sheet is publicly viewable:")
    print("   1. Open your Google Sheet")
    print("   2. Click 'Share' button")
    print("   3. Set to 'Anyone with the link can view'")
    print("   4. Copy the URL")
    
    input("\nPress Enter to start the dashboard...")
    
    # Start dashboard
    start_dashboard()

if __name__ == "__main__":
    main()


