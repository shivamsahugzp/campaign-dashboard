from flask import Flask, render_template, jsonify, request
import requests
import json
import csv
from datetime import datetime, timedelta
import threading
import time
import re
from io import StringIO
import calendar

app = Flask(__name__)

# Global variables for caching
cached_data = None
last_update = None
current_sheet_url = None
update_lock = threading.Lock()

def extract_sheet_id_from_url(url):
    """Extract sheet ID from Google Sheets URL"""
    try:
        # Handle different URL formats
        if '/spreadsheets/d/' in url:
            sheet_id = url.split('/spreadsheets/d/')[1].split('/')[0]
        elif 'id=' in url:
            sheet_id = url.split('id=')[1].split('&')[0]
        else:
            return None
        return sheet_id
    except:
        return None

def get_csv_url_from_sheet_url(sheet_url):
    """Convert Google Sheets URL to CSV export URL"""
    sheet_id = extract_sheet_id_from_url(sheet_url)
    if not sheet_id:
        return None
    
    # Get the gid (sheet tab) from URL
    gid = '475146199'  # Default to your specific sheet tab
    if 'gid=' in sheet_url:
        gid = sheet_url.split('gid=')[1].split('#')[0].split('&')[0]
    
    # Create CSV export URL
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    return csv_url

def fetch_sheet_data(sheet_url=None):
    """Fetch data from Google Sheets via CSV export"""
    global cached_data, last_update, current_sheet_url
    
    try:
        if not sheet_url:
            sheet_url = "https://docs.google.com/spreadsheets/d/1suvLm83Xlsx4k4h1KJqugFt0sh6dQn3Z47ugXr8lN5c/edit"
        
        current_sheet_url = sheet_url
        csv_url = get_csv_url_from_sheet_url(sheet_url)
        
        if not csv_url:
            return None
        
        # Fetch CSV data
        response = requests.get(csv_url, timeout=30)
        response.raise_for_status()
        
        # Parse CSV
        csv_data = StringIO(response.text)
        reader = csv.DictReader(csv_data)
        data = list(reader)
        
        if not data:
            return None
        
        # Process data
        processed_data = process_campaign_data(data)
        
        with update_lock:
            cached_data = processed_data
            last_update = datetime.now()
        
        return processed_data
        
    except Exception as e:
        print(f"Error fetching sheet data: {e}")
        return None

