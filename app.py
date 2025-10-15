from flask import Flask, render_template, jsonify, request
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import threading
import time
import schedule

app = Flask(__name__)

# Global variables for caching
cached_data = None
last_update = None
update_lock = threading.Lock()

def get_google_sheets_client():
    """Initialize Google Sheets client"""
    try:
        # Check if credentials file exists
        if not os.path.exists('credentials.json'):
            return None
        
        # Define the scope
        scope = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        
        # Load credentials
        creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"Error initializing Google Sheets client: {e}")
        return None

def fetch_sheet_data(sheet_url=None):
    """Fetch data from Google Sheets"""
    global cached_data, last_update
    
    try:
        client = get_google_sheets_client()
        if not client:
            return None
        
        # Use provided URL or default
        if not sheet_url:
            sheet_url = "https://docs.google.com/spreadsheets/d/1suvLm83Xlsx4k4h1KJqugFt0sh6dQn3Z47ugXr8lN5c/edit"
        
        # Extract sheet ID from URL
        sheet_id = sheet_url.split('/d/')[1].split('/')[0]
        
        # Open the spreadsheet
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1
        
        # Get all values
        data = worksheet.get_all_values()
        
        if not data:
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])
        
        # Clean and process data
        processed_data = process_campaign_data(df)
        
        with update_lock:
            cached_data = processed_data
            last_update = datetime.now()
        
        return processed_data
        
    except Exception as e:
        print(f"Error fetching sheet data: {e}")
        return None

def process_campaign_data(df):
    """Process and clean the campaign data"""
    try:
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Convert numeric columns
        numeric_columns = ['S.no', 'Total leads dialled', 'Total connnected calls']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Process campaign status
        df['Campaign Status'] = df['Campaign Status'].fillna('Unknown')
        
        # Count live campaigns
        live_campaigns = df[df['Campaign Status'].str.contains('Live', case=False, na=False)]
        
        # Process monitoring IDs
        df['Monitoring IDs'] = df['Monitoring'].fillna('')
        
        # Calculate metrics
        metrics = {
            'total_clients': len(df),
            'live_campaigns': len(live_campaigns),
            'total_leads_dialled': df['Total leads dialled'].sum() if 'Total leads dialled' in df.columns else 0,
            'total_connected_calls': df['Total connnected calls'].sum() if 'Total connnected calls' in df.columns else 0,
            'campaign_status_breakdown': df['Campaign Status'].value_counts().to_dict(),
            'application_status_breakdown': df['Application Status (Voice)'].value_counts().to_dict() if 'Application Status (Voice)' in df.columns else {},
            'last_updated': datetime.now().isoformat()
        }
        
        return {
            'raw_data': df.to_dict('records'),
            'metrics': metrics,
            'live_campaigns': live_campaigns.to_dict('records')
        }
        
    except Exception as e:
        print(f"Error processing data: {e}")
        return None

def auto_refresh():
    """Auto-refresh data every minute"""
    while True:
        try:
            fetch_sheet_data()
            print(f"Data refreshed at {datetime.now()}")
        except Exception as e:
            print(f"Error in auto-refresh: {e}")
        time.sleep(60)  # Wait 60 seconds

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/data')
def get_data():
    """API endpoint to get current data"""
    global cached_data, last_update
    
    with update_lock:
        if cached_data is None:
            # Try to fetch data if not cached
            fetch_sheet_data()
        
        return jsonify({
            'data': cached_data,
            'last_update': last_update.isoformat() if last_update else None,
            'status': 'success'
        })

@app.route('/api/refresh', methods=['POST'])
def manual_refresh():
    """Manual refresh endpoint"""
    data = request.get_json()
    sheet_url = data.get('sheet_url') if data else None
    
    result = fetch_sheet_data(sheet_url)
    
    if result:
        return jsonify({'status': 'success', 'message': 'Data refreshed successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to refresh data'})

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update sheet URL configuration"""
    data = request.get_json()
    sheet_url = data.get('sheet_url')
    
    if sheet_url:
        # Store the new URL (you might want to save this to a config file)
        result = fetch_sheet_data(sheet_url)
        if result:
            return jsonify({'status': 'success', 'message': 'Configuration updated successfully'})
    
    return jsonify({'status': 'error', 'message': 'Invalid sheet URL'})

if __name__ == '__main__':
    # Start auto-refresh thread
    refresh_thread = threading.Thread(target=auto_refresh, daemon=True)
    refresh_thread.start()
    
    # Initial data fetch
    fetch_sheet_data()
    
    app.run(debug=True, host='0.0.0.0', port=5000)



