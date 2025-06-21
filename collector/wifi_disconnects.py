#!/usr/bin/env python3
from datetime import datetime, timedelta
import subprocess
import re
import json

def get_disconnect_events(since_minutes=15):
    time_since = (datetime.now() - timedelta(minutes=since_minutes)).isoformat()
    predicate = 'eventMessage CONTAINS "WiFi" OR eventMessage CONTAINS "AirPort" OR eventMessage CONTAINS "en0"'

    try:
        output = subprocess.check_output([
            'log', 'show', '--info',
            '--style', 'syslog',
            '--predicate', predicate,
            '--start', time_since,
            '--last', f'{since_minutes}m'
        ], stderr=subprocess.DEVNULL, text=True)

        disconnect_events = []
        for line in output.splitlines():
            if any(word in line.lower() for word in ['disconnect', 'disassociated', 'link down']):
                match = re.match(r'^(\d{4}-\d{2}-\d{2}.*?)\s+(.*)', line)
                if match:
                    timestamp, message = match.groups()
                    disconnect_events.append({
                        "timestamp": timestamp.strip(),
                        "message": message.strip()
                    })
        return disconnect_events
    except subprocess.CalledProcessError:
        return [{"error": "Log access failed. Try running with sudo?"}]

if __name__ == "__main__":
    events = get_disconnect_events()
    print(json.dumps(events, indent=2))
