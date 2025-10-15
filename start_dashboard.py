#!/usr/bin/env python3
import webbrowser
import time
import threading
from no_pandas_app import app

def open_browser():
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

print('🚀 Campaign Dashboard Starting...')
print('📱 Dashboard URL: http://localhost:5000')
print('🔄 Auto-refresh: Every minute')
print('📋 Your Google Sheets data is loading...')

browser_thread = threading.Thread(target=open_browser)
browser_thread.daemon = True
browser_thread.start()

app.run(debug=False, host='0.0.0.0', port=5000)