def process_campaign_data(data):
    """Process and clean the campaign data with comprehensive analytics"""
    try:
        # Initialize counters and analytics
        live_campaigns = []
        total_leads = 0
        total_calls = 0
        
        # Comprehensive analytics
        campaign_times = []
        bot_types = {}
        reporting_cms = {}
        client_status = {}
        hourly_distribution = {}
        daily_distribution = {}
        performance_metrics = {}
        client_performance = {}
        cm_performance = {}
        bot_performance = {}
        
        # Time analysis
        time_patterns = {
            'morning': 0,    # 6-12
            'afternoon': 0,  # 12-18
            'evening': 0,    # 18-24
            'night': 0       # 0-6
        }
        
        # Status tracking
        status_trends = {
            'Live': 0,
            'Posted': 0,
            'No File': 0,
            'Unknown': 0
        }
        
        for row in data:
            # Count live campaigns
            campaign_status = row.get('Campaign Status', '').strip()
            if 'Live' in campaign_status:
                live_campaigns.append(row)
            
            # Sum numeric values
            try:
                leads = row.get('Total leads dialled', '0').replace(',', '')
                if leads and leads.isdigit():
                    total_leads += int(leads)
            except:
                pass
            
            try:
                calls = row.get('Total connnected calls', '0').replace(',', '')
                if calls and calls.isdigit():
                    total_calls += int(calls)
            except:
                pass
            
            # Client analysis
            client = row.get('Client', '').strip()
            if client:
                client_status[client] = campaign_status
                
                # Client performance tracking
                if client not in client_performance:
                    client_performance[client] = {
                        'total_campaigns': 0,
                        'live_campaigns': 0,
                        'leads': 0,
                        'calls': 0,
                        'success_rate': 0
                    }
                
                client_performance[client]['total_campaigns'] += 1
                if 'Live' in campaign_status:
                    client_performance[client]['live_campaigns'] += 1
                
                try:
                    leads = row.get('Total leads dialled', '0').replace(',', '')
                    calls = row.get('Total connnected calls', '0').replace(',', '')
                    if leads and leads.isdigit():
                        client_performance[client]['leads'] += int(leads)
                    if calls and calls.isdigit():
                        client_performance[client]['calls'] += int(calls)
                except:
                    pass
            
            # Bot type analysis
            bot_name = row.get('Bot Name', '').strip()
            if bot_name:
                if 'LLM' in bot_name:
                    bot_types['LLM'] = bot_types.get('LLM', 0) + 1
                elif 'Studio' in bot_name:
                    bot_types['Studio'] = bot_types.get('Studio', 0) + 1
                elif 'SMS' in bot_name:
                    bot_types['SMS'] = bot_types.get('SMS', 0) + 1
                else:
                    bot_types['Other'] = bot_types.get('Other', 0) + 1
                
                # Bot performance tracking
                if bot_name not in bot_performance:
                    bot_performance[bot_name] = {
                        'total_campaigns': 0,
                        'live_campaigns': 0,
                        'leads': 0,
                        'calls': 0
                    }
                
                bot_performance[bot_name]['total_campaigns'] += 1
                if 'Live' in campaign_status:
                    bot_performance[bot_name]['live_campaigns'] += 1
                
                try:
                    leads = row.get('Total leads dialled', '0').replace(',', '')
                    calls = row.get('Total connnected calls', '0').replace(',', '')
                    if leads and leads.isdigit():
                        bot_performance[bot_name]['leads'] += int(leads)
                    if calls and calls.isdigit():
                        bot_performance[bot_name]['calls'] += int(calls)
                except:
                    pass
            
            # Reporting CM analysis
            cm = row.get(' reporting CM', '').strip()
            if cm:
                reporting_cms[cm] = reporting_cms.get(cm, 0) + 1
                
                # CM performance tracking
                if cm not in cm_performance:
                    cm_performance[cm] = {
                        'total_campaigns': 0,
                        'live_campaigns': 0,
                        'leads': 0,
                        'calls': 0
                    }
                
                cm_performance[cm]['total_campaigns'] += 1
                if 'Live' in campaign_status:
                    cm_performance[cm]['live_campaigns'] += 1
                
                try:
                    leads = row.get('Total leads dialled', '0').replace(',', '')
                    calls = row.get('Total connnected calls', '0').replace(',', '')
                    if leads and leads.isdigit():
                        cm_performance[cm]['leads'] += int(leads)
                    if calls and calls.isdigit():
                        cm_performance[cm]['calls'] += int(calls)
                except:
                    pass
            
            # Time analysis
            for i in range(1, 5):
                time_key = f'{i}st Campaign' if i == 1 else f'{i}nd Campaign' if i == 2 else f'{i}rd Campaign' if i == 3 else f'{i}th Campaign'
                time_val = row.get(time_key, '').strip()
                if time_val and time_val != 'None' and 'No Specific time' not in time_val:
                    campaign_times.append(time_val)
                    
                    # Extract hour for distribution
                    if 'AM' in time_val or 'PM' in time_val:
                        hour_match = re.search(r'(\d+):', time_val)
                        if hour_match:
                            hour = int(hour_match.group(1))
                            if 'PM' in time_val and hour != 12:
                                hour += 12
                            elif 'AM' in time_val and hour == 12:
                                hour = 0
                            
                            hourly_distribution[f"{hour:02d}:00"] = hourly_distribution.get(f"{hour:02d}:00", 0) + 1
                            
                            # Time pattern analysis
                            if 6 <= hour < 12:
                                time_patterns['morning'] += 1
                            elif 12 <= hour < 18:
                                time_patterns['afternoon'] += 1
                            elif 18 <= hour < 24:
                                time_patterns['evening'] += 1
                            else:
                                time_patterns['night'] += 1
            
            # Status trends
            if campaign_status in status_trends:
                status_trends[campaign_status] += 1
            else:
                status_trends['Unknown'] += 1
        
        # Calculate status breakdowns
        campaign_status_counts = {}
        app_status_counts = {}
        
        for row in data:
            # Campaign status breakdown
            status = row.get('Campaign Status', 'Unknown').strip()
            campaign_status_counts[status] = campaign_status_counts.get(status, 0) + 1
            
            # Application status breakdown
            app_status = row.get('Application Status (Voice)', 'Unknown').strip()
            app_status_counts[app_status] = app_status_counts.get(app_status, 0) + 1
        
        # Calculate success rates
        success_rate = (total_calls / total_leads * 100) if total_leads > 0 else 0
        
        # Calculate performance metrics
        performance_metrics = {
            'total_campaigns': len(data),
            'live_campaigns': len(live_campaigns),
            'inactive_campaigns': len(data) - len(live_campaigns),
            'campaign_utilization': (len(live_campaigns) / len(data) * 100) if len(data) > 0 else 0,
            'lead_conversion_rate': success_rate,
            'avg_leads_per_campaign': total_leads / len(data) if len(data) > 0 else 0,
            'avg_calls_per_campaign': total_calls / len(data) if len(data) > 0 else 0
        }
        
        # Calculate comprehensive metrics
        metrics = {
            'total_clients': len(data),
            'live_campaigns': len(live_campaigns),
            'total_leads_dialled': total_leads,
            'total_connected_calls': total_calls,
            'success_rate': round(success_rate, 2),
            'campaign_status_breakdown': campaign_status_counts,
            'application_status_breakdown': app_status_counts,
            'bot_types_breakdown': bot_types,
            'reporting_cms_breakdown': reporting_cms,
            'hourly_distribution': hourly_distribution,
            'time_patterns': time_patterns,
            'status_trends': status_trends,
            'client_status': client_status,
            'performance_metrics': performance_metrics,
            'client_performance': client_performance,
            'cm_performance': cm_performance,
            'bot_performance': bot_performance,
            'last_updated': datetime.now().isoformat(),
            'sheet_url': current_sheet_url
        }
        
        return {
            'raw_data': data,
            'metrics': metrics,
            'live_campaigns': live_campaigns,
            'analytics': {
                'campaign_times': campaign_times,
                'bot_types': bot_types,
                'reporting_cms': reporting_cms,
                'hourly_distribution': hourly_distribution,
                'time_patterns': time_patterns,
                'client_performance': client_performance,
                'cm_performance': cm_performance,
                'bot_performance': bot_performance
            }
        }
        
    except Exception as e:
        print(f"Error processing data: {e}")
        return None

