import json
import os
from datetime import datetime

# Path to audit log file
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), '../data/audit_logs.json')

def add_audit_log(action, user):
    # Try loading existing logs
    try:
        with open(LOG_FILE_PATH, 'r') as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    # New log entry
    log_entry = {
        "id": len(logs) + 1,
        "action": action,
        "user": user,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    logs.append(log_entry)

    # Save updated logs
    with open(LOG_FILE_PATH, 'w') as file:
        json.dump(logs, file, indent=4)
