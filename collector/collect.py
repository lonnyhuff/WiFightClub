#!/usr/bin/env python3
import subprocess
import json
from datetime import datetime
from pathlib import Path
import re

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def get_wifi_stats():
    try:
        result = subprocess.run(
            ["sudo", "wdutil", "info"],
            capture_output=True,
            text=True,
            timeout=5
        )
        output = result.stdout
        wifi_info = {}

        patterns = {
            "ssid": r"SSID\s+:\s+(.+)",
            "rssi": r"RSSI\s+:\s+(-?\d+)\s*dBm",
            "tx_rate": r"Tx Rate\s+:\s+([\d\.]+)\s*Mbps",
            "noise": r"Noise\s+:\s+(-?\d+)\s*dBm",
            "channel": r"Channel\s+:\s+([^\s]+)"
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, output)
            if match:
                value = match.group(1).strip()
                if key in ["rssi", "noise"]:
                    wifi_info[key] = int(value)
                elif key == "tx_rate":
                    wifi_info[key] = float(value)
                else:
                    wifi_info[key] = value

        return wifi_info if wifi_info else {"error": "No fields matched."}

    except Exception as e:
        return {"error": f"Failed to run wdutil: {str(e)}"}

def get_ping_stats():
    try:
        result = subprocess.run(
            ["ping", "-c", "100", "-i", "0.1", "8.8.8.8"],
            capture_output=True,
            text=True,
            timeout=20
        )
        summary = result.stdout

        # Extract packet loss and latency info
        loss_match = re.search(r'(\d+(\.\d+)?)% packet loss', summary)
        rtt_match = re.search(r'round-trip.*= ([\d\.]+)/([\d\.]+)/([\d\.]+)/', summary)

        if loss_match and rtt_match:
            loss = float(loss_match.group(1))
            avg_latency = float(rtt_match.group(2))
            return {
                "packet_loss_percent": loss,
                "avg_latency_ms": avg_latency
            }

        return {"error": "Failed to parse ping output"}
    except Exception as e:
        return {"error": f"Ping failed: {str(e)}"}

def collect_data():
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "wifi_stats": get_wifi_stats(),
        "ping_stats": get_ping_stats()
    }

def save_log(data):
    filename = f"log_{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    path = DATA_DIR / filename
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved diagnostics to {path}")

if __name__ == "__main__":
    save_log(collect_data())