def auto_refresh():
    """Auto-refresh data every minute"""
    while True:
        try:
            fetch_sheet_data(current_sheet_url)
            print(f"Data refreshed at {datetime.now()}")
        except Exception as e:
            print(f"Error in auto-refresh: {e}")
        time.sleep(60)  # Wait 60 seconds

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('comprehensive_dashboard.html')

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
        return jsonify({'status': 'error', 'message': 'Failed to refresh data. Please check your sheet URL and sharing settings.'})

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update sheet URL configuration"""
    data = request.get_json()
    sheet_url = data.get('sheet_url')
    
    if sheet_url:
        result = fetch_sheet_data(sheet_url)
        if result:
            return jsonify({'status': 'success', 'message': 'Configuration updated successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to access the sheet. Please ensure the sheet is publicly viewable or shared correctly.'})
    
    return jsonify({'status': 'error', 'message': 'Invalid sheet URL'})

@app.route('/api/export')
def export_data():
    """Export data as CSV"""
    global cached_data
    
    with update_lock:
        if cached_data and cached_data.get('raw_data'):
            # Create CSV response
            from flask import Response
            
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=cached_data['raw_data'][0].keys())
            writer.writeheader()
            writer.writerows(cached_data['raw_data'])
            
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=campaign_data.csv'}
            )
    
    return jsonify({'status': 'error', 'message': 'No data available to export'})

if __name__ == '__main__':
    # Start auto-refresh thread
    refresh_thread = threading.Thread(target=auto_refresh, daemon=True)
    refresh_thread.start()
    
    # Initial data fetch
    fetch_sheet_data()
    
    print("🚀 Comprehensive Campaign Dashboard Started!")
    print("📱 Access your dashboard at: http://localhost:5000")
    print("🔄 Auto-refresh enabled (every minute)")
    print("📊 Advanced analytics and comprehensive insights enabled!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)


