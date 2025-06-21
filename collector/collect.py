#!/usr/bin/env python3
import subprocess
import json
import datetime
import time
import os
import signal
from pathlib import Path
from multiprocessing import Process
import click

DATA_DIR = Path("data")
PID_FILE = Path(".wifightclub.pid")
RETENTION_DAYS = 7

def get_wifi_info():
    try:
        result = subprocess.check_output(
            ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"],
            text=True
        )
        wifi_info = {}
        for line in result.strip().split("\n"):
            if ":" in line:
                key, val = line.strip().split(":", 1)
                wifi_info[key.strip()] = val.strip()
        return wifi_info
    except Exception as e:
        return {"error": str(e)}

def run_ping():
    try:
        result = subprocess.check_output(["ping", "-c", "100", "-i", "0.1", "8.8.8.8"], text=True)
        return result.strip()
    except Exception as e:
        return f"Ping failed: {e}"

def save_diagnostics(data):
    timestamp = data["timestamp"].replace(":", "-")
    filename = DATA_DIR / f"{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def clean_old_logs():
    now = datetime.datetime.utcnow()
    cutoff = now - datetime.timedelta(days=RETENTION_DAYS)
    for file in DATA_DIR.glob("*.json"):
        try:
            timestamp_str = file.stem
            timestamp = datetime.datetime.fromisoformat(timestamp_str.replace("T", ""))
            if timestamp < cutoff:
                file.unlink()
        except:
            continue

def collect_once():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    clean_old_logs()

    timestamp = datetime.datetime.utcnow().isoformat()
    wifi_info = get_wifi_info()
    ping_result = run_ping()

    diagnostic = {
        "timestamp": timestamp,
        "wifi_info": wifi_info,
        "ping_summary": ping_result
    }

    save_diagnostics(diagnostic)
    print(f"✅ Logged diagnostics at {timestamp}")

def run_daemon(interval):
    print(f"🌀 Starting WiFightClub collector (every {interval}s)...")
    while True:
        collect_once()
        time.sleep(interval)

def start_daemon(interval):
    if PID_FILE.exists():
        print("⚠️ Daemon already running (PID file exists).")
        return

    p = Process(target=run_daemon, args=(interval,))
    p.start()
    PID_FILE.write_text(str(p.pid))
    print(f"✅ Daemon started (PID {p.pid})")

def stop_daemon():
    if not PID_FILE.exists():
        print("❌ No running daemon found.")
        return

    pid = int(PID_FILE.read_text())
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"🛑 Stopped daemon process (PID {pid})")
    except ProcessLookupError:
        print("⚠️ Process not found. Cleaning up PID file.")
    PID_FILE.unlink()

@click.command()
@click.option('--once', is_flag=True, help='Run one-time diagnostics')
@click.option('--daemon', is_flag=True, help='Run collector in background loop')
@click.option('--stop', is_flag=True, help='Stop background collector')
@click.option('--interval', default=900, help='Interval between collections in seconds (used with --daemon)')
def cli(once, daemon, stop, interval):
    if once:
        collect_once()
    elif daemon:
        start_daemon(interval)
    elif stop:
        stop_daemon()
    else:
        click.echo("❓ Use --once, --daemon, or --stop")

if __name__ == "__main__":
    cli()
