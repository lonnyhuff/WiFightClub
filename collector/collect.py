#!/usr/bin/env python3
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import re

def get_disconnect_events(minutes=15):
    time_since = (datetime.now() - timedelta(minutes=minutes)).isoformat()
    predicate = 'eventMessage CONTAINS "en0" OR eventMessage CONTAINS "WiFi"'
    try:
        output = subprocess.check_output([
            'log', 'show', '--style', 'syslog',
            '--predicate', predicate,
            '--start', time_since,
            '--last', f'{minutes}m'
        ], stderr=subprocess.DEVNULL, text=True)

        disconnects = []
        for line in output.splitlines():
            if re.search(r'disconnect|nw_flow_disconnected|link down|flow:disconnect', line, re.IGNORECASE):
                match = re.match(r'^(\d{4}-\d{2}-\d{2}.*?)\s+(.*)', line)
                if match:
                    timestamp, message = match.groups()
                    disconnects.append({
                        "timestamp": timestamp.strip(),
                        "message": message.strip()
                    })
        return disconnects
    except subprocess.CalledProcessError:
        return [{"error": "log command failed (permissions or SIP)"}]

def collect_data():
    timestamp = datetime.now().isoformat()
    wifi_signal = -55  # placeholder for real RSSI
    ping_stats = {
        "packet_loss_percent": 0.0,
        "avg_latency_ms": 7.0
    }
    disconnects = get_disconnect_events()
    return {
        "timestamp": timestamp,
        "wifi_signal": wifi_signal,
        "ping_stats": ping_stats,
        "disconnect_events": disconnects
    }

if __name__ == "__main__":
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(data_dir / f"log_{ts}.json", "w") as f:
        json.dump(collect_data(), f, indent=2)
