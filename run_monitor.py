#!/usr/bin/env python3
import os
import time
import shutil
import datetime
import subprocess
from pathlib import Path
from dotenv import load_dotenv

from collector import collect

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
    """Collect diagnostics using the collector module and save them."""
    # ensure we're in repo base so collector writes to the correct folder
    os.chdir(BASE)

    data = collect.collect_data()
    collect.save_log(data)
    print(f"✅ Collected diagnostics at {data['timestamp']}")

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
