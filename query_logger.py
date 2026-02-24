"""
Query logging utility for analytics dashboard
"""

import json
import os
from datetime import datetime

LOG_FILE = "data/query_logs.json"


def log_query(farmer_name: str, location: str, query: str, query_type: str):
    """Log a farmer query for analytics."""
    os.makedirs("data", exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "farmer_name": farmer_name or "Anonymous",
        "location": location or "Unknown",
        "query": query[:200],  # Truncate long queries
        "type": query_type,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(entry)
        
        # Keep last 1000 logs
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"Logging error: {e}")


def get_logs() -> list:
    """Get all query logs."""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []
