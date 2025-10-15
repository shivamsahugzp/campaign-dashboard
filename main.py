#!/usr/bin/env python3
"""
Campaign Dashboard - Main Application Entry Point
================================================

A comprehensive real-time dashboard for monitoring Google Sheets data with
advanced analytics, automated reporting, and interactive visualizations.

Author: Shivam Sahu
GitHub: https://github.com/shivamsahugzp/campaign-dashboard
"""

import os
import sys
import logging
from pathlib import Path
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
from datetime import datetime, timedelta
import threading
import time
import schedule
from typing import Dict, List, Optional, Any
import asyncio
from dataclasses import dataclass
import hashlib
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('campaign_dashboard.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DashboardConfig:
    """Configuration class for dashboard settings"""
    refresh_interval: int = 60  # seconds
    max_cache_age: int = 300   # seconds
    enable_auto_refresh: bool = True
    debug_mode: bool = False
    port: int = 5000
    host: str = '0.0.0.0'

class CampaignDashboard:
    """Main dashboard application class"""
    
    def __init__(self, config: DashboardConfig = None):
        self.config = config or DashboardConfig()
        self.app = Flask(__name__)
        self.app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
        
        # Enable CORS for API endpoints
        CORS(self.app, resources={
            r"/api/*": {"origins": "*"},
            r"/static/*": {"origins": "*"}
        })
        
        # Global variables for caching
        self.cached_data = None
        self.last_update = None
        self.update_lock = threading.Lock()
        self.sheet_client = None
        
        # Initialize Google Sheets client
        self._initialize_sheets_client()
        
        # Setup routes
        self._setup_routes()
        
        # Start background scheduler
        if self.config.enable_auto_refresh:
            self._start_scheduler()
    
    def _initialize_sheets_client(self):
        """Initialize Google Sheets client with error handling"""
        try:
            credentials_path = Path('credentials.json')
            if not credentials_path.exists():
                logger.warning("credentials.json not found. Using demo mode.")
                return None
            
            scope = [
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
            
            creds = Credentials.from_service_account_file(
                str(credentials_path), 
                scopes=scope
            )
            self.sheet_client = gspread.authorize(creds)
            logger.info("Google Sheets client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {e}")
            self.sheet_client = None
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template('dashboard.html')
        
        @self.app.route('/api/data')
        def api_data():
            """API endpoint for dashboard data"""
            try:
                sheet_url = request.args.get('sheet_url')
                data = self._fetch_sheet_data(sheet_url)
                
                if data is None:
                    return jsonify({
                        'error': 'Unable to fetch data. Check credentials and sheet URL.',
                        'demo_mode': self.sheet_client is None
                    }), 500
                
                return jsonify({
                    'data': data,
                    'last_update': self.last_update.isoformat() if self.last_update else None,
                    'cache_age': self._get_cache_age(),
                    'status': 'success'
                })
                
            except Exception as e:
                logger.error(f"API error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/health')
        def api_health():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'sheets_connected': self.sheet_client is not None,
                'cache_age': self._get_cache_age()
            })
        
        @self.app.route('/api/config')
        def api_config():
            """Configuration endpoint"""
            return jsonify({
                'refresh_interval': self.config.refresh_interval,
                'max_cache_age': self.config.max_cache_age,
                'enable_auto_refresh': self.config.enable_auto_refresh,
                'debug_mode': self.config.debug_mode
            })
        
        @self.app.route('/demo')
        def demo():
            """Demo page with sample data"""
            return render_template('demo.html')
        
        @self.app.route('/api/demo-data')
        def api_demo_data():
            """Demo data endpoint"""
            demo_data = self._generate_demo_data()
            return jsonify({
                'data': demo_data,
                'last_update': datetime.now().isoformat(),
                'demo_mode': True
            })
    
    def _fetch_sheet_data(self, sheet_url: str = None) -> Optional[Dict[str, Any]]:
        """Fetch data from Google Sheets with caching"""
        with self.update_lock:
            # Check cache validity
            if (self.cached_data and self.last_update and 
                self._get_cache_age() < self.config.max_cache_age):
                return self.cached_data
            
            try:
                if not self.sheet_client:
                    logger.warning("No Google Sheets client available")
                    return None
                
                # Use provided URL or default demo sheet
                if not sheet_url:
                    sheet_url = os.environ.get('DEFAULT_SHEET_URL', 
                        'https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit')
                
                # Extract sheet ID from URL
                sheet_id = self._extract_sheet_id(sheet_url)
                if not sheet_id:
                    logger.error(f"Invalid sheet URL: {sheet_url}")
                    return None
                
                # Open spreadsheet
                spreadsheet = self.sheet_client.open_by_key(sheet_id)
                worksheet = spreadsheet.sheet1
                
                # Get all records
                records = worksheet.get_all_records()
                
                if not records:
                    logger.warning("No data found in sheet")
                    return None
                
                # Convert to DataFrame for processing
                df = pd.DataFrame(records)
                
                # Process and structure data
                processed_data = self._process_dataframe(df)
                
                # Update cache
                self.cached_data = processed_data
                self.last_update = datetime.now()
                
                logger.info(f"Successfully fetched {len(records)} records")
                return processed_data
                
            except Exception as e:
                logger.error(f"Error fetching sheet data: {e}")
                return None
    
    def _extract_sheet_id(self, url: str) -> Optional[str]:
        """Extract sheet ID from Google Sheets URL"""
        try:
            if '/d/' in url:
                return url.split('/d/')[1].split('/')[0]
            return None
        except Exception:
            return None
    
    def _process_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Process DataFrame into dashboard-ready format"""
        try:
            # Basic statistics
            stats = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'data_types': df.dtypes.to_dict()
            }
            
            # Numeric columns analysis
            numeric_cols = df.select_dtypes(include=['number']).columns
            numeric_stats = {}
            for col in numeric_cols:
                numeric_stats[col] = {
                    'sum': float(df[col].sum()),
                    'mean': float(df[col].mean()),
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'std': float(df[col].std())
                }
            
            # Sample data for display
            sample_data = df.head(100).to_dict('records')
            
            return {
                'stats': stats,
                'numeric_stats': numeric_stats,
                'sample_data': sample_data,
                'raw_data': df.to_dict('records'),
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing dataframe: {e}")
            return {'error': str(e)}
    
    def _generate_demo_data(self) -> Dict[str, Any]:
        """Generate demo data for testing"""
        import random
        
        # Generate sample campaign data
        campaigns = []
        for i in range(50):
            campaigns.append({
                'campaign_id': f'CAMP_{i+1:03d}',
                'campaign_name': f'Campaign {i+1}',
                'impressions': random.randint(1000, 100000),
                'clicks': random.randint(50, 5000),
                'conversions': random.randint(5, 500),
                'cost': round(random.uniform(100, 10000), 2),
                'revenue': round(random.uniform(200, 20000), 2),
                'date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
            })
        
        df = pd.DataFrame(campaigns)
        return self._process_dataframe(df)
    
    def _get_cache_age(self) -> int:
        """Get cache age in seconds"""
        if not self.last_update:
            return float('inf')
        return int((datetime.now() - self.last_update).total_seconds())
    
    def _start_scheduler(self):
        """Start background scheduler for auto-refresh"""
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(1)
        
        # Schedule data refresh
        schedule.every(self.config.refresh_interval).seconds.do(
            lambda: self._fetch_sheet_data()
        )
        
        # Start scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info(f"Scheduler started with {self.config.refresh_interval}s interval")
    
    def run(self):
        """Run the dashboard application"""
        logger.info(f"Starting Campaign Dashboard on {self.config.host}:{self.config.port}")
        self.app.run(
            host=self.config.host,
            port=self.config.port,
            debug=self.config.debug_mode,
            threaded=True
        )

def main():
    """Main entry point"""
    # Load configuration from environment
    config = DashboardConfig(
        refresh_interval=int(os.environ.get('REFRESH_INTERVAL', 60)),
        max_cache_age=int(os.environ.get('MAX_CACHE_AGE', 300)),
        enable_auto_refresh=os.environ.get('ENABLE_AUTO_REFRESH', 'true').lower() == 'true',
        debug_mode=os.environ.get('DEBUG_MODE', 'false').lower() == 'true',
        port=int(os.environ.get('PORT', 5000)),
        host=os.environ.get('HOST', '0.0.0.0')
    )
    
    # Create and run dashboard
    dashboard = CampaignDashboard(config)
    dashboard.run()

if __name__ == '__main__':
    main()
