import os
import json
import pandas as pd
import plotly.express as px
from datetime import datetime

DATA_DIR = "data"
DOCS_DIR = "docs"

def load_logs():
    logs = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            path = os.path.join(DATA_DIR, filename)
            with open(path, "r") as f:
                try:
                    logs.append(json.load(f))
                except json.JSONDecodeError:
                    print(f"⚠️ Skipping invalid JSON: {filename}")
    return logs

def build_dataframe(logs):
    rows = []
    for log in logs:
        if 'timestamp' in log and 'wifi_signal' in log and 'ping_stats' in log:
            rows.append({
                'timestamp': log['timestamp'],
                'rssi': log['wifi_signal'],
                'packet_loss_percent': log['ping_stats'].get('packet_loss_percent'),
                'avg_latency_ms': log['ping_stats'].get('avg_latency_ms'),
            })
    df = pd.DataFrame(rows)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df.sort_values(by="timestamp")

def make_plot(df, y, title, y_label, filename):
    fig = px.line(df, x='timestamp', y=y, title=title)
    fig.update_layout(
        xaxis_title='Time',
        yaxis_title=y_label,
        template='plotly_white'
    )
    path = os.path.join(DOCS_DIR, filename)
    fig.write_html(path)
    print(f"✅ Plot written to {path}")

def main():
    logs = load_logs()
    if not logs:
        print("🚫 No diagnostics_log.json found.")
        return

    df = build_dataframe(logs)

    make_plot(df, 'rssi', 'WiFi Signal Strength Over Time', 'RSSI', 'rssi_plot.html')
    make_plot(df, 'packet_loss_percent', 'Packet Loss % Over Time', 'packet_loss_percent', 'packet_loss_plot.html')
    make_plot(df, 'avg_latency_ms', 'Ping Latency Over Time', 'Average Latency (ms)', 'latency_plot.html')

    print("📉 All plots updated.")

if __name__ == "__main__":
    main()
