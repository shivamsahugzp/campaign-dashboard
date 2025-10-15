# 🎯 Campaign Dashboard - Complete Setup & Usage Guide

## 🚀 Quick Start (5 Minutes)

### Option 1: Automated Setup
```bash
cd /Users/shivamsahu/Documents/Projects/campaign_dashboard
python3 quick_start.py
```

### Option 2: Manual Setup
```bash
cd /Users/shivamsahu/Documents/Projects/campaign_dashboard
./setup.sh
source venv/bin/activate
python app.py
```

## 📋 Prerequisites

### 1. Google Sheets API Setup
1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create/Select Project**
3. **Enable APIs:**
   - Google Sheets API
   - Google Drive API
4. **Create Service Account:**
   - IAM & Admin → Service Accounts → Create Service Account
   - Name: `campaign-dashboard-service`
   - Role: `Viewer`
5. **Generate Key:**
   - Click on service account → Keys → Add Key → Create new key → JSON
   - Download and rename to `credentials.json`
6. **Share Your Sheet:**
   - Open your Google Sheet
   - Click Share → Add service account email → Viewer access

### 2. Your Current Sheet
Your sheet URL: `https://docs.google.com/spreadsheets/d/1suvLm83Xlsx4k4h1KJqugFt0sh6dQn3Z47ugXr8lN5c/edit`

## 🎯 Dashboard Features

### 📊 Real-Time Metrics
- **Total Clients**: Count of all clients
- **Live Campaigns**: Active campaigns
- **Total Leads Dialled**: Sum of all leads
- **Connected Calls**: Successful connections

### 📈 Interactive Charts
- **Campaign Status Distribution**: Live/Posted/No File breakdown
- **Application Status**: Studio/Application/LLM-Studio distribution

### 📋 Live Campaigns Table
- Real-time view of all active campaigns
- Client details, bot names, schedules
- Status indicators with color coding

### ⚙️ Configuration Panel
- Change Google Sheets URL dynamically
- No need to restart the application
- Instant updates when URL changes

## 🔄 Auto-Refresh Features
- **Automatic**: Data refreshes every 60 seconds
- **Manual**: Click refresh button anytime
- **Visual**: Last update timestamp displayed
- **Background**: Updates happen without interrupting your work

## 📱 Access Your Dashboard

### Local Access
- **URL**: `http://localhost:5000`
- **Status**: Available only on your computer
- **Use Case**: Development and testing

### Network Access
- **URL**: `http://YOUR_IP:5000`
- **Status**: Available on your local network
- **Use Case**: Team access within office

### Production Deployment (Optional)
For production use, consider:
- **Heroku**: Easy cloud deployment
- **AWS/GCP**: Scalable cloud hosting
- **Docker**: Containerized deployment

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### 1. "Error initializing Google Sheets client"
**Solution:**
- Verify `credentials.json` exists and is valid
- Check service account has sheet access
- Ensure APIs are enabled in Google Cloud Console

#### 2. "Failed to fetch data"
**Solution:**
- Verify sheet is shared with service account
- Check sheet URL format
- Ensure sheet has data in expected columns

#### 3. Dashboard not loading
**Solution:**
- Check if port 5000 is available
- Verify all dependencies installed
- Check console for error messages

#### 4. Data not updating
**Solution:**
- Check internet connection
- Verify sheet permissions
- Try manual refresh button

## 📊 Understanding Your Data

### Expected Sheet Columns
Your dashboard expects these columns:
- `Client` - Client name
- `1st Campaign`, `2nd Campaign`, `3rd Campaign`, `4th Campaign` - Schedule times
- `Bot Name` - Bot identifier
- `Application Status (Voice)` - Studio/Application/LLM-Studio
- `Campaign Status` - Live/Posted/No File
- `Monitoring` - Monitoring IDs
- `Reports` - Report status
- `Total leads dialled` - Lead count
- `Total connnected calls` - Connection count

### Status Indicators
- 🟢 **Live**: Active campaigns
- 🟡 **Posted**: Scheduled campaigns
- 🔴 **No File**: Inactive campaigns

## 🔧 Advanced Configuration

### Custom Refresh Intervals
Edit `app.py` line 60:
```python
time.sleep(60)  # Change 60 to desired seconds
```

### Custom Port
Edit `app.py` last line:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change port number
```

### Multiple Sheets
The dashboard supports switching between different sheets using the configuration panel.

## 📈 Performance Tips

### For Large Datasets
- Consider pagination for tables
- Use data caching
- Implement data filtering

### For High Frequency Updates
- Adjust refresh interval
- Implement incremental updates
- Use WebSocket for real-time updates

## 🔒 Security Best Practices

### Credentials Management
- Never commit `credentials.json` to version control
- Use environment variables in production
- Regularly rotate service account keys

### Access Control
- Limit service account permissions
- Use principle of least privilege
- Monitor API usage

## 📞 Support

### Getting Help
1. Check this guide first
2. Review console error messages
3. Verify Google Sheets API setup
4. Test with sample data

### Common Commands
```bash
# Check if dashboard is running
curl http://localhost:5000/api/data

# View logs
tail -f app.log

# Restart dashboard
pkill -f "python app.py"
python app.py
```

## 🎉 Success!

Your dashboard is now ready! You should see:
- ✅ Real-time metrics updating
- ✅ Interactive charts
- ✅ Live campaigns table
- ✅ Auto-refresh every minute
- ✅ Configurable sheet URL

**Dashboard URL**: `http://localhost:5000`

Enjoy your new campaign monitoring dashboard! 🚀


