#!/usr/bin/env python3
"""
Quick test to check Google Sheets access
"""
import requests

def test_sheet_access():
    sheet_url = "https://docs.google.com/spreadsheets/d/1suvLm83Xlsx4k4h1KJqugFt0sh6dQn3Z47ugXr8lN5c/edit"
    
    # Extract sheet ID
    sheet_id = sheet_url.split('/spreadsheets/d/')[1].split('/')[0]
    
    # Create CSV export URL
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=475146199"
    
    print(f"🔍 Testing access to your Google Sheet...")
    print(f"📋 Sheet ID: {sheet_id}")
    print(f"🔗 CSV URL: {csv_url}")
    
    try:
        response = requests.get(csv_url, timeout=10)
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Your sheet is accessible!")
            print("📱 Your dashboard should work now!")
            print("🌐 Open: http://localhost:5000")
        else:
            print("❌ FAILED! Your sheet is not publicly accessible.")
            print("🔧 To fix this:")
            print("   1. Open your Google Sheet")
            print("   2. Click 'Share' button")
            print("   3. Set to 'Anyone with the link can view'")
            print("   4. Save and try again")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("🔧 Make sure your sheet is publicly viewable!")

if __name__ == "__main__":
    test_sheet_access()
