#!/bin/bash

# Campaign Dashboard Setup Script

echo "🚀 Setting up Campaign Dashboard..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if credentials.json exists
if [ ! -f "credentials.json" ]; then
    echo "⚠️  credentials.json not found!"
    echo "📋 Please follow these steps:"
    echo "1. Go to Google Cloud Console (https://console.cloud.google.com/)"
    echo "2. Create a new project or select existing one"
    echo "3. Enable Google Sheets API and Google Drive API"
    echo "4. Create a Service Account and download JSON key"
    echo "5. Rename the downloaded file to 'credentials.json'"
    echo "6. Place it in this directory"
    echo "7. Share your Google Sheet with the service account email"
    echo ""
    echo "📄 Example credentials.json format saved as 'credentials.json.example'"
    echo "🔄 Run this script again after setting up credentials"
    exit 1
fi

echo "✅ Setup complete!"
echo ""
echo "🎯 To start the dashboard:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the app: python app.py"
echo "3. Open browser: http://localhost:5000"
echo ""
echo "📖 For detailed instructions, see README.md"


