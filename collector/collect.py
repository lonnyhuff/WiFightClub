import os
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path
import re

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def get_wifi_signal():
    try:
        output = subprocess.check_output([
            "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport",
            "-I"
        ], text=True)

        wifi_info = {}
        for line in output.strip().split("\n"):
            if ":" in line:
                key, val = line.strip().split(":", 1)
                wifi_info[key.strip()] = val.strip()

        rssi = int(wifi_info.get("agrCtlRSSI", -999))
        return rssi
    except Exception as e:
        print(f"⚠️ Failed to get WiFi signal: {e}")
        return None

def parse_ping_summary(ping_output):
    try:
        packet_loss = re.search(r"(\d+(?:\.\d+)?)% packet loss", ping_output)
        latency = re.search(r"round-trip .* = [\d.]+/([\d.]+)/[\d.]+/[\d.]+ ms", ping_output)

        return {
            "packet_loss_percent": float(packet_loss.group(1)) if packet_loss else None,
            "avg_latency_ms": float(latency.group(1)) if latency else None
        }
    except Exception as e:
        print(f"⚠️ Failed to parse ping output: {e}")
        return {
            "packet_loss_percent": None,
            "avg_latency_ms": None
        }

def get_ping_stats():
    try:
        output = subprocess.check_output(["ping", "-c", "100", "-i", "0.1", "8.8.8.8"], text=True)
        return parse_ping_summary(output)
    except Exception as e:
        print(f"⚠️ Ping command failed: {e}")
        return {
            "packet_loss_percent": None,
            "avg_latency_ms": None
        }

def get_disconnect_events(minutes=10):
    try:
        time_since = (datetime.now() - timedelta(minutes=minutes)).isoformat()
        output = subprocess.check_output([
            "log", "show", "--style", "syslog",
            "--predicate", 'eventMessage CONTAINS "en0" OR eventMessage CONTAINS "WiFi"',
            "--start", time_since
        ], text=True)
        disconnect_lines = [line for line in output.splitlines()
                            if re.search(r"disconnect|link down|disassoc", line, re.IGNORECASE)]
        return disconnect_lines
    except Exception as e:
        return [{"error": "log command failed (permissions or SIP)", "details": str(e)}]

def collect_data():
    return {
        "timestamp": datetime.now().isoformat(),
        "wifi_signal": get_wifi_signal(),
        "ping_stats": get_ping_stats(),
        "disconnect_events": get_disconnect_events()
    }

def main():
    data = collect_data()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = DATA_DIR / f"log_{timestamp}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Collected data saved to {path}")

if __name__ == "__main__":
    main()
