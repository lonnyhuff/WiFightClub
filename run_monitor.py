#!/usr/bin/env python3
import os
import time
import shutil
import json
import datetime
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Set up paths
BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
ARCHIVE_DIR = BASE / "archive"
DOCS_DIR = BASE / "docs"

# Load .env config
load_dotenv(BASE / ".env")
GITHUB_PAT = os.getenv("GITHUB_PAT")
REPO_URL = os.getenv("REPO_URL")

# Settings
INTERVAL = 300  # in seconds (5 mins)
RETENTION_DAYS = 7

def collect_diagnostics():
    timestamp = datetime.datetime.utcnow().isoformat()
    try:
        airport_cmd = ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"]
        wifi_raw = subprocess.check_output(airport_cmd, text=True)
        wifi = {}
        for line in wifi_raw.strip().split("\n"):
            if ":" in line:
                key, val = line.strip().split(":", 1)
                wifi[key.strip()] = val.strip()
    except Exception as e:
        wifi = {"error": str(e)}

    try:
        ping_raw = subprocess.check_output(["ping", "-c", "100", "-i", "0.1", "8.8.8.8"], text=True)
    except Exception as e:
        ping_raw = f"Ping failed: {e}"

    diag = {
        "timestamp": timestamp,
        "wifi_info": wifi,
        "ping_summary": ping_raw
    }

    DATA_DIR.mkdir(exist_ok=True)
    file_path = DATA_DIR / f"{timestamp.replace(':', '-')}.json"
    with open(file_path, "w") as f:
        json.dump(diag, f, indent=2)

    print(f"✅ Collected diagnostics at {timestamp}")

def archive_old_logs():
    now = datetime.datetime.utcnow()
    cutoff = now - datetime.timedelta(days=RETENTION_DAYS)
    ARCHIVE_DIR.mkdir(exist_ok=True)

    for file in DATA_DIR.glob("*.json"):
        try:
            ts = datetime.datetime.fromisoformat(file.stem.replace("T", "").replace("-", ":", 2))
            if ts < cutoff:
                shutil.move(str(file), ARCHIVE_DIR / file.name)
        except Exception:
            continue

def regenerate_plots():
    subprocess.run(["python3", "visualizer/plot.py"], cwd=BASE)

def push_to_github():
    subprocess.run(["python3", "push_to_github/sync.py"], cwd=BASE)

def monitor_loop():
    print("🌀 WiFightClub monitor starting...")
    while True:
        collect_diagnostics()
        archive_old_logs()
        regenerate_plots()
        push_to_github()
        print(f"🕒 Sleeping for {INTERVAL} seconds...\n")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    monitor_loop()
